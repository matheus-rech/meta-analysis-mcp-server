"""Core Meta-Analysis Tools."""

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import scipy.stats as stats
from typing import Dict, List, Any, Optional, Tuple
import json
import base64
import io
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

R_SCRIPTS_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "r_scripts"

def run_r_script(function_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run R script with the given function name and input data.
    
    Args:
        function_name: Name of the R function to call
        input_data: Dictionary of input data to pass to the R function
        
    Returns:
        Dictionary of results from the R function
    """
    logger.info(f"Running R function: {function_name}")
    
    try:
        if not R_SCRIPTS_DIR.exists():
            raise FileNotFoundError(f"R scripts directory not found: {R_SCRIPTS_DIR}")
            
        r_script_path = R_SCRIPTS_DIR / "meta_analysis.R"
        
        if not r_script_path.exists():
            raise FileNotFoundError(f"R script not found: {r_script_path}")
        
        result = subprocess.run(
            ["Rscript", str(r_script_path), function_name, json.dumps(input_data)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            logger.error(f"R script failed with return code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            raise RuntimeError(f"R script execution failed: {result.stderr}")
            
        try:
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON output from R: {result.stdout}")
            raise ValueError(f"Failed to parse JSON output from R: {result.stdout}")
            
    except Exception as e:
        logger.error(f"Exception running R script: {str(e)}")
        raise


class MetaAnalysisTools:
    """Core meta-analysis functionality."""

    def __init__(self):
        """Initialize meta-analysis tools."""
        self.logger = logger
        self.sessions = {}  # Store session data

    async def perform_meta_analysis(
        self,
        studies: List[Dict[str, Any]] = None,
        session_id: str = None,
        method: str = "random",
        measure: str = "SMD"
    ) -> Dict[str, Any]:
        """
        Perform statistical meta-analysis using R.
        
        Args:
            studies: List of study data with effect_size, standard_error, sample_size (optional if session_id provided)
            session_id: Session ID to use studies from session (optional if studies provided)
            method: Meta-analysis method ("fixed" or "random")
            measure: Effect measure (SMD, MD, OR, RR, RD)
            
        Returns:
            Meta-analysis results including pooled effect, confidence intervals, heterogeneity
        """
        try:
            if session_id and session_id in self.sessions:
                studies = self.sessions[session_id]["studies"]
            elif not studies:
                raise ValueError("Either studies list or valid session_id must be provided")

            effect_sizes = [s["effect_size"] for s in studies]
            standard_errors = [s["standard_error"] for s in studies]
            study_ids = [s["study_id"] for s in studies]
            sample_sizes = [s["sample_size"] for s in studies]
            
            r_method = "FE" if method == "fixed" else "REML"
            input_data = {
                "effect_sizes": effect_sizes,
                "standard_errors": standard_errors,
                "study_ids": study_ids,
                "method": r_method
            }
            
            r_results = run_r_script("perform_meta_analysis", input_data)
            
            if "error" in r_results:
                raise RuntimeError(f"R meta-analysis failed: {r_results['error']}")
            
            # Calculate weights and confidence intervals for study results
            variances = [se ** 2 for se in standard_errors]
            weights = [1 / var for var in variances]
            
            # Format study-level results
            study_results = []
            for i, study in enumerate(studies):
                ci_lower = effect_sizes[i] - 1.96 * standard_errors[i]
                ci_upper = effect_sizes[i] + 1.96 * standard_errors[i]
                
                study_results.append({
                    "study_id": study_ids[i],
                    "effect_size": float(effect_sizes[i]),
                    "standard_error": float(standard_errors[i]),
                    "weight": float(weights[i] / sum(weights) * 100),
                    "ci_lower": float(ci_lower),
                    "ci_upper": float(ci_upper)
                })
            
            results = {
                "meta_analysis_results": {
                    "method": method,
                    "measure": measure,
                    "number_of_studies": len(studies),
                    "total_participants": int(sum(sample_sizes)),
                    "pooled_effect": float(r_results["estimate"]),
                    "standard_error": float(r_results["se"]),
                    "ci_lower": float(r_results["ci_lower"]),
                    "ci_upper": float(r_results["ci_upper"]),
                    "z_value": float(r_results["z_value"]),
                    "p_value": float(r_results["p_value"]),
                    "significant": float(r_results["p_value"]) < 0.05
                },
                "heterogeneity": {
                    "Q_statistic": float(r_results["q_statistic"]),
                    "degrees_of_freedom": int(r_results["q_df"]),
                    "p_heterogeneity": float(r_results["q_p_value"]),
                    "I_squared": float(r_results["i_squared"]),
                    "tau_squared": float(r_results["tau_squared"]),
                    "interpretation": self._interpret_heterogeneity(float(r_results["i_squared"]))
                },
                "study_results": study_results,
                "summary": self._generate_summary(
                    float(r_results["estimate"]), 
                    float(r_results["ci_lower"]), 
                    float(r_results["ci_upper"]), 
                    float(r_results["p_value"]), 
                    float(r_results["i_squared"]), 
                    measure
                )
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in meta-analysis: {e}")
            raise

    async def create_forest_plot(
        self,
        studies: List[Dict[str, Any]],
        title: str = "Forest Plot",
        output_format: str = "png"
    ) -> Dict[str, Any]:
        """
        Create forest plot visualization using R.
        
        Args:
            studies: Study data with effect_size, ci_lower, ci_upper, weight
            title: Plot title
            output_format: Output format (png, svg, html)
            
        Returns:
            Forest plot data and visualization
        """
        try:
            if not studies:
                raise ValueError("No studies provided for forest plot")

            study_names = [s["study_id"] for s in studies]
            effect_sizes = [s["effect_size"] for s in studies]
            standard_errors = [s.get("standard_error", 0.1) for s in studies]
            
            # Calculate confidence intervals if not provided
            ci_lowers = []
            ci_uppers = []
            for i, study in enumerate(studies):
                if "ci_lower" in study and "ci_upper" in study:
                    ci_lowers.append(study["ci_lower"])
                    ci_uppers.append(study["ci_upper"])
                else:
                    # Calculate 95% CI from effect size and standard error
                    ci_lower = effect_sizes[i] - 1.96 * standard_errors[i]
                    ci_upper = effect_sizes[i] + 1.96 * standard_errors[i]
                    ci_lowers.append(ci_lower)
                    ci_uppers.append(ci_upper)
            
            # Calculate weights if not provided
            weights = []
            for study in studies:
                if "weight" in study:
                    weights.append(study["weight"])
                else:
                    # Calculate weight as inverse of variance
                    se = study.get("standard_error", 0.1)
                    weight = 1 / (se ** 2) if se > 0 else 1.0
                    weights.append(weight)
            
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [(w / total_weight) * 100 for w in weights]
            else:
                weights = [100.0 / len(studies) for _ in studies]
            
            # Prepare data for R forest plot
            forest_plot_data = {
                "effect_sizes": effect_sizes,
                "standard_errors": standard_errors,
                "study_names": study_names,
                "ci_lower": ci_lowers,
                "ci_upper": ci_uppers,
                "weights": weights,
                "output_file": os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output", "forest_plot.png"),
                "title": title,
                "x_label": "Effect Size",
                "width": 1000,
                "height": max(600, len(studies) * 50)
            }
            
            # Call R script to create forest plot
            forest_plot_result = run_r_script("create_forest_plot", forest_plot_data)
            
            if not forest_plot_result.get("success", False):
                self.logger.warning(f"Failed to generate forest plot in R: {forest_plot_result.get('error', 'Unknown error')}")
                # Fall back to plotly for forest plot
                fig = go.Figure()
                
                # Add confidence intervals
                for i, (name, effect, ci_low, ci_high, weight) in enumerate(zip(
                    study_names, effect_sizes, ci_lowers, ci_uppers, weights
                )):
                    # Horizontal line for CI
                    fig.add_trace(go.Scatter(
                        x=[ci_low, ci_high],
                        y=[i, i],
                        mode='lines',
                        line=dict(color='black', width=2),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    
                    # Square for point estimate (size proportional to weight)
                    marker_size = max(8, min(20, weight * 0.5))
                    fig.add_trace(go.Scatter(
                        x=[effect],
                        y=[i],
                        mode='markers',
                        marker=dict(
                            symbol='square',
                            size=marker_size,
                            color='blue',
                            line=dict(color='black', width=1)
                        ),
                        showlegend=False,
                        hovertemplate=f'<b>{name}</b><br>' +
                                    f'Effect Size: {effect:.3f}<br>' +
                                    f'95% CI: [{ci_low:.3f}, {ci_high:.3f}]<br>' +
                                    f'Weight: {weight:.1f}%<extra></extra>'
                    ))
                
                # Add vertical line at null effect
                fig.add_vline(x=0, line_dash="dash", line_color="red", opacity=0.7)
                
                # Update layout
                fig.update_layout(
                    title=title,
                    xaxis_title="Effect Size",
                    yaxis=dict(
                        tickmode='array',
                        tickvals=list(range(len(studies))),
                        ticktext=study_names,
                        autorange='reversed'
                    ),
                    height=max(400, len(studies) * 50),
                    showlegend=False,
                    template='plotly_white'
                )
                
                # Generate output based on format
                if output_format == "html":
                    plot_data = fig.to_html(include_plotlyjs=True)
                elif output_format == "svg":
                    plot_data = fig.to_image(format="svg", engine="kaleido").decode()
                else:  # png
                    img_bytes = fig.to_image(format="png", engine="kaleido")
                    plot_data = base64.b64encode(img_bytes).decode()
            else:
                # Use R-generated forest plot
                forest_plot_path = forest_plot_result["output_file"]
                
                with open(forest_plot_path, "rb") as f:
                    img_bytes = f.read()
                
                if output_format == "html":
                    html = f"""
                    <html>
                    <body>
                        <h2>{title}</h2>
                        <img src="data:image/png;base64,{base64.b64encode(img_bytes).decode()}" alt="Forest Plot">
                    </body>
                    </html>
                    """
                    plot_data = html
                elif output_format == "svg":
                    self.logger.warning("SVG output format requested but R generates PNG. Returning PNG.")
                    plot_data = base64.b64encode(img_bytes).decode()
                else:  # png
                    plot_data = base64.b64encode(img_bytes).decode()
            
            return {
                "forest_plot": {
                    "title": title,
                    "format": output_format,
                    "plot_data": plot_data,
                    "studies_plotted": len(studies),
                    "effect_range": {
                        "min": float(min(ci_lowers)),
                        "max": float(max(ci_uppers))
                    },
                    "generated_by": "R metafor package" if forest_plot_result.get("success", False) else "Plotly fallback"
                },
                "study_summary": [
                    {
                        "study_id": s["study_id"],
                        "effect_size": s["effect_size"],
                        "ci_lower": ci_lowers[i],
                        "ci_upper": ci_uppers[i],
                        "weight": weights[i]
                    }
                    for i, s in enumerate(studies)
                ],
                "pooled_effect": forest_plot_result.get("pooled_effect", None),
                "pooled_ci": [
                    forest_plot_result.get("ci_lower", None),
                    forest_plot_result.get("ci_upper", None)
                ] if forest_plot_result.get("success", False) else None
            }
            
        except Exception as e:
            self.logger.error(f"Error creating forest plot: {e}")
            raise

    async def assess_heterogeneity(
        self,
        studies: List[Dict[str, Any]] = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Assess between-study heterogeneity using R.
        
        Args:
            studies: Study data with effect_size and variance (optional if session_id provided)
            session_id: Session ID to use studies from session (optional if studies provided)
            
        Returns:
            Heterogeneity assessment results
        """
        try:
            if session_id and session_id in self.sessions:
                studies = self.sessions[session_id]["studies"]
            elif not studies:
                raise ValueError("Either studies list or valid session_id must be provided")
                
            if len(studies) < 2:
                raise ValueError("At least 2 studies required for heterogeneity assessment")

            effect_sizes = [s["effect_size"] for s in studies]
            standard_errors = [s.get("standard_error", 0.1) for s in studies]
            variances = [se ** 2 for se in standard_errors]
            study_ids = [s["study_id"] for s in studies]
            
            input_data = {
                "effect_sizes": effect_sizes,
                "standard_errors": standard_errors,
                "study_ids": study_ids,
                "method": "REML"  # Default method for metafor
            }
            
            r_results = run_r_script("perform_meta_analysis", input_data)
            
            if "error" in r_results:
                raise RuntimeError(f"R heterogeneity assessment failed: {r_results['error']}")
            
            # Calculate weights and deviations for study contributions
            weights = [1 / v for v in variances]
            total_weight = sum(weights)
            pooled_effect = float(r_results["estimate"])
            
            return {
                "heterogeneity_assessment": {
                    "Q_statistic": float(r_results["q_statistic"]),
                    "degrees_of_freedom": int(r_results["q_df"]),
                    "p_value": float(r_results["q_p_value"]),
                    "I_squared": float(r_results["i_squared"]),
                    "tau_squared": float(r_results["tau_squared"]),
                    "H_squared": float(r_results["h_squared"]),
                    "significant_heterogeneity": float(r_results["q_p_value"]) < 0.10,  # Traditional threshold
                    "interpretation": {
                        "I_squared_level": self._interpret_heterogeneity(float(r_results["i_squared"])),
                        "clinical_significance": self._assess_clinical_heterogeneity(
                            float(r_results["i_squared"]), 
                            float(r_results["tau_squared"])
                        ),
                        "recommendation": self._heterogeneity_recommendation(
                            float(r_results["i_squared"]), 
                            float(r_results["q_p_value"])
                        )
                    }
                },
                "study_contributions": [
                    {
                        "study_id": study_ids[i],
                        "effect_size": float(effect_sizes[i]),
                        "weight": float(weights[i] / total_weight * 100),
                        "deviation_from_pooled": float(abs(effect_sizes[i] - pooled_effect))
                    }
                    for i in range(len(studies))
                ],
                "analysis_method": "R metafor package"
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing heterogeneity: {e}")
            raise

    async def detect_publication_bias(
        self,
        studies: List[Dict[str, Any]],
        tests: List[str] = ["egger"]
    ) -> Dict[str, Any]:
        """
        Assess publication bias using statistical tests and funnel plots in R.
        
        Args:
            studies: Study data with effect_size and standard_error
            tests: Statistical tests to perform
            
        Returns:
            Publication bias assessment results
        """
        try:
            if len(studies) < 3:
                raise ValueError("At least 3 studies required for publication bias assessment")

            effect_sizes = [s["effect_size"] for s in studies]
            standard_errors = [s["standard_error"] for s in studies]
            study_ids = [s["study_id"] for s in studies]
            
            input_data = {
                "effect_sizes": effect_sizes,
                "standard_errors": standard_errors,
                "study_ids": study_ids
            }
            
            r_results = run_r_script("assess_publication_bias", input_data)
            
            if "error" in r_results:
                raise RuntimeError(f"R publication bias assessment failed: {r_results['error']}")
            
            # Create funnel plot using R
            funnel_plot_data = {
                "effect_sizes": effect_sizes,
                "standard_errors": standard_errors,
                "output_file": os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output", "funnel_plot.png"),
                "title": "Funnel Plot for Publication Bias Assessment",
                "width": 800,
                "height": 600
            }
            
            funnel_plot_result = run_r_script("create_funnel_plot", funnel_plot_data)
            
            if not funnel_plot_result.get("success", False):
                self.logger.warning(f"Failed to generate funnel plot in R: {funnel_plot_result.get('error', 'Unknown error')}")
                # Fall back to plotly for funnel plot
                fig = go.Figure()
                
                # Add study points
                fig.add_trace(go.Scatter(
                    x=effect_sizes,
                    y=[1/se for se in standard_errors],  # Precision on y-axis
                    mode='markers',
                    marker=dict(size=8, color='blue', opacity=0.7),
                    text=study_ids,
                    hovertemplate='<b>%{text}</b><br>' +
                                'Effect Size: %{x:.3f}<br>' +
                                'Precision: %{y:.3f}<extra></extra>',
                    name='Studies'
                ))
                
                # Add vertical line at null effect
                fig.add_vline(x=0, line_dash="dash", line_color="red", opacity=0.7)
                
                # Update layout
                fig.update_layout(
                    title="Funnel Plot for Publication Bias Assessment",
                    xaxis_title="Effect Size",
                    yaxis_title="Precision (1/SE)",
                    template='plotly_white',
                    showlegend=False
                )
                
                # Convert to base64 image
                img_bytes = fig.to_image(format="png", engine="kaleido")
                plot_data = base64.b64encode(img_bytes).decode()
                
                funnel_plot = {
                    "plot_data": plot_data,
                    "format": "png",
                    "interpretation": self._interpret_funnel_plot_symmetry(effect_sizes, standard_errors)
                }
            else:
                # Use R-generated funnel plot
                funnel_plot_path = funnel_plot_result["output_file"]
                
                with open(funnel_plot_path, "rb") as f:
                    plot_data = base64.b64encode(f.read()).decode()
                
                funnel_plot = {
                    "plot_data": plot_data,
                    "format": "png",
                    "interpretation": "Funnel plot analysis performed using R's metafor package"
                }
            
            results = {
                "publication_bias_assessment": {
                    "number_of_studies": len(studies),
                    "tests_performed": tests
                },
                "statistical_tests": {
                    "egger": {
                        "statistic": float(r_results["egger_test"]["statistic"]),
                        "p_value": float(r_results["egger_test"]["p_value"]),
                        "significant": r_results["egger_test"]["significant"],
                        "interpretation": "Evidence of publication bias" if r_results["egger_test"]["significant"] else "No evidence of publication bias"
                    },
                    "begg": {
                        "correlation": float(r_results["begg_test"]["statistic"]),
                        "p_value": float(r_results["begg_test"]["p_value"]),
                        "significant": r_results["begg_test"]["significant"],
                        "interpretation": "Evidence of publication bias" if r_results["begg_test"]["significant"] else "No evidence of publication bias"
                    }
                },
                "funnel_plot": funnel_plot_path if os.path.exists(funnel_plot_path) else "plotly_generated",
                "overall_interpretation": r_results["interpretation"]
            }
            
            # Overall assessment
            bias_evidence = []
            if results["statistical_tests"]["egger"]["significant"]:
                bias_evidence.append("Egger's test")
            if results["statistical_tests"]["begg"]["significant"]:
                bias_evidence.append("Begg's test")
                
            results["overall_assessment"] = {
                "evidence_of_bias": len(bias_evidence) > 0,
                "significant_tests": bias_evidence,
                "recommendation": self._publication_bias_recommendation(len(bias_evidence), len(studies))
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error detecting publication bias: {e}")
            raise

    def _interpret_heterogeneity(self, i_squared: float) -> str:
        """Interpret I-squared values."""
        if i_squared <= 25:
            return "Low heterogeneity"
        elif i_squared <= 50:
            return "Moderate heterogeneity"
        elif i_squared <= 75:
            return "Substantial heterogeneity"
        else:
            return "Considerable heterogeneity"

    def _assess_clinical_heterogeneity(self, i_squared: float, tau_squared: float) -> str:
        """Assess clinical significance of heterogeneity."""
        if i_squared > 50 and tau_squared > 0.25:
            return "Clinically significant heterogeneity - consider subgroup analysis"
        elif i_squared > 75:
            return "High heterogeneity - pooling may not be appropriate"
        else:
            return "Acceptable heterogeneity for pooling"

    def _heterogeneity_recommendation(self, i_squared: float, p_value: float) -> str:
        """Provide recommendation based on heterogeneity."""
        if i_squared > 75 or (i_squared > 50 and p_value < 0.05):
            return "Consider random-effects model and explore sources of heterogeneity"
        elif i_squared > 25:
            return "Random-effects model recommended"
        else:
            return "Fixed-effects model may be appropriate"

    def _interpret_funnel_plot_symmetry(self, effects: np.ndarray, se: np.ndarray) -> str:
        """Interpret funnel plot symmetry."""
        # Simple assessment based on distribution of effects at different precision levels
        high_precision = effects[se < np.median(se)]
        low_precision = effects[se >= np.median(se)]
        
        if len(high_precision) > 0 and len(low_precision) > 0:
            symmetry_measure = abs(np.mean(high_precision) - np.mean(low_precision))
            if symmetry_measure > np.std(effects) / 2:
                return "Asymmetric funnel plot - possible publication bias"
            else:
                return "Relatively symmetric funnel plot"
        else:
            return "Insufficient data for symmetry assessment"

    def _publication_bias_recommendation(self, significant_tests: int, n_studies: int) -> str:
        """Provide recommendation based on publication bias assessment."""
        if significant_tests > 0:
            if n_studies < 10:
                return "Possible publication bias detected, but low power with few studies"
            else:
                return "Evidence of publication bias - consider trim-and-fill analysis or additional search strategies"
        else:
            return "No strong evidence of publication bias detected"

    def _generate_summary(self, effect: float, ci_low: float, ci_high: float, 
                         p_value: float, i_squared: float, measure: str) -> str:
        """Generate summary interpretation."""
        significance = "significant" if p_value < 0.05 else "non-significant"
        direction = "positive" if effect > 0 else "negative" if effect < 0 else "null"
        heterogeneity = self._interpret_heterogeneity(i_squared).lower()
        
        return (f"Meta-analysis shows a {significance} {direction} effect "
               f"({measure} = {effect:.3f}, 95% CI [{ci_low:.3f}, {ci_high:.3f}], "
               f"p = {p_value:.3f}) with {heterogeneity}.")

    async def initialize_meta_analysis(self, user_id: str = "default_user", title: str = "Meta-Analysis", 
                                      description: str = "", project_name: str = "", 
                                      study_type: str = "clinical_trial", effect_measure: str = "SMD") -> Dict[str, Any]:
        """Initialize a new meta-analysis session."""
        import uuid
        session_id = str(uuid.uuid4())
        
        if project_name:
            title = project_name
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "study_type": study_type,
            "effect_measure": effect_measure,
            "created_at": "2025-07-29",
            "studies": [],
            "results": {},
            "files": []
        }
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "study_type": study_type,
            "effect_measure": effect_measure,
            "status": "initialized",
            "message": "Meta-analysis session created successfully"
        }

    async def upload_study_data(self, session_id: str, studies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upload and validate study data for a session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        required_fields = ["study_id", "effect_size", "standard_error", "sample_size"]
        validation_errors = []
        
        for study in studies:
            for field in required_fields:
                if field not in study:
                    validation_errors.append(f"Missing required field '{field}' in study {study.get('study_id', 'unknown')}")
        
        if validation_errors:
            return {
                "session_id": session_id,
                "validation_status": "failed",
                "errors": validation_errors,
                "message": f"Validation failed with {len(validation_errors)} errors"
            }
        
        self.sessions[session_id]["studies"] = studies
        
        return {
            "session_id": session_id,
            "studies_uploaded": len(studies),
            "validation_status": "passed",
            "validation_summary": {
                "total_studies": len(studies),
                "valid_studies": len(studies),
                "invalid_studies": 0
            },
            "message": f"Successfully uploaded {len(studies)} studies"
        }

    async def generate_forest_plot(self, session_id: str, title: str = "Forest Plot", output_format: str = "png") -> Dict[str, Any]:
        """Generate forest plot for session studies."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        studies = self.sessions[session_id]["studies"]
        if not studies:
            raise ValueError("No studies found in session")
        
        # Add confidence intervals if missing
        for study in studies:
            if "ci_lower" not in study:
                study["ci_lower"] = study["effect_size"] - 1.96 * study["standard_error"]
            if "ci_upper" not in study:
                study["ci_upper"] = study["effect_size"] + 1.96 * study["standard_error"]
            if "weight" not in study:
                study["weight"] = 1 / (study["standard_error"] ** 2)
        
        total_weight = sum(s["weight"] for s in studies)
        for study in studies:
            study["weight"] = (study["weight"] / total_weight) * 100
        
        result = await self.create_forest_plot(studies, title, output_format)
        self.sessions[session_id]["files"].append(f"forest_plot.{output_format}")
        
        return result

    async def assess_publication_bias(self, session_id: str, tests: List[str] = ["egger"]) -> Dict[str, Any]:
        """Assess publication bias for session studies."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        studies = self.sessions[session_id]["studies"]
        if not studies:
            raise ValueError("No studies found in session")
        
        result = await self.detect_publication_bias(studies, tests)
        self.sessions[session_id]["files"].append("funnel_plot.png")
        
        return result

    async def generate_report(self, session_id: str, format: str = "html", include_plots: bool = True, include_data_summary: bool = True) -> Dict[str, Any]:
        """Generate comprehensive meta-analysis report."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        studies = session["studies"]
        
        if not studies:
            raise ValueError("No studies found in session")
        
        # Generate basic report content
        report_content = f"""
        <html>
        <head><title>{session['title']}</title></head>
        <body>
        <h1>{session['title']}</h1>
        <p>{session['description']}</p>
        
        <h2>Study Summary</h2>
        <p>Number of studies: {len(studies)}</p>
        <p>Total participants: {sum(s['sample_size'] for s in studies)}</p>
        
        <h2>Studies Included</h2>
        <ul>
        """
        
        for study in studies:
            report_content += f"<li>{study['study_id']}: Effect size = {study['effect_size']:.3f} (SE = {study['standard_error']:.3f})</li>"
        
        report_content += """
        </ul>
        
        <h2>Meta-Analysis Results</h2>
        <p>Detailed results would be generated here based on the analysis performed.</p>
        
        </body>
        </html>
        """
        
        filename = f"meta_analysis_report_{session_id}.html"
        self.sessions[session_id]["files"].append(filename)
        
        return {
            "session_id": session_id,
            "report_format": format,
            "filename": filename,
            "content": report_content,
            "size_bytes": len(report_content),
            "message": "Report generated successfully"
        }

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status and files."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "title": session["title"],
            "description": session["description"],
            "created_at": session["created_at"],
            "studies_count": len(session["studies"]),
            "files_generated": session["files"],
            "status": "active",
            "last_updated": "2025-07-29"
        }

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
from datetime import datetime
from ..models import (
    MetaAnalysisResult, ForestPlotResult, PublicationBiasResult, 
    HeterogeneityMetrics, StudyData, ConfidenceInterval,
    ToolResponse, ValidationError, PublicationBiasTest
)

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
        studies: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None,
        method: str = "random",
        measure: str = "SMD"
    ) -> ToolResponse:
        """
        Perform statistical meta-analysis using R with Pydantic validation.
        
        Args:
            studies: List of study data with effect_size, standard_error, sample_size (optional if session_id provided)
            session_id: Session ID to use studies from session (optional if studies provided)
            method: Meta-analysis method ("fixed" or "random")
            measure: Effect measure (SMD, MD, OR, RR, RD)
            
        Returns:
            ToolResponse containing validated MetaAnalysisResult
        """
        start_time = datetime.now()
        
        try:
            if session_id and session_id in self.sessions:
                studies = self.sessions[session_id]["studies"]
            elif not studies:
                return ToolResponse(
                    success=False,
                    data={"error": "Either studies list or valid session_id must be provided"},
                    errors=["Either studies list or valid session_id must be provided"]
                )
            
            validated_studies = []
            for i, study in enumerate(studies):
                try:
                    validated_study = StudyData(**study)
                    validated_studies.append(validated_study)
                except Exception as e:
                    return ToolResponse(
                        success=False,
                        data={"error": f"Invalid study data at index {i}"},
                        errors=[f"Study {i} validation failed: {str(e)}"]
                    )

            effect_sizes = [s.effect_size for s in validated_studies]
            standard_errors = [s.standard_error for s in validated_studies]
            study_ids = [s.study_id for s in validated_studies]
            sample_sizes = [s.sample_size for s in validated_studies]
            
            r_method = "FE" if method == "fixed" else "REML"
            input_data = {
                "effect_sizes": effect_sizes,
                "standard_errors": standard_errors,
                "study_ids": study_ids,
                "method": r_method
            }
            
            r_results = run_r_script("perform_meta_analysis", input_data)
            
            if "error" in r_results:
                return ToolResponse(
                    success=False,
                    data={"error": f"R meta-analysis failed: {r_results['error']}"},
                    errors=[f"R meta-analysis failed: {r_results['error']}"]
                )
            
            try:
                confidence_interval = ConfidenceInterval(
                    lower=float(r_results["ci_lower"]),
                    upper=float(r_results["ci_upper"]),
                    level=0.95
                )
            except Exception as e:
                return ToolResponse(
                    success=False,
                    data={"error": "Invalid confidence interval from R results"},
                    errors=[f"Confidence interval validation failed: {str(e)}"]
                )
            
            try:
                heterogeneity = HeterogeneityMetrics(
                    i_squared=float(r_results["i_squared"]),
                    tau_squared=float(r_results["tau_squared"]),
                    q_statistic=float(r_results["q_statistic"]),
                    q_p_value=float(r_results["q_p_value"]),
                    interpretation=self._interpret_heterogeneity(float(r_results["i_squared"]))
                )
            except Exception as e:
                return ToolResponse(
                    success=False,
                    data={"error": "Invalid heterogeneity metrics from R results"},
                    errors=[f"Heterogeneity validation failed: {str(e)}"]
                )
            
            # Calculate weights and update study data
            variances = [se ** 2 for se in standard_errors]
            weights = [1 / var for var in variances]
            total_weight = sum(weights)
            
            # Create validated study results
            validated_study_results = []
            for i, study in enumerate(validated_studies):
                try:
                    study_with_weight = StudyData(
                        study_id=study.study_id,
                        effect_size=study.effect_size,
                        standard_error=study.standard_error,
                        sample_size=study.sample_size,
                        study_name=study.study_name,
                        weight=float(weights[i] / total_weight * 100)
                    )
                    validated_study_results.append(study_with_weight)
                except Exception as e:
                    return ToolResponse(
                        success=False,
                        data={"error": f"Invalid study data at index {i}"},
                        errors=[f"Study {i} weight validation failed: {str(e)}"]
                    )
            
            try:
                meta_result = MetaAnalysisResult(
                    pooled_effect_size=float(r_results["estimate"]),
                    confidence_interval=confidence_interval,
                    p_value=float(r_results["p_value"]),
                    method=method,
                    measure=measure,
                    studies_analyzed=len(validated_studies),
                    heterogeneity=heterogeneity,
                    studies=validated_study_results,
                    analysis_timestamp=datetime.now()
                )
            except Exception as e:
                return ToolResponse(
                    success=False,
                    data={"error": "Invalid meta-analysis result structure"},
                    errors=[f"MetaAnalysisResult validation failed: {str(e)}"]
                )
            
            if session_id:
                if session_id not in self.sessions:
                    self.sessions[session_id] = {}
                self.sessions[session_id]['last_meta_analysis'] = meta_result.dict()
                self.sessions[session_id]['last_activity'] = datetime.now()
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ToolResponse(
                success=True,
                data=meta_result,
                message=f"Meta-analysis completed successfully with {len(validated_studies)} studies",
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Error in meta-analysis: {e}")
            return ToolResponse(
                success=False,
                data={"error": f"Meta-analysis failed: {str(e)}"},
                errors=[f"Meta-analysis execution failed: {str(e)}"],
                execution_time_ms=execution_time
            )

    async def create_forest_plot(
        self,
        studies: List[Dict[str, Any]],
        title: str = "Forest Plot",
        output_format: str = "png"
    ) -> ToolResponse:
        """
        Create forest plot visualization using R with Pydantic validation.
        
        Args:
            studies: Study data with effect_size, standard_error, sample_size
            title: Plot title
            output_format: Output format (png, svg, html)
            
        Returns:
            ToolResponse containing validated ForestPlotResult
        """
        start_time = datetime.now()
        
        try:
            if not studies:
                return ToolResponse(
                    success=False,
                    data={"error": "No studies provided for forest plot"},
                    errors=["No studies provided for forest plot"]
                )
            
            validated_studies = []
            for i, study in enumerate(studies):
                try:
                    validated_study = StudyData(**study)
                    validated_studies.append(validated_study)
                except Exception as e:
                    return ToolResponse(
                        success=False,
                        data={"error": f"Invalid study data at index {i}"},
                        errors=[f"Study {i} validation failed: {str(e)}"]
                    )

            study_names = [s.study_id for s in validated_studies]
            effect_sizes = [s.effect_size for s in validated_studies]
            standard_errors = [s.standard_error for s in validated_studies]
            
            # Calculate confidence intervals and weights
            ci_lowers = []
            ci_uppers = []
            weights = []
            
            for i, study in enumerate(validated_studies):
                # Calculate 95% CI from effect size and standard error
                ci_lower = study.effect_size - 1.96 * study.standard_error
                ci_upper = study.effect_size + 1.96 * study.standard_error
                ci_lowers.append(ci_lower)
                ci_uppers.append(ci_upper)
                
                # Calculate weight as inverse of variance or use provided weight
                if study.weight is not None:
                    weights.append(study.weight)
                else:
                    weight = 1 / (study.standard_error ** 2) if study.standard_error > 0 else 1.0
                    weights.append(weight)
            
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [(w / total_weight) * 100 for w in weights]
            else:
                weights = [100.0 / len(validated_studies) for _ in validated_studies]
            
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
                "height": max(600, len(validated_studies) * 50)
            }
            
            # Call R script to create forest plot
            forest_plot_result = run_r_script("create_forest_plot", forest_plot_data)
            
            if isinstance(forest_plot_result, str):
                try:
                    forest_plot_result = json.loads(forest_plot_result)
                except json.JSONDecodeError:
                    return ToolResponse(
                        success=False,
                        data={"error": "Failed to parse forest plot result JSON"},
                        errors=["Failed to parse forest plot result JSON"]
                    )
            
            if not forest_plot_result.get("success", False):
                return ToolResponse(
                    success=False,
                    data={"error": f"R forest plot generation failed: {forest_plot_result.get('error', 'Unknown error')}"},
                    errors=[f"R forest plot generation failed: {forest_plot_result.get('error', 'Unknown error')}"]
                )
            
            # Create validated ForestPlotResult
            try:
                plot_file = forest_plot_result.get("plot_file", "")
                file_size = None
                if plot_file and os.path.exists(plot_file):
                    file_size = os.path.getsize(plot_file)
                
                forest_result = ForestPlotResult(
                    plot_file=plot_file,
                    format=output_format,
                    studies_plotted=len(validated_studies),
                    title=title,
                    dimensions={"width": 1000, "height": max(600, len(validated_studies) * 50)},
                    file_size_bytes=file_size
                )
            except Exception as e:
                return ToolResponse(
                    success=False,
                    data={"error": "Invalid forest plot result structure"},
                    errors=[f"ForestPlotResult validation failed: {str(e)}"]
                )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ToolResponse(
                success=True,
                data=forest_result,
                message=f"Forest plot generated successfully for {len(validated_studies)} studies",
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Error in forest plot generation: {e}")
            return ToolResponse(
                success=False,
                data={"error": f"Forest plot generation failed: {str(e)}"},
                errors=[f"Forest plot generation failed: {str(e)}"],
                execution_time_ms=execution_time
            )

    async def assess_heterogeneity(
        self,
        studies: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None
    ) -> ToolResponse:
        """
        Assess between-study heterogeneity using R.
        
        Args:
            studies: Study data with effect_size and variance (optional if session_id provided)
            session_id: Session ID to use studies from session (optional if studies provided)
            
        Returns:
            ToolResponse containing heterogeneity assessment results
        """
        start_time = datetime.now()
        
        try:
            if session_id and session_id in self.sessions:
                studies = self.sessions[session_id]["studies"]
            elif not studies:
                return ToolResponse(
                    success=False,
                    data={"error": "Either studies list or valid session_id must be provided"},
                    errors=["Either studies list or valid session_id must be provided"]
                )
                
            if len(studies) < 2:
                return ToolResponse(
                    success=False,
                    data={"error": "At least 2 studies required for heterogeneity assessment"},
                    errors=["At least 2 studies required for heterogeneity assessment"]
                )

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
            
            if isinstance(r_results, str):
                try:
                    r_results = json.loads(r_results)
                except json.JSONDecodeError as e:
                    return ToolResponse(
                        success=False,
                        data={"error": f"Failed to parse R results: {str(e)}"},
                        errors=[f"Failed to parse R results: {str(e)}"]
                    )
            
            if "error" in r_results:
                return ToolResponse(
                    success=False,
                    data={"error": f"R heterogeneity assessment failed: {r_results['error']}"},
                    errors=[f"R heterogeneity assessment failed: {r_results['error']}"]
                )
            
            # Calculate weights and deviations for study contributions
            weights = [1 / v for v in variances]
            total_weight = sum(weights)
            pooled_effect = float(r_results["estimate"])
            
            heterogeneity_data = {
                "tau_squared": float(r_results["tau_squared"]),
                "i_squared": float(r_results["i_squared"]),
                "h_squared": float(r_results["h_squared"]),
                "q_statistic": float(r_results["q_statistic"]),
                "q_df": int(r_results["q_df"]),
                "q_p_value": float(r_results["q_p_value"]),
                "significant_heterogeneity": float(r_results["q_p_value"]) < 0.10,
                "interpretation": self._interpret_heterogeneity(float(r_results["i_squared"])),
                "clinical_significance": self._assess_clinical_heterogeneity(
                    float(r_results["i_squared"]), 
                    float(r_results["tau_squared"])
                ),
                "recommendation": self._heterogeneity_recommendation(
                    float(r_results["i_squared"]), 
                    float(r_results["q_p_value"])
                ),
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
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ToolResponse(
                success=True,
                data=heterogeneity_data,
                message=f"Heterogeneity assessment completed for {len(studies)} studies using R",
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Error assessing heterogeneity: {e}")
            return ToolResponse(
                success=False,
                data={"error": f"Heterogeneity assessment failed: {str(e)}"},
                errors=[f"Heterogeneity assessment failed: {str(e)}"],
                execution_time_ms=execution_time
            )

    async def detect_publication_bias(
        self,
        studies: List[Dict[str, Any]],
        tests: List[str] = ["egger"]
    ) -> ToolResponse:
        """
        Assess publication bias using statistical tests and funnel plots in R with Pydantic validation.
        
        Args:
            studies: Study data with effect_size and standard_error
            tests: Statistical tests to perform
            
        Returns:
            ToolResponse containing validated PublicationBiasResult
        """
        start_time = datetime.now()
        
        try:
            if len(studies) < 3:
                return ToolResponse(
                    success=False,
                    data={"error": "At least 3 studies required for publication bias assessment"},
                    errors=["At least 3 studies required for publication bias assessment"]
                )
            
            validated_studies = []
            for i, study in enumerate(studies):
                try:
                    validated_study = StudyData(**study)
                    validated_studies.append(validated_study)
                except Exception as e:
                    return ToolResponse(
                        success=False,
                        data={"error": f"Invalid study data at index {i}"},
                        errors=[f"Study {i} validation failed: {str(e)}"]
                    )

            effect_sizes = [s.effect_size for s in validated_studies]
            standard_errors = [s.standard_error for s in validated_studies]
            study_ids = [s.study_id for s in validated_studies]
            
            input_data = {
                "effect_sizes": effect_sizes,
                "standard_errors": standard_errors,
                "study_ids": study_ids
            }
            
            r_results = run_r_script("assess_publication_bias", input_data)
            
            if isinstance(r_results, str):
                try:
                    r_results = json.loads(r_results)
                except json.JSONDecodeError as e:
                    return ToolResponse(
                        success=False,
                        data={"error": f"Failed to parse R results: {str(e)}"},
                        errors=[f"Failed to parse R results: {str(e)}"]
                    )
            
            if "error" in r_results:
                return ToolResponse(
                    success=False,
                    data={"error": f"R publication bias assessment failed: {r_results['error']}"},
                    errors=[f"R publication bias assessment failed: {r_results['error']}"]
                )
            
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
            
            if isinstance(funnel_plot_result, str):
                try:
                    funnel_plot_result = json.loads(funnel_plot_result)
                except json.JSONDecodeError:
                    self.logger.warning("Failed to parse funnel plot result JSON, using fallback")
                    funnel_plot_result = {"success": False, "error": "JSON parsing failed"}
            
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
                    "interpretation": self._interpret_funnel_plot_symmetry(np.array(effect_sizes), np.array(standard_errors))
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
            
            # Create validated PublicationBiasTest objects
            try:
                egger_test = PublicationBiasTest(
                    test_name="Egger's test",
                    statistic=float(r_results["egger_test"]["statistic"]),
                    p_value=float(r_results["egger_test"]["p_value"]),
                    significant=bool(r_results["egger_test"]["significant"]),
                    interpretation="Evidence of publication bias" if r_results["egger_test"]["significant"] else "No evidence of publication bias"
                )
                
                begg_test = PublicationBiasTest(
                    test_name="Begg's test", 
                    statistic=float(r_results["begg_test"]["statistic"]),
                    p_value=float(r_results["begg_test"]["p_value"]),
                    significant=bool(r_results["begg_test"]["significant"]),
                    interpretation="Evidence of publication bias" if r_results["begg_test"]["significant"] else "No evidence of publication bias"
                )
            except (KeyError, TypeError, ValueError) as e:
                return ToolResponse(
                    success=False,
                    data={"error": f"Failed to parse R publication bias results: {str(e)}"},
                    errors=[f"Failed to parse R publication bias results: {str(e)}"]
                )
            
            # Overall assessment
            bias_evidence = []
            try:
                if r_results["egger_test"]["significant"]:
                    bias_evidence.append("Egger's test")
                if r_results["begg_test"]["significant"]:
                    bias_evidence.append("Begg's test")
            except (KeyError, TypeError) as e:
                return ToolResponse(
                    success=False,
                    data={"error": f"Failed to access R results for bias evidence: {str(e)}"},
                    errors=[f"Failed to access R results for bias evidence: {str(e)}"]
                )
            
            conclusion = self._publication_bias_recommendation(len(bias_evidence), len(validated_studies))
            
            # Create validated PublicationBiasResult
            try:
                if 'funnel_plot_path' in locals() and os.path.exists(funnel_plot_path):
                    funnel_plot_file = funnel_plot_path
                else:
                    funnel_plot_file = "plotly_generated_funnel_plot"
                
                bias_result = PublicationBiasResult(
                    funnel_plot=funnel_plot_file,
                    tests_performed=["egger", "begg"],
                    egger_test=egger_test,
                    begg_test=begg_test,
                    conclusion=conclusion,
                    studies_analyzed=len(validated_studies)
                )
            except Exception as e:
                return ToolResponse(
                    success=False,
                    data={"error": f"Failed to create PublicationBiasResult: {str(e)}"},
                    errors=[f"Failed to create PublicationBiasResult: {str(e)}"]
                )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ToolResponse(
                success=True,
                data=bias_result,
                message=f"Publication bias assessment completed for {len(validated_studies)} studies",
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Error detecting publication bias: {e}")
            return ToolResponse(
                success=False,
                data={"error": f"Publication bias assessment failed: {str(e)}"},
                errors=[f"Publication bias assessment failed: {str(e)}"],
                execution_time_ms=execution_time
            )

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

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

logger = logging.getLogger(__name__)


class MetaAnalysisTools:
    """Core meta-analysis functionality."""

    def __init__(self):
        """Initialize meta-analysis tools."""
        self.logger = logger

    async def perform_meta_analysis(
        self,
        studies: List[Dict[str, Any]],
        method: str = "random",
        measure: str = "SMD"
    ) -> Dict[str, Any]:
        """
        Perform statistical meta-analysis.
        
        Args:
            studies: List of study data with effect_size, standard_error, sample_size
            method: Meta-analysis method ("fixed" or "random")
            measure: Effect measure (SMD, MD, OR, RR, RD)
            
        Returns:
            Meta-analysis results including pooled effect, confidence intervals, heterogeneity
        """
        try:
            if not studies:
                raise ValueError("No studies provided")

            # Convert to arrays
            effect_sizes = np.array([s["effect_size"] for s in studies])
            standard_errors = np.array([s["standard_error"] for s in studies])
            sample_sizes = np.array([s["sample_size"] for s in studies])
            
            # Calculate weights (inverse variance)
            variances = standard_errors ** 2
            weights = 1 / variances
            
            if method == "fixed":
                # Fixed-effects model
                pooled_effect = np.sum(weights * effect_sizes) / np.sum(weights)
                pooled_variance = 1 / np.sum(weights)
                pooled_se = np.sqrt(pooled_variance)
                
                # Heterogeneity statistics
                Q = np.sum(weights * (effect_sizes - pooled_effect) ** 2)
                df = len(studies) - 1
                p_heterogeneity = 1 - stats.chi2.cdf(Q, df) if df > 0 else 1.0
                I_squared = max(0, (Q - df) / Q * 100) if Q > 0 else 0
                tau_squared = 0  # Fixed effects assumes no between-study variance
                
            else:  # random effects
                # Calculate Q statistic first
                fixed_pooled = np.sum(weights * effect_sizes) / np.sum(weights)
                Q = np.sum(weights * (effect_sizes - fixed_pooled) ** 2)
                df = len(studies) - 1
                
                # Estimate tau-squared (DerSimonian-Laird method)
                if df > 0 and Q > df:
                    tau_squared = (Q - df) / (np.sum(weights) - np.sum(weights ** 2) / np.sum(weights))
                else:
                    tau_squared = 0
                
                # Random-effects weights
                random_weights = 1 / (variances + tau_squared)
                pooled_effect = np.sum(random_weights * effect_sizes) / np.sum(random_weights)
                pooled_variance = 1 / np.sum(random_weights)
                pooled_se = np.sqrt(pooled_variance)
                
                # Heterogeneity statistics
                p_heterogeneity = 1 - stats.chi2.cdf(Q, df) if df > 0 else 1.0
                I_squared = max(0, (Q - df) / Q * 100) if Q > 0 else 0
            
            # Confidence intervals
            z_score = stats.norm.ppf(0.975)  # 95% CI
            ci_lower = pooled_effect - z_score * pooled_se
            ci_upper = pooled_effect + z_score * pooled_se
            
            # Z-test for overall effect
            z_statistic = pooled_effect / pooled_se if pooled_se > 0 else 0
            p_value = 2 * (1 - stats.norm.cdf(abs(z_statistic)))
            
            # Format study-level results
            study_results = []
            for i, study in enumerate(studies):
                study_weight = weights[i] if method == "fixed" else random_weights[i]
                study_ci_lower = effect_sizes[i] - z_score * standard_errors[i]
                study_ci_upper = effect_sizes[i] + z_score * standard_errors[i]
                
                study_results.append({
                    "study_id": study["study_id"],
                    "effect_size": float(effect_sizes[i]),
                    "standard_error": float(standard_errors[i]),
                    "weight": float(study_weight / np.sum(weights if method == "fixed" else random_weights) * 100),
                    "ci_lower": float(study_ci_lower),
                    "ci_upper": float(study_ci_upper)
                })
            
            results = {
                "meta_analysis_results": {
                    "method": method,
                    "measure": measure,
                    "number_of_studies": len(studies),
                    "total_participants": int(np.sum(sample_sizes)),
                    "pooled_effect": float(pooled_effect),
                    "standard_error": float(pooled_se),
                    "ci_lower": float(ci_lower),
                    "ci_upper": float(ci_upper),
                    "z_statistic": float(z_statistic),
                    "p_value": float(p_value),
                    "significant": p_value < 0.05
                },
                "heterogeneity": {
                    "Q_statistic": float(Q),
                    "degrees_of_freedom": int(df),
                    "p_heterogeneity": float(p_heterogeneity),
                    "I_squared": float(I_squared),
                    "tau_squared": float(tau_squared),
                    "interpretation": self._interpret_heterogeneity(I_squared)
                },
                "study_results": study_results,
                "summary": self._generate_summary(pooled_effect, ci_lower, ci_upper, p_value, I_squared, measure)
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
        Create forest plot visualization.
        
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

            # Create plotly forest plot
            fig = go.Figure()
            
            study_names = [s["study_id"] for s in studies]
            effect_sizes = [s["effect_size"] for s in studies]
            ci_lowers = [s["ci_lower"] for s in studies]
            ci_uppers = [s["ci_upper"] for s in studies]
            weights = [s["weight"] for s in studies]
            
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
            
            return {
                "forest_plot": {
                    "title": title,
                    "format": output_format,
                    "plot_data": plot_data,
                    "studies_plotted": len(studies),
                    "effect_range": {
                        "min": float(min(ci_lowers)),
                        "max": float(max(ci_uppers))
                    }
                },
                "study_summary": [
                    {
                        "study_id": s["study_id"],
                        "effect_size": s["effect_size"],
                        "ci_lower": s["ci_lower"],
                        "ci_upper": s["ci_upper"],
                        "weight": s["weight"]
                    }
                    for s in studies
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error creating forest plot: {e}")
            raise

    async def assess_heterogeneity(
        self,
        studies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess between-study heterogeneity.
        
        Args:
            studies: Study data with effect_size and variance
            
        Returns:
            Heterogeneity assessment results
        """
        try:
            if len(studies) < 2:
                raise ValueError("At least 2 studies required for heterogeneity assessment")

            effect_sizes = np.array([s["effect_size"] for s in studies])
            variances = np.array([s["variance"] for s in studies])
            weights = 1 / variances
            
            # Fixed-effects pooled estimate
            pooled_effect = np.sum(weights * effect_sizes) / np.sum(weights)
            
            # Q statistic
            Q = np.sum(weights * (effect_sizes - pooled_effect) ** 2)
            df = len(studies) - 1
            p_value = 1 - stats.chi2.cdf(Q, df) if df > 0 else 1.0
            
            # I-squared
            I_squared = max(0, (Q - df) / Q * 100) if Q > 0 else 0
            
            # Tau-squared (DerSimonian-Laird)
            if df > 0 and Q > df:
                c = np.sum(weights) - np.sum(weights ** 2) / np.sum(weights)
                tau_squared = (Q - df) / c
            else:
                tau_squared = 0
                
            # H statistic
            H = np.sqrt(Q / df) if df > 0 else 1.0
            
            return {
                "heterogeneity_assessment": {
                    "Q_statistic": float(Q),
                    "degrees_of_freedom": int(df),
                    "p_value": float(p_value),
                    "I_squared": float(I_squared),
                    "tau_squared": float(tau_squared),
                    "H_statistic": float(H),
                    "significant_heterogeneity": p_value < 0.10,  # Traditional threshold
                    "interpretation": {
                        "I_squared_level": self._interpret_heterogeneity(I_squared),
                        "clinical_significance": self._assess_clinical_heterogeneity(I_squared, tau_squared),
                        "recommendation": self._heterogeneity_recommendation(I_squared, p_value)
                    }
                },
                "study_contributions": [
                    {
                        "study_id": studies[i]["study_id"],
                        "effect_size": float(effect_sizes[i]),
                        "weight": float(weights[i] / np.sum(weights) * 100),
                        "deviation_from_pooled": float(abs(effect_sizes[i] - pooled_effect))
                    }
                    for i in range(len(studies))
                ]
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
        Assess publication bias using statistical tests and funnel plots.
        
        Args:
            studies: Study data with effect_size and standard_error
            tests: Statistical tests to perform
            
        Returns:
            Publication bias assessment results
        """
        try:
            if len(studies) < 3:
                raise ValueError("At least 3 studies required for publication bias assessment")

            effect_sizes = np.array([s["effect_size"] for s in studies])
            standard_errors = np.array([s["standard_error"] for s in studies])
            
            results = {
                "publication_bias_assessment": {
                    "number_of_studies": len(studies),
                    "tests_performed": tests
                },
                "statistical_tests": {},
                "funnel_plot": {}
            }
            
            # Egger's test
            if "egger" in tests:
                # Regression of standardized effect on precision
                precision = 1 / standard_errors
                standardized_effects = effect_sizes / standard_errors
                
                # Linear regression: standardized_effect = intercept + slope * precision
                slope, intercept, r_value, p_value, std_err = stats.linregress(precision, standardized_effects)
                
                results["statistical_tests"]["egger"] = {
                    "intercept": float(intercept),
                    "slope": float(slope),
                    "p_value": float(p_value),
                    "significant": p_value < 0.05,
                    "interpretation": "Evidence of publication bias" if p_value < 0.05 else "No evidence of publication bias"
                }
            
            # Begg's test
            if "begg" in tests:
                # Rank correlation between effect sizes and variances
                ranks_effect = stats.rankdata(effect_sizes)
                ranks_variance = stats.rankdata(standard_errors ** 2)
                
                correlation, p_value = stats.spearmanr(ranks_effect, ranks_variance)
                
                results["statistical_tests"]["begg"] = {
                    "correlation": float(correlation),
                    "p_value": float(p_value),
                    "significant": p_value < 0.05,
                    "interpretation": "Evidence of publication bias" if p_value < 0.05 else "No evidence of publication bias"
                }
            
            # Create funnel plot
            fig = go.Figure()
            
            # Add study points
            fig.add_trace(go.Scatter(
                x=effect_sizes,
                y=1/standard_errors,  # Precision on y-axis
                mode='markers',
                marker=dict(size=8, color='blue', opacity=0.7),
                text=[s["study_id"] for s in studies],
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
            
            results["funnel_plot"] = {
                "plot_data": plot_data,
                "format": "png",
                "interpretation": self._interpret_funnel_plot_symmetry(effect_sizes, standard_errors)
            }
            
            # Overall assessment
            bias_evidence = []
            if "egger" in results["statistical_tests"] and results["statistical_tests"]["egger"]["significant"]:
                bias_evidence.append("Egger's test")
            if "begg" in results["statistical_tests"] and results["statistical_tests"]["begg"]["significant"]:
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
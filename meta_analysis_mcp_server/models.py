"""
Pydantic models for meta-analysis MCP server output validation.
Provides type safety and validation for complex statistical outputs.
"""

from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ConfidenceInterval(BaseModel):
    """Confidence interval with lower and upper bounds."""
    lower: float = Field(..., description="Lower bound of confidence interval")
    upper: float = Field(..., description="Upper bound of confidence interval")
    level: float = Field(default=0.95, description="Confidence level (e.g., 0.95 for 95% CI)")


class HeterogeneityMetrics(BaseModel):
    """Heterogeneity assessment metrics."""
    i_squared: float = Field(..., ge=0, le=100, description="I² statistic (0-100%)")
    tau_squared: float = Field(..., ge=0, description="Tau² statistic")
    q_statistic: float = Field(..., ge=0, description="Cochran's Q statistic")
    q_p_value: float = Field(..., ge=0, le=1, description="P-value for Q test")
    interpretation: str = Field(..., description="Interpretation of heterogeneity level")


class StudyData(BaseModel):
    """Individual study data structure."""
    study_id: str = Field(..., description="Unique study identifier")
    effect_size: float = Field(..., description="Effect size estimate")
    standard_error: float = Field(..., gt=0, description="Standard error of effect size")
    sample_size: int = Field(..., gt=0, description="Total sample size")
    study_name: Optional[str] = Field(None, description="Human-readable study name")
    weight: Optional[float] = Field(None, ge=0, le=100, description="Study weight in meta-analysis")


class MetaAnalysisResult(BaseModel):
    """Complete meta-analysis results with validation."""
    pooled_effect_size: float = Field(..., description="Pooled effect size estimate")
    confidence_interval: ConfidenceInterval = Field(..., description="95% confidence interval")
    p_value: float = Field(..., ge=0, le=1, description="Statistical significance p-value")
    method: str = Field(..., description="Meta-analysis method used")
    measure: str = Field(..., description="Effect size measure")
    studies_analyzed: int = Field(..., gt=0, description="Number of studies included")
    heterogeneity: HeterogeneityMetrics = Field(..., description="Heterogeneity assessment")
    studies: List[StudyData] = Field(..., description="Individual study data")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")


class ForestPlotResult(BaseModel):
    """Forest plot generation results."""
    plot_file: str = Field(..., description="Path to generated forest plot file")
    format: str = Field(..., description="Plot file format (png, svg, etc.)")
    studies_plotted: int = Field(..., gt=0, description="Number of studies plotted")
    title: str = Field(..., description="Plot title")
    dimensions: Optional[Dict[str, int]] = Field(None, description="Plot dimensions (width, height)")
    file_size_bytes: Optional[int] = Field(None, gt=0, description="File size in bytes")


class PublicationBiasTest(BaseModel):
    """Individual publication bias test result."""
    test_name: str = Field(..., description="Name of the bias test")
    statistic: float = Field(..., description="Test statistic value")
    p_value: float = Field(..., ge=0, le=1, description="P-value of the test")
    interpretation: str = Field(..., description="Interpretation of test result")


class PublicationBiasResult(BaseModel):
    """Publication bias assessment results."""
    funnel_plot: str = Field(..., description="Path to funnel plot file")
    tests_performed: List[str] = Field(..., description="List of bias tests performed")
    egger_test: Optional[PublicationBiasTest] = Field(None, description="Egger's test results")
    begg_test: Optional[PublicationBiasTest] = Field(None, description="Begg's test results")
    conclusion: str = Field(..., description="Overall bias assessment conclusion")
    studies_analyzed: int = Field(..., gt=0, description="Number of studies analyzed")


class ROBDomainAssessment(BaseModel):
    """Risk of bias assessment for individual domain."""
    domain: str = Field(..., description="ROB domain name")
    judgment: str = Field(..., description="Risk judgment (Low/Some concerns/High)")
    rationale: str = Field(..., description="Rationale for judgment")
    support_for_judgment: Optional[str] = Field(None, description="Supporting evidence")


class ROBAssessmentResult(BaseModel):
    """Complete risk of bias assessment result."""
    study_id: str = Field(..., description="Study identifier")
    overall_rob: str = Field(..., description="Overall risk of bias judgment")
    domain_assessments: List[ROBDomainAssessment] = Field(..., description="Individual domain assessments")
    assessment_mode: str = Field(..., description="Assessment mode used")
    rob_version: str = Field(default="ROB 2.0", description="ROB tool version")


class PRISMAItem(BaseModel):
    """Individual PRISMA checklist item."""
    item_number: str = Field(..., description="PRISMA item number")
    item_description: str = Field(..., description="Item description")
    status: str = Field(..., description="Compliance status")
    page_number: Optional[str] = Field(None, description="Page number where addressed")
    notes: Optional[str] = Field(None, description="Additional notes")


class PRISMAChecklistResult(BaseModel):
    """PRISMA 2020 checklist assessment result."""
    checklist_items: List[PRISMAItem] = Field(..., description="Individual checklist items")
    compliance_score: float = Field(..., ge=0, le=100, description="Overall compliance percentage")
    grade: str = Field(..., description="Compliance grade (A+, A, B+, etc.)")
    flow_diagram: Optional[str] = Field(None, description="Path to PRISMA flow diagram")
    total_items: int = Field(..., gt=0, description="Total number of checklist items")
    completed_items: int = Field(..., ge=0, description="Number of completed items")


class GRADEFactor(BaseModel):
    """Individual GRADE assessment factor."""
    factor: str = Field(..., description="GRADE factor name")
    rating: str = Field(..., description="Factor rating")
    rationale: str = Field(..., description="Rationale for rating")
    impact: str = Field(..., description="Impact on evidence quality")


class GRADEAssessmentResult(BaseModel):
    """GRADE evidence quality assessment result."""
    outcome: str = Field(..., description="Outcome being assessed")
    initial_certainty: str = Field(..., description="Initial certainty level")
    factors_assessed: List[GRADEFactor] = Field(..., description="Individual GRADE factors")
    overall_certainty: str = Field(..., description="Final certainty level")
    certainty_rationale: str = Field(..., description="Rationale for final certainty")
    recommendation_strength: Optional[str] = Field(None, description="Recommendation strength")


class CochraneReportResult(BaseModel):
    """Cochrane systematic review report result."""
    report_file: str = Field(..., description="Path to generated report file")
    format: str = Field(..., description="Report format (HTML, PDF, etc.)")
    sections_included: List[str] = Field(..., description="Report sections included")
    compliance_summary: Dict[str, Any] = Field(..., description="Summary of compliance assessments")
    generation_timestamp: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")
    file_size_bytes: Optional[int] = Field(None, gt=0, description="Report file size in bytes")


class SessionStatus(BaseModel):
    """MCP session status information."""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    studies_count: int = Field(..., ge=0, description="Number of studies in session")
    analyses_completed: int = Field(..., ge=0, description="Number of analyses completed")
    status: str = Field(..., description="Session status")
    outputs_generated: List[str] = Field(default_factory=list, description="List of generated outputs")


class ToolResponse(BaseModel):
    """Generic tool response wrapper with validation."""
    success: bool = Field(..., description="Whether the tool execution was successful")
    data: Union[
        MetaAnalysisResult,
        ForestPlotResult, 
        PublicationBiasResult,
        HeterogeneityMetrics,
        ROBAssessmentResult,
        PRISMAChecklistResult,
        GRADEAssessmentResult,
        CochraneReportResult,
        SessionStatus,
        Dict[str, Any]
    ] = Field(..., description="Tool-specific result data")
    message: Optional[str] = Field(None, description="Human-readable message")
    errors: Optional[List[str]] = Field(None, description="List of validation errors")
    execution_time_ms: Optional[float] = Field(None, gt=0, description="Execution time in milliseconds")


class ValidationError(BaseModel):
    """Structured validation error information."""
    field: str = Field(..., description="Field that failed validation")
    error_type: str = Field(..., description="Type of validation error")
    message: str = Field(..., description="Human-readable error message")
    invalid_value: Optional[Any] = Field(None, description="The invalid value that caused the error")

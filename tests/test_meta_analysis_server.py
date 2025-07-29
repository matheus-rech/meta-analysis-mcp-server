"""Test suite for Meta-Analysis MCP Server."""

import pytest
import asyncio
import numpy as np
from meta_analysis_mcp_server.tools.meta_analysis import MetaAnalysisTools
from meta_analysis_mcp_server.tools.cochrane_compliance import CochraneComplianceTools


@pytest.fixture
async def meta_tools():
    """Create MetaAnalysisTools instance."""
    return MetaAnalysisTools()


@pytest.fixture
async def cochrane_tools():
    """Create CochraneComplianceTools instance."""
    return CochraneComplianceTools()


@pytest.fixture
def sample_studies():
    """Sample study data for testing."""
    return [
        {
            "study_id": "Study_1",
            "effect_size": 0.5,
            "standard_error": 0.1,
            "sample_size": 100
        },
        {
            "study_id": "Study_2", 
            "effect_size": 0.3,
            "standard_error": 0.15,
            "sample_size": 80
        },
        {
            "study_id": "Study_3",
            "effect_size": 0.7,
            "standard_error": 0.12,
            "sample_size": 120
        }
    ]


@pytest.fixture
def sample_rob_studies():
    """Sample studies for risk of bias assessment."""
    return [
        {
            "study_id": "RCT_001",
            "title": "Randomized controlled trial of intervention X",
            "authors": "Smith et al.",
            "year": 2023,
            "study_design": "RCT",
            "randomization_method": "Computer-generated sequence",
            "blinding": "Double-blind",
            "outcome_assessment": "Blinded assessor",
            "attrition_rate": 5.2,
            "selective_reporting": "Protocol registered"
        }
    ]


class TestMetaAnalysisTools:
    """Test core meta-analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_perform_meta_analysis_fixed(self, meta_tools, sample_studies):
        """Test fixed-effects meta-analysis."""
        result = await meta_tools.perform_meta_analysis(
            studies=sample_studies,
            method="fixed",
            measure="SMD"
        )
        
        assert "meta_analysis_results" in result
        assert "heterogeneity" in result
        assert "study_results" in result
        assert result["meta_analysis_results"]["method"] == "fixed"
        assert result["meta_analysis_results"]["number_of_studies"] == 3
        assert isinstance(result["meta_analysis_results"]["pooled_effect"], float)
        
    @pytest.mark.asyncio
    async def test_perform_meta_analysis_random(self, meta_tools, sample_studies):
        """Test random-effects meta-analysis."""
        result = await meta_tools.perform_meta_analysis(
            studies=sample_studies,
            method="random",
            measure="SMD"
        )
        
        assert result["meta_analysis_results"]["method"] == "random"
        assert "tau_squared" in result["heterogeneity"]
        assert "I_squared" in result["heterogeneity"]
        
    @pytest.mark.asyncio
    async def test_create_forest_plot(self, meta_tools):
        """Test forest plot generation."""
        studies = [
            {
                "study_id": "Study_1",
                "effect_size": 0.5,
                "ci_lower": 0.3,
                "ci_upper": 0.7,
                "weight": 30.0
            },
            {
                "study_id": "Study_2",
                "effect_size": 0.3,
                "ci_lower": 0.1,
                "ci_upper": 0.5,
                "weight": 25.0
            }
        ]
        
        result = await meta_tools.create_forest_plot(
            studies=studies,
            title="Test Forest Plot",
            output_format="png"
        )
        
        assert "forest_plot" in result
        assert result["forest_plot"]["format"] == "png"
        assert result["forest_plot"]["studies_plotted"] == 2
        assert "plot_data" in result["forest_plot"]
        
    @pytest.mark.asyncio
    async def test_assess_heterogeneity(self, meta_tools):
        """Test heterogeneity assessment."""
        studies = [
            {"study_id": "Study_1", "effect_size": 0.5, "variance": 0.01},
            {"study_id": "Study_2", "effect_size": 0.3, "variance": 0.0225},
            {"study_id": "Study_3", "effect_size": 0.7, "variance": 0.0144}
        ]
        
        result = await meta_tools.assess_heterogeneity(studies=studies)
        
        assert "heterogeneity_assessment" in result
        assert "Q_statistic" in result["heterogeneity_assessment"]
        assert "I_squared" in result["heterogeneity_assessment"]
        assert "interpretation" in result["heterogeneity_assessment"]
        
    @pytest.mark.asyncio
    async def test_detect_publication_bias(self, meta_tools):
        """Test publication bias detection."""
        studies = [
            {"study_id": f"Study_{i}", "effect_size": 0.3 + i*0.1, "standard_error": 0.1 + i*0.02}
            for i in range(5)
        ]
        
        result = await meta_tools.detect_publication_bias(
            studies=studies,
            tests=["egger"]
        )
        
        assert "statistical_tests" in result
        assert "egger" in result["statistical_tests"]
        assert "funnel_plot" in result
        assert "overall_assessment" in result


class TestCochraneComplianceTools:
    """Test Cochrane compliance functionality."""
    
    @pytest.mark.asyncio
    async def test_assess_risk_of_bias(self, cochrane_tools, sample_rob_studies):
        """Test risk of bias assessment."""
        result = await cochrane_tools.assess_risk_of_bias(
            studies=sample_rob_studies,
            assessment_mode="automated"
        )
        
        assert "assessment_summary" in result
        assert "study_assessments" in result
        assert "domain_summary" in result
        assert "overall_assessment" in result
        assert result["assessment_summary"]["total_studies"] == 1
        
    @pytest.mark.asyncio
    async def test_generate_prisma_checklist(self, cochrane_tools):
        """Test PRISMA checklist generation."""
        review_data = {
            "title": "Systematic review and meta-analysis of intervention X",
            "abstract": "Background: This review examines... Objectives: To assess... Methods: We searched... Results: We found... Conclusions: The evidence suggests...",
            "search_strategy": "We searched MEDLINE, Embase, and Cochrane Library",
            "inclusion_criteria": "Randomized controlled trials",
            "data_extraction": "Two reviewers independently extracted data"
        }
        
        result = await cochrane_tools.generate_prisma_checklist(
            review_data=review_data,
            generate_flow_diagram=True
        )
        
        assert "checklist_summary" in result
        assert "item_assessments" in result
        assert "compliance_score" in result
        assert result["checklist_summary"]["prisma_version"] == "PRISMA 2020"
        assert isinstance(result["compliance_score"]["percentage"], float)
        
    @pytest.mark.asyncio
    async def test_perform_grade_assessment(self, cochrane_tools):
        """Test GRADE assessment."""
        evidence_profile = {
            "outcome": "Primary outcome measure",
            "studies": 5,
            "participants": 500,
            "study_design": "RCT",
            "risk_of_bias": "Low risk",
            "inconsistency": "Low heterogeneity (I² = 20%)",
            "effect_size": 0.5
        }
        
        result = await cochrane_tools.perform_grade_assessment(
            evidence_profile=evidence_profile
        )
        
        assert "assessment_summary" in result
        assert "domain_assessments" in result
        assert "overall_certainty" in result
        assert "certainty_rating" in result
        assert result["overall_certainty"] in ["Very Low", "Low", "Moderate", "High"]
        
    @pytest.mark.asyncio
    async def test_generate_cochrane_report(self, cochrane_tools):
        """Test Cochrane report generation."""
        review_metadata = {
            "title": "Test Systematic Review",
            "authors": ["Dr. Jane Smith", "Dr. John Doe"],
            "abstract": "This is a test abstract",
            "background": "Background information",
            "objectives": "Study objectives",
            "methods": "Methods used",
            "results": "Main results",
            "conclusions": "Conclusions drawn"
        }
        
        result = await cochrane_tools.generate_cochrane_report(
            review_metadata=review_metadata,
            output_format="html"
        )
        
        assert "report_metadata" in result
        assert "sections" in result
        assert "compliance_indicators" in result
        assert result["report_metadata"]["cochrane_compliance"] is True
        assert "formatted_output" in result


class TestIntegration:
    """Integration tests combining multiple tools."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, meta_tools, cochrane_tools, sample_studies):
        """Test complete meta-analysis workflow with Cochrane compliance."""
        # Perform meta-analysis
        meta_result = await meta_tools.perform_meta_analysis(
            studies=sample_studies,
            method="random"
        )
        
        # Generate PRISMA checklist
        review_data = {
            "title": "Systematic review and meta-analysis of test intervention",
            "abstract": "Background and objectives included",
            "search_strategy": "Comprehensive search performed"
        }
        
        prisma_result = await cochrane_tools.generate_prisma_checklist(
            review_data=review_data
        )
        
        # Generate final report
        report_metadata = {
            "title": "Complete Meta-Analysis Report",
            "authors": ["Test Author"],
            "abstract": "Test abstract",
            "results": "Significant effect found"
        }
        
        report_result = await cochrane_tools.generate_cochrane_report(
            review_metadata=report_metadata,
            analysis_results=meta_result,
            prisma_checklist=prisma_result
        )
        
        # Verify integration
        assert meta_result["meta_analysis_results"]["number_of_studies"] == 3
        assert prisma_result["compliance_score"]["percentage"] > 0
        assert report_result["compliance_indicators"]["cochrane_compliance"] is True
        assert report_result["compliance_indicators"]["prisma_compliance"] > 0


if __name__ == "__main__":
    pytest.main([__file__])
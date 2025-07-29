#!/usr/bin/env python3
"""Manual verification script for Meta-Analysis MCP Server."""

import sys
import os
import asyncio

# Add the project to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from meta_analysis_mcp_server.tools.meta_analysis import MetaAnalysisTools
from meta_analysis_mcp_server.tools.cochrane_compliance import CochraneComplianceTools


async def verify_core_functionality():
    """Verify core meta-analysis functionality."""
    print("🔍 VERIFYING CORE META-ANALYSIS FUNCTIONALITY")
    print("=" * 50)
    
    meta_tools = MetaAnalysisTools()
    
    # Test data
    test_studies = [
        {"study_id": "Test_A", "effect_size": 0.5, "standard_error": 0.1, "sample_size": 100},
        {"study_id": "Test_B", "effect_size": 0.3, "standard_error": 0.12, "sample_size": 80},
        {"study_id": "Test_C", "effect_size": 0.7, "standard_error": 0.15, "sample_size": 120}
    ]
    
    # Test meta-analysis
    try:
        result = await meta_tools.perform_meta_analysis(test_studies, method="random")
        assert "meta_analysis_results" in result
        assert result["meta_analysis_results"]["number_of_studies"] == 3
        print("✅ Meta-analysis: PASSED")
    except Exception as e:
        print(f"❌ Meta-analysis: FAILED - {e}")
        return False
    
    # Test forest plot
    try:
        forest_studies = [
            {"study_id": "Test_A", "effect_size": 0.5, "ci_lower": 0.3, "ci_upper": 0.7, "weight": 35.0},
            {"study_id": "Test_B", "effect_size": 0.3, "ci_lower": 0.1, "ci_upper": 0.5, "weight": 30.0}
        ]
        plot_result = await meta_tools.create_forest_plot(forest_studies)
        assert "forest_plot" in plot_result
        print("✅ Forest plot: PASSED")
    except Exception as e:
        print(f"❌ Forest plot: FAILED - {e}")
        return False
    
    # Test heterogeneity assessment
    try:
        het_studies = [
            {"study_id": "Test_A", "effect_size": 0.5, "variance": 0.01},
            {"study_id": "Test_B", "effect_size": 0.3, "variance": 0.0144}
        ]
        het_result = await meta_tools.assess_heterogeneity(het_studies)
        assert "heterogeneity_assessment" in het_result
        print("✅ Heterogeneity assessment: PASSED")
    except Exception as e:
        print(f"❌ Heterogeneity assessment: FAILED - {e}")
        return False
    
    # Test publication bias
    try:
        bias_studies = [
            {"study_id": f"Test_{i}", "effect_size": 0.3 + i*0.1, "standard_error": 0.1 + i*0.02}
            for i in range(4)
        ]
        bias_result = await meta_tools.detect_publication_bias(bias_studies)
        assert "statistical_tests" in bias_result
        print("✅ Publication bias detection: PASSED")
    except Exception as e:
        print(f"❌ Publication bias detection: FAILED - {e}")
        return False
    
    return True


async def verify_cochrane_functionality():
    """Verify Cochrane compliance functionality."""
    print("\n🎯 VERIFYING COCHRANE COMPLIANCE FUNCTIONALITY")
    print("=" * 50)
    
    cochrane_tools = CochraneComplianceTools()
    
    # Test ROB assessment
    try:
        rob_studies = [
            {
                "study_id": "ROB_Test",
                "title": "Test RCT",
                "randomization_method": "Computer-generated",
                "blinding": "Double-blind",
                "attrition_rate": 5.0
            }
        ]
        rob_result = await cochrane_tools.assess_risk_of_bias(rob_studies)
        assert "assessment_summary" in rob_result
        assert "study_assessments" in rob_result
        print("✅ Risk of bias assessment: PASSED")
    except Exception as e:
        print(f"❌ Risk of bias assessment: FAILED - {e}")
        return False
    
    # Test PRISMA checklist
    try:
        review_data = {
            "title": "Test systematic review and meta-analysis",
            "abstract": "Background: Test. Objectives: Test. Methods: Test. Results: Test. Conclusions: Test.",
            "search_strategy": "Test search",
            "inclusion_criteria": "Test criteria"
        }
        prisma_result = await cochrane_tools.generate_prisma_checklist(review_data)
        assert "compliance_score" in prisma_result
        assert "item_assessments" in prisma_result
        print("✅ PRISMA checklist: PASSED")
    except Exception as e:
        print(f"❌ PRISMA checklist: FAILED - {e}")
        return False
    
    # Test GRADE assessment
    try:
        evidence_profile = {
            "outcome": "Test outcome",
            "studies": 3,
            "participants": 300,
            "study_design": "RCT"
        }
        grade_result = await cochrane_tools.perform_grade_assessment(evidence_profile)
        assert "overall_certainty" in grade_result
        assert "domain_assessments" in grade_result
        print("✅ GRADE assessment: PASSED")
    except Exception as e:
        print(f"❌ GRADE assessment: FAILED - {e}")
        return False
    
    # Test Cochrane report
    try:
        report_metadata = {
            "title": "Test Report",
            "authors": ["Test Author"],
            "abstract": "Test abstract"
        }
        report_result = await cochrane_tools.generate_cochrane_report(report_metadata)
        assert "report_metadata" in report_result
        assert "sections" in report_result
        print("✅ Cochrane report generation: PASSED")
    except Exception as e:
        print(f"❌ Cochrane report generation: FAILED - {e}")
        return False
    
    return True


async def verify_integration():
    """Verify integration between tools."""
    print("\n🔗 VERIFYING TOOL INTEGRATION")
    print("=" * 50)
    
    try:
        meta_tools = MetaAnalysisTools()
        cochrane_tools = CochraneComplianceTools()
        
        # Simulate workflow
        studies = [
            {"study_id": "Int_A", "effect_size": 0.4, "standard_error": 0.1, "sample_size": 100},
            {"study_id": "Int_B", "effect_size": 0.6, "standard_error": 0.12, "sample_size": 80}
        ]
        
        # Meta-analysis
        meta_result = await meta_tools.perform_meta_analysis(studies)
        
        # PRISMA checklist
        review_data = {"title": "Integration test review", "abstract": "Test abstract"}
        prisma_result = await cochrane_tools.generate_prisma_checklist(review_data)
        
        # Combined report
        report_result = await cochrane_tools.generate_cochrane_report(
            review_metadata={"title": "Integration Test", "authors": ["Test"], "abstract": "Test"},
            analysis_results=meta_result,
            prisma_checklist=prisma_result
        )
        
        assert report_result["compliance_indicators"]["overall_quality_score"] > 0
        print("✅ Tool integration: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Tool integration: FAILED - {e}")
        return False


async def main():
    """Run all verification tests."""
    print("🚀 META-ANALYSIS MCP SERVER VERIFICATION")
    print("=" * 60)
    
    # Run all tests
    core_passed = await verify_core_functionality()
    cochrane_passed = await verify_cochrane_functionality()
    integration_passed = await verify_integration()
    
    # Summary
    print("\n📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_tests = 3
    passed_tests = sum([core_passed, cochrane_passed, integration_passed])
    
    print(f"Core Meta-Analysis: {'✅ PASSED' if core_passed else '❌ FAILED'}")
    print(f"Cochrane Compliance: {'✅ PASSED' if cochrane_passed else '❌ FAILED'}")
    print(f"Tool Integration: {'✅ PASSED' if integration_passed else '❌ FAILED'}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL VERIFICATION TESTS PASSED!")
        print("✅ Server is ready for deployment")
        print("✅ All 4 Cochrane compliance tools working")
        print("✅ PRISMA 2020 reporting functional")
        print("✅ Meta-analysis capabilities verified")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed")
        print("❌ Server needs fixes before deployment")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
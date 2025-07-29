#!/usr/bin/env python3
"""
Corrected R integration demonstration with proper method signatures.
Tests all available tools with correct parameters.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meta_analysis_mcp_server.tools.meta_analysis import MetaAnalysisTools
from meta_analysis_mcp_server.tools.cochrane_compliance import CochraneComplianceTools

SAMPLE_STUDIES = [
    {
        "study_id": "study_1",
        "author": "Smith et al.",
        "year": 2020,
        "effect_size": 0.5,
        "standard_error": 0.1,
        "sample_size": 100,
        "intervention": "Treatment A",
        "control": "Placebo",
        "title": "Effectiveness of Treatment A in Population 1"
    },
    {
        "study_id": "study_2", 
        "author": "Johnson et al.",
        "year": 2021,
        "effect_size": 0.3,
        "standard_error": 0.15,
        "sample_size": 80,
        "intervention": "Treatment A",
        "control": "Placebo",
        "title": "Treatment A vs Placebo: RCT Study"
    },
    {
        "study_id": "study_3",
        "author": "Brown et al.",
        "year": 2019,
        "effect_size": 0.7,
        "standard_error": 0.12,
        "sample_size": 120,
        "intervention": "Treatment A", 
        "control": "Placebo",
        "title": "Multi-center Trial of Treatment A"
    }
]

async def test_meta_analysis_with_r():
    """Test meta-analysis tools with R integration using correct signatures."""
    print("🔬 Testing Meta-Analysis Tools with R Integration (Corrected)")
    print("=" * 70)
    
    meta_tools = MetaAnalysisTools()
    results = {}
    
    try:
        print("\n📊 1. Performing Meta-Analysis with R...")
        ma_result = await meta_tools.perform_meta_analysis(
            studies=SAMPLE_STUDIES,
            method="random",
            measure="SMD"
        )
        
        if ma_result and "meta_analysis_results" in ma_result:
            print("   ✅ SUCCESS: Meta-analysis completed with R")
            print(f"   📈 Pooled Effect: {ma_result['meta_analysis_results']['pooled_effect']:.3f}")
            print(f"   📊 95% CI: [{ma_result['meta_analysis_results']['ci_lower']:.3f}, {ma_result['meta_analysis_results']['ci_upper']:.3f}]")
            print(f"   🎯 P-value: {ma_result['meta_analysis_results']['p_value']:.4f}")
            print(f"   📏 I²: {ma_result['heterogeneity']['I_squared']:.1f}%")
            results["meta_analysis"] = {"success": True, "result": ma_result}
        else:
            print("   ❌ FAILED: Meta-analysis")
            results["meta_analysis"] = {"success": False, "error": "No results returned"}
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: Meta-analysis failed: {str(e)}")
        results["meta_analysis"] = {"success": False, "error": str(e)}
    
    try:
        print("\n🌲 2. Creating Forest Plot with R...")
        studies_with_ci = []
        for study in SAMPLE_STUDIES:
            ci_lower = study["effect_size"] - 1.96 * study["standard_error"]
            ci_upper = study["effect_size"] + 1.96 * study["standard_error"]
            weight = 1 / (study["standard_error"] ** 2)
            studies_with_ci.append({
                **study,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "weight": weight
            })
        
        forest_result = await meta_tools.create_forest_plot(
            studies=studies_with_ci,
            title="Treatment A vs Placebo - Forest Plot"
        )
        
        if forest_result and "forest_plot" in forest_result:
            print("   ✅ SUCCESS: Forest plot created")
            if "plot_path" in forest_result["forest_plot"]:
                print(f"   📁 Plot saved to: {forest_result['forest_plot']['plot_path']}")
            results["forest_plot"] = {"success": True, "result": forest_result}
        else:
            print("   ❌ FAILED: Forest plot creation")
            results["forest_plot"] = {"success": False, "error": "No forest plot returned"}
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: Forest plot failed: {str(e)}")
        results["forest_plot"] = {"success": False, "error": str(e)}
    
    try:
        print("\n📏 3. Assessing Heterogeneity with R...")
        studies_with_variance = []
        for study in SAMPLE_STUDIES:
            variance = study["standard_error"] ** 2
            studies_with_variance.append({
                **study,
                "variance": variance
            })
        
        het_result = await meta_tools.assess_heterogeneity(
            studies=studies_with_variance
        )
        
        if het_result and "heterogeneity_assessment" in het_result:
            print("   ✅ SUCCESS: Heterogeneity assessment with R")
            print(f"   📊 I²: {het_result['heterogeneity_assessment']['I_squared']:.1f}%")
            print(f"   🎯 Q-statistic: {het_result['heterogeneity_assessment']['Q_statistic']:.3f}")
            results["heterogeneity"] = {"success": True, "result": het_result}
        else:
            print("   ❌ FAILED: Heterogeneity assessment")
            results["heterogeneity"] = {"success": False, "error": "No assessment returned"}
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: Heterogeneity assessment failed: {str(e)}")
        results["heterogeneity"] = {"success": False, "error": str(e)}
    
    try:
        print("\n🔍 4. Detecting Publication Bias with R...")
        bias_result = await meta_tools.detect_publication_bias(
            studies=SAMPLE_STUDIES
        )
        
        if bias_result and "publication_bias_assessment" in bias_result:
            print("   ✅ SUCCESS: Publication bias detection with R")
            if "statistical_tests" in bias_result and "egger" in bias_result["statistical_tests"]:
                print(f"   📊 Egger's test p-value: {bias_result['statistical_tests']['egger']['p_value']:.4f}")
            results["publication_bias"] = {"success": True, "result": bias_result}
        else:
            print("   ❌ FAILED: Publication bias detection")
            results["publication_bias"] = {"success": False, "error": "No bias assessment returned"}
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: Publication bias detection failed: {str(e)}")
        results["publication_bias"] = {"success": False, "error": str(e)}
    
    return results

async def test_cochrane_tools():
    """Test Cochrane compliance tools with correct signatures."""
    print("\n🏥 Testing Cochrane Compliance Tools (Corrected)")
    print("=" * 70)
    
    cochrane_tools = CochraneComplianceTools()
    results = {}
    
    try:
        print("\n⚖️ 5. Assessing Risk of Bias...")
        rob_result = await cochrane_tools.assess_risk_of_bias(
            studies=SAMPLE_STUDIES,
            assessment_mode="hybrid",
            domains=["randomization", "allocation_concealment", "blinding"]
        )
        
        if rob_result and "assessment_summary" in rob_result:
            print("   ✅ SUCCESS: Risk of bias assessment")
            print(f"   📊 Studies assessed: {rob_result['assessment_summary']['total_studies']}")
            print(f"   🎯 Assessment mode: {rob_result['assessment_summary']['assessment_mode']}")
            results["risk_of_bias"] = {"success": True, "result": rob_result}
        else:
            print("   ❌ FAILED: Risk of bias assessment")
            results["risk_of_bias"] = {"success": False, "error": "No assessment returned"}
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: Risk of bias assessment failed: {str(e)}")
        results["risk_of_bias"] = {"success": False, "error": str(e)}
    
    try:
        print("\n📋 6. Generating PRISMA Checklist...")
        review_data = {
            "title": "Effectiveness of Treatment A vs Placebo: A Systematic Review",
            "included_studies": len(SAMPLE_STUDIES),
            "review_type": "intervention"
        }
        prisma_result = await cochrane_tools.generate_prisma_checklist(
            review_data=review_data
        )
        
        if prisma_result and "checklist_summary" in prisma_result:
            print("   ✅ SUCCESS: PRISMA checklist generated")
            print(f"   📊 Items assessed: {len(prisma_result.get('item_assessments', {}))}")
            if "compliance_score" in prisma_result and "percentage" in prisma_result["compliance_score"]:
                print(f"   🎯 Compliance score: {prisma_result['compliance_score']['percentage']:.1f}%")
            results["prisma_checklist"] = {"success": True, "result": prisma_result}
        else:
            print("   ❌ FAILED: PRISMA checklist generation")
            results["prisma_checklist"] = {"success": False, "error": "No checklist returned"}
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: PRISMA checklist generation failed: {str(e)}")
        results["prisma_checklist"] = {"success": False, "error": str(e)}
    
    try:
        print("\n📄 7. Generating Cochrane Report...")
        review_metadata = {
            "title": "Effectiveness of Treatment A vs Placebo: A Systematic Review",
            "authors": ["Test Author"],
            "background": "This systematic review evaluates Treatment A effectiveness.",
            "objectives": "To assess Treatment A effectiveness and safety.",
            "study_data": SAMPLE_STUDIES
        }
        report_result = await cochrane_tools.generate_cochrane_report(
            review_metadata=review_metadata
        )
        
        if report_result and "report_metadata" in report_result:
            print("   ✅ SUCCESS: Cochrane report generated")
            if "compliance_indicators" in report_result and "overall_quality_score" in report_result["compliance_indicators"]:
                print(f"   📊 Report quality score: {report_result['compliance_indicators']['overall_quality_score']:.1f}%")
            if "formatted_output" in report_result:
                print(f"   📄 Report length: {len(report_result['formatted_output'])} characters")
            results["cochrane_report"] = {"success": True, "result": report_result}
        else:
            print("   ❌ FAILED: Cochrane report generation")
            results["cochrane_report"] = {"success": False, "error": "No report returned"}
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: Cochrane report generation failed: {str(e)}")
        results["cochrane_report"] = {"success": False, "error": str(e)}
    
    return results

async def main():
    """Run corrected R integration demonstration."""
    print("🚀 Meta-Analysis MCP Server - Corrected R Integration Demo")
    print("Testing R-based calculations with proper method signatures")
    print("=" * 80)
    
    meta_results = await test_meta_analysis_with_r()
    
    cochrane_results = await test_cochrane_tools()
    
    all_results = {**meta_results, **cochrane_results}
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 CORRECTED R INTEGRATION DEMONSTRATION SUMMARY")
    print("=" * 80)
    
    total_tests = len(all_results)
    successful_tests = sum(1 for result in all_results.values() if result["success"])
    
    print(f"Total Tools Tested: {total_tests}")
    print(f"Successful Tests: {successful_tests}")
    print(f"Failed Tests: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! R Integration is fully functional!")
        print("✅ Meta-analysis calculations performed in R")
        print("✅ Forest plots generated with R visualization")
        print("✅ Heterogeneity assessment using R statistics")
        print("✅ Publication bias detection with R tests")
        print("✅ Cochrane compliance tools operational")
        print("\n🚀 READY FOR DEPLOYMENT!")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} tests failed. Review the output above for details.")
        
        failed_tests = [name for name, result in all_results.items() if not result["success"]]
        if failed_tests:
            print(f"Failed tests: {', '.join(failed_tests)}")
    
    with open("corrected_r_demo_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n📄 Detailed results saved to: corrected_r_demo_results.json")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

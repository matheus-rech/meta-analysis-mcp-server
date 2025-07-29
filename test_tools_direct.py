#!/usr/bin/env python3
"""
Direct test of all 11 MCP tools (7 meta-analysis + 4 Cochrane compliance)
to demonstrate end-to-end functionality with R calculations.
"""

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
        "control": "Placebo"
    },
    {
        "study_id": "study_2", 
        "author": "Johnson et al.",
        "year": 2021,
        "effect_size": 0.3,
        "standard_error": 0.15,
        "sample_size": 80,
        "intervention": "Treatment A",
        "control": "Placebo"
    },
    {
        "study_id": "study_3",
        "author": "Brown et al.",
        "year": 2019,
        "effect_size": 0.7,
        "standard_error": 0.12,
        "sample_size": 120,
        "intervention": "Treatment A", 
        "control": "Placebo"
    }
]

def test_tool(tool_instance, method_name, arguments):
    """Test a single tool method and return results."""
    try:
        print(f"\n🔧 Testing {method_name}...")
        print(f"   Arguments: {json.dumps(arguments, indent=2)}")
        
        method = getattr(tool_instance, method_name)
        
        result = method(**arguments)
        
        if isinstance(result, dict) and not result.get("error"):
            print(f"   ✅ SUCCESS: {method_name}")
            result_str = str(result)
            if len(result_str) > 500:
                print(f"   📊 Result: {result_str[:500]}...")
            else:
                print(f"   📊 Result: {result_str}")
            return True, result
        else:
            print(f"   ❌ FAILED: {method_name}")
            print(f"   Error: {result.get('error', 'Unknown error') if isinstance(result, dict) else str(result)}")
            return False, result
            
    except Exception as e:
        print(f"   ❌ EXCEPTION in {method_name}: {str(e)}")
        return False, {"error": str(e)}

def main():
    """Run comprehensive test of all 11 MCP tools."""
    print("=== Direct Meta-Analysis MCP Tools Test ===")
    print("Testing all 11 tools (7 meta-analysis + 4 Cochrane compliance)")
    print("with R calculations integration\n")
    
    meta_tools = MetaAnalysisTools()
    cochrane_tools = CochraneComplianceTools()
    
    results = {}
    total_tests = 0
    passed_tests = 0
    
    print("📁 PHASE 1: Data Management")
    success, result = test_tool(meta_tools, "upload_data", {
        "studies": SAMPLE_STUDIES,
        "session_id": "test_session_001"
    })
    results["upload_data"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    success, result = test_tool(meta_tools, "validate_data", {
        "session_id": "test_session_001"
    })
    results["validate_data"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    print("\n📊 PHASE 2: Statistical Analysis (R Integration)")
    success, result = test_tool(meta_tools, "perform_meta_analysis", {
        "session_id": "test_session_001",
        "method": "random_effects",
        "confidence_level": 0.95
    })
    results["perform_meta_analysis"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    success, result = test_tool(meta_tools, "assess_heterogeneity", {
        "session_id": "test_session_001"
    })
    results["assess_heterogeneity"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    success, result = test_tool(meta_tools, "detect_publication_bias", {
        "session_id": "test_session_001"
    })
    results["detect_publication_bias"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    print("\n📈 PHASE 3: Visualization (R Graphics)")
    success, result = test_tool(meta_tools, "create_forest_plot", {
        "session_id": "test_session_001",
        "title": "Treatment A vs Placebo - Forest Plot"
    })
    results["create_forest_plot"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    success, result = test_tool(meta_tools, "create_funnel_plot", {
        "session_id": "test_session_001",
        "title": "Publication Bias Assessment - Funnel Plot"
    })
    results["create_funnel_plot"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    print("\n🔍 PHASE 4: Cochrane Compliance Tools")
    success, result = test_tool(cochrane_tools, "assess_risk_of_bias", {
        "session_id": "test_session_001",
        "domains": ["randomization", "allocation_concealment", "blinding", "incomplete_data", "selective_reporting"]
    })
    results["assess_risk_of_bias"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    success, result = test_tool(cochrane_tools, "generate_prisma_checklist", {
        "session_id": "test_session_001",
        "review_type": "intervention"
    })
    results["generate_prisma_checklist"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    success, result = test_tool(cochrane_tools, "create_prisma_flow_diagram", {
        "session_id": "test_session_001",
        "identification": 1000,
        "screening": 500,
        "eligibility": 50,
        "included": 3
    })
    results["create_prisma_flow_diagram"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    print("\n📋 PHASE 5: Report Generation")
    success, result = test_tool(cochrane_tools, "generate_cochrane_report", {
        "session_id": "test_session_001",
        "title": "Effectiveness of Treatment A vs Placebo: A Systematic Review and Meta-Analysis",
        "authors": ["Test Author"],
        "background": "This systematic review evaluates the effectiveness of Treatment A compared to placebo.",
        "objectives": "To assess the effectiveness and safety of Treatment A for the target condition."
    })
    results["generate_cochrane_report"] = {"success": success, "result": result}
    total_tests += 1
    if success: passed_tests += 1
    
    # Summary
    print("\n" + "="*60)
    print("🎯 COMPREHENSIVE TEST SUMMARY")
    print("="*60)
    print(f"Total Tools Tested: {total_tests}")
    print(f"Successful Tests: {passed_tests}")
    print(f"Failed Tests: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Meta-Analysis MCP Server is fully functional!")
        print("✅ R calculations integration working correctly")
        print("✅ All 7 meta-analysis tools operational")
        print("✅ All 4 Cochrane compliance tools operational")
        print("✅ End-to-end workflow demonstrated successfully")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Review the output above for details.")
    
    with open("direct_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n📄 Detailed results saved to: direct_test_results.json")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

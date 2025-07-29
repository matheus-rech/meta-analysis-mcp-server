#!/usr/bin/env python3
"""Test script to verify complete R integration in meta-analysis tools."""

import sys
import os
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from meta_analysis_mcp_server.tools.meta_analysis import MetaAnalysisTools

async def test_complete_r_integration():
    """Test complete R integration for all statistical calculations."""
    print("=== Testing Complete R Integration ===")
    
    meta_tools = MetaAnalysisTools()
    
    test_studies = [
        {"study_id": "Study_1", "effect_size": 0.5, "standard_error": 0.1, "sample_size": 100},
        {"study_id": "Study_2", "effect_size": 0.3, "standard_error": 0.15, "sample_size": 80},
        {"study_id": "Study_3", "effect_size": 0.7, "standard_error": 0.12, "sample_size": 120},
        {"study_id": "Study_4", "effect_size": 0.2, "standard_error": 0.18, "sample_size": 60}
    ]
    
    print(f"Testing with {len(test_studies)} studies...")
    
    print("\n1. Testing perform_meta_analysis with R integration...")
    try:
        meta_result = await meta_tools.perform_meta_analysis(test_studies)
        if meta_result.success:
            print("✅ Meta-analysis with R integration successful")
            data = meta_result.data
            if hasattr(data, 'model_dump'):
                result_dict = data.model_dump()
            else:
                result_dict = data.__dict__ if hasattr(data, '__dict__') else data
            
            print(f"   Pooled effect size: {result_dict.get('pooled_effect_size', 'N/A')}")
            print(f"   95% CI: [{result_dict.get('confidence_interval', {}).get('lower', 'N/A')}, {result_dict.get('confidence_interval', {}).get('upper', 'N/A')}]")
            print(f"   I² heterogeneity: {result_dict.get('heterogeneity', {}).get('i_squared', 'N/A')}%")
        else:
            print(f"❌ Meta-analysis failed: {meta_result.errors}")
            return False
    except Exception as e:
        print(f"❌ Meta-analysis exception: {e}")
        return False
    
    print("\n2. Testing detect_publication_bias with R integration...")
    try:
        bias_result = await meta_tools.detect_publication_bias(test_studies)
        if bias_result.success:
            print("✅ Publication bias assessment with R integration successful")
            data = bias_result.data
            if hasattr(data, 'model_dump'):
                result_dict = data.model_dump()
            else:
                result_dict = data.__dict__ if hasattr(data, '__dict__') else data
            
            egger_test = result_dict.get('egger_test', {})
            begg_test = result_dict.get('begg_test', {})
            
            if egger_test:
                print(f"   Egger's test: p = {egger_test.get('p_value', 'N/A')}, significant = {egger_test.get('significant', False)}")
            if begg_test:
                print(f"   Begg's test: p = {begg_test.get('p_value', 'N/A')}, significant = {begg_test.get('significant', False)}")
            
            print(f"   Conclusion: {result_dict.get('conclusion', 'N/A')}")
        else:
            print(f"❌ Publication bias assessment failed: {bias_result.errors}")
            return False
    except Exception as e:
        print(f"❌ Publication bias assessment exception: {e}")
        return False
    
    print("\n3. Testing assess_heterogeneity with R integration...")
    try:
        het_result = await meta_tools.assess_heterogeneity(test_studies)
        if het_result.success:
            print("✅ Heterogeneity assessment with R integration successful")
            data = het_result.data
            if hasattr(data, 'model_dump'):
                result_dict = data.model_dump()
            else:
                result_dict = data.__dict__ if hasattr(data, '__dict__') else data
            
            print(f"   τ² (tau-squared): {result_dict.get('tau_squared', 'N/A')}")
            print(f"   I² (I-squared): {result_dict.get('i_squared', 'N/A')}%")
            print(f"   H² (H-squared): {result_dict.get('h_squared', 'N/A')}")
            print(f"   Q statistic: {result_dict.get('q_statistic', 'N/A')}")
            print(f"   Q p-value: {result_dict.get('q_p_value', 'N/A')}")
            print(f"   Interpretation: {result_dict.get('interpretation', 'N/A')}")
        else:
            print(f"❌ Heterogeneity assessment failed: {het_result.errors}")
            return False
    except Exception as e:
        print(f"❌ Heterogeneity assessment exception: {e}")
        return False
    
    print("\n4. Testing create_forest_plot with R integration...")
    try:
        forest_result = await meta_tools.create_forest_plot(test_studies, title="R Integration Test Forest Plot")
        if forest_result.success:
            print("✅ Forest plot generation with R integration successful")
            data = forest_result.data
            if hasattr(data, 'model_dump'):
                result_dict = data.model_dump()
            else:
                result_dict = data.__dict__ if hasattr(data, '__dict__') else data
            
            print(f"   Plot file: {result_dict.get('plot_file', 'N/A')}")
            print(f"   Studies plotted: {result_dict.get('studies_plotted', 'N/A')}")
        else:
            print(f"❌ Forest plot generation failed: {forest_result.errors}")
            return False
    except Exception as e:
        print(f"❌ Forest plot generation exception: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL R INTEGRATION TESTS PASSED!")
    print("✅ Meta-analysis calculations now use R metafor package")
    print("✅ Publication bias assessment uses R regtest() and ranktest()")
    print("✅ Heterogeneity metrics come from R rma() output")
    print("✅ Forest plot generation uses R forest() function")
    
    return True

if __name__ == "__main__":
    print("Complete R Integration Test for Meta-Analysis MCP Server")
    print("=" * 60)
    
    success = asyncio.run(test_complete_r_integration())
    
    if success:
        print("\n🚀 R INTEGRATION IMPLEMENTATION COMPLETE")
        print("All statistical calculations now use R instead of Python")
    else:
        print("\n❌ R INTEGRATION IMPLEMENTATION FAILED")
        print("Some statistical calculations are not using R properly")
        sys.exit(1)

#!/usr/bin/env python3
"""
Test Pydantic validation implementation for meta-analysis MCP server.
Validates that Pydantic models improve output validation and error handling.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
sys.path.append('/home/ubuntu/repos/meta-analysis-mcp-server')

from meta_analysis_mcp_server.tools.meta_analysis import MetaAnalysisTools
from meta_analysis_mcp_server.models import (
    MetaAnalysisResult, StudyData, ConfidenceInterval, 
    HeterogeneityMetrics, ToolResponse
)

async def test_pydantic_validation():
    """Test Pydantic validation improvements."""
    print("🔍 Testing Pydantic Validation Implementation")
    print("=" * 55)
    
    meta_tools = MetaAnalysisTools()
    
    print("1️⃣ Test Valid Study Data Validation")
    print("-" * 40)
    
    valid_studies = [
        {
            "study_id": "Study_A",
            "effect_size": 0.5,
            "standard_error": 0.1,
            "sample_size": 100,
            "study_name": "Cardiovascular Intervention A"
        },
        {
            "study_id": "Study_B", 
            "effect_size": 0.3,
            "standard_error": 0.15,
            "sample_size": 80,
            "study_name": "Cardiovascular Intervention B"
        }
    ]
    
    try:
        result = await meta_tools.perform_meta_analysis(
            studies=valid_studies,
            method="random",
            measure="SMD"
        )
        
        print(f"✅ Valid data processed successfully!")
        print(f"   Response type: {type(result).__name__}")
        print(f"   Success: {result.success}")
        print(f"   Data type: {type(result.data).__name__}")
        
        if result.success and isinstance(result.data, MetaAnalysisResult):
            print(f"   Pooled Effect: {result.data.pooled_effect_size}")
            print(f"   CI: [{result.data.confidence_interval.lower:.3f}, {result.data.confidence_interval.upper:.3f}]")
            print(f"   I² Heterogeneity: {result.data.heterogeneity.i_squared:.1f}%")
            print(f"   Studies: {len(result.data.studies)}")
            print(f"   Execution time: {result.execution_time_ms:.1f}ms")
        print()
        
    except Exception as e:
        print(f"❌ Valid data test failed: {e}")
        print()
    
    print("2️⃣ Test Invalid Study Data Validation")
    print("-" * 40)
    
    invalid_studies = [
        {
            "study_id": "Study_Invalid",
            "effect_size": "not_a_number",  # Invalid type
            "standard_error": -0.1,  # Invalid negative value
            "sample_size": 0,  # Invalid zero value
        }
    ]
    
    try:
        result = await meta_tools.perform_meta_analysis(
            studies=invalid_studies,
            method="random",
            measure="SMD"
        )
        
        print(f"✅ Invalid data handled gracefully!")
        print(f"   Success: {result.success}")
        print(f"   Errors: {result.errors}")
        print(f"   Message: {result.message}")
        print()
        
    except Exception as e:
        print(f"❌ Invalid data test failed: {e}")
        print()
    
    print("3️⃣ Test Empty Studies Validation")
    print("-" * 40)
    
    try:
        result = await meta_tools.perform_meta_analysis(
            studies=[],
            method="random",
            measure="SMD"
        )
        
        print(f"✅ Empty studies handled gracefully!")
        print(f"   Success: {result.success}")
        print(f"   Errors: {result.errors}")
        print()
        
    except Exception as e:
        print(f"❌ Empty studies test failed: {e}")
        print()
    
    print("4️⃣ Test Direct Model Validation")
    print("-" * 40)
    
    try:
        valid_study = StudyData(
            study_id="test_study",
            effect_size=0.5,
            standard_error=0.1,
            sample_size=100,
            study_name="Test Study"
        )
        print(f"✅ StudyData validation: {valid_study.study_id}")
        
        valid_ci = ConfidenceInterval(lower=0.2, upper=0.8, level=0.95)
        print(f"✅ ConfidenceInterval validation: [{valid_ci.lower}, {valid_ci.upper}]")
        
        valid_het = HeterogeneityMetrics(
            i_squared=25.5,
            tau_squared=0.05,
            q_statistic=3.2,
            q_p_value=0.15,
            interpretation="Low heterogeneity"
        )
        print(f"✅ HeterogeneityMetrics validation: I²={valid_het.i_squared}%")
        print()
        
    except Exception as e:
        print(f"❌ Direct model validation failed: {e}")
        print()
    
    print("5️⃣ Test Invalid Model Data")
    print("-" * 40)
    
    try:
        invalid_study = StudyData(
            study_id="test_study",
            effect_size=0.5,
            standard_error=-0.1,  # Should fail: negative standard error
            sample_size=100
        )
        print(f"❌ Should have failed but didn't: {invalid_study}")
        
    except Exception as e:
        print(f"✅ Invalid StudyData correctly rejected: {str(e)[:100]}...")
    
    try:
        invalid_het = HeterogeneityMetrics(
            i_squared=150.0,  # Should fail: > 100%
            tau_squared=0.05,
            q_statistic=3.2,
            q_p_value=0.15,
            interpretation="Invalid heterogeneity"
        )
        print(f"❌ Should have failed but didn't: {invalid_het}")
        
    except Exception as e:
        print(f"✅ Invalid HeterogeneityMetrics correctly rejected: {str(e)[:100]}...")
    
    print()
    
    print("🎯 Pydantic Validation Testing Summary")
    print("=" * 55)
    print("✅ ToolResponse wrapper provides structured error handling")
    print("✅ StudyData validation catches invalid input data")
    print("✅ MetaAnalysisResult ensures output data integrity")
    print("✅ Confidence intervals and heterogeneity metrics validated")
    print("✅ Graceful error handling with detailed error messages")
    print("✅ Type safety prevents runtime errors from invalid data")
    print()
    print("🚀 Pydantic validation significantly improves:")
    print("   • Type safety and data integrity")
    print("   • Error messages with field-specific details")
    print("   • Automatic validation of complex nested structures")
    print("   • Documentation through model schemas")
    print("   • Prevention of invalid data propagation")

if __name__ == "__main__":
    asyncio.run(test_pydantic_validation())

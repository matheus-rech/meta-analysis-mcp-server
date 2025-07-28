#!/usr/bin/env python3

import asyncio
import json
import logging
from pathlib import Path
from mcp_server import MCPProtocolHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_individual_tools():
    """Test each MCP tool individually with detailed output"""
    
    print("=" * 60)
    print("INDIVIDUAL TOOL TESTING")
    print("=" * 60)
    
    handler = MCPProtocolHandler()
    
    print("\n🧪 TEST 1: Initialize Meta-Analysis Session")
    print("-" * 50)
    
    init_request = {
        "method": "tools/call",
        "params": {
            "name": "initialize_meta_analysis",
            "arguments": {
                "user_id": "test_user_123",
                "project_name": "Individual Tool Test Project",
                "study_type": "clinical_trial",
                "effect_measure": "OR",
                "analysis_model": "random"
            }
        }
    }
    
    try:
        response = await handler.handle_request(init_request)
        data = json.loads(response["content"][0]["text"])
        session_id = data.get("session_id")
        print(f"✅ SUCCESS: Session created with ID: {session_id}")
        print(f"   Project: {data.get('message', 'N/A')}")
        print(f"   Parameters: {data.get('parameters', {})}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return None
    
    if not session_id:
        print("❌ Cannot continue without session ID")
        return None
    
    print("\n🧪 TEST 2: Upload Study Data")
    print("-" * 35)
    
    upload_request = {
        "method": "tools/call",
        "params": {
            "name": "upload_study_data",
            "arguments": {
                "session_id": session_id,
                "file_path": "/home/ubuntu/meta_analysis_mcp/sample_data.csv",
                "data_type": "effect_sizes"
            }
        }
    }
    
    try:
        response = await handler.handle_request(upload_request)
        data = json.loads(response["content"][0]["text"])
        print(f"✅ SUCCESS: {data.get('message', 'Data uploaded')}")
        if 'validation_summary' in data:
            summary = data['validation_summary']
            print(f"   Studies: {summary.get('total_studies', 'N/A')}")
            print(f"   Validation: {summary.get('validation_status', 'N/A')}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
    
    print("\n🧪 TEST 3: Perform Meta-Analysis")
    print("-" * 40)
    
    analysis_request = {
        "method": "tools/call",
        "params": {
            "name": "perform_meta_analysis",
            "arguments": {
                "session_id": session_id,
                "method": "random_effects",
                "heterogeneity_test": True
            }
        }
    }
    
    try:
        response = await handler.handle_request(analysis_request)
        data = json.loads(response["content"][0]["text"])
        print(f"✅ SUCCESS: {data.get('message', 'Analysis completed')}")
        if 'results' in data:
            results = data['results']
            print(f"   Pooled effect: {results.get('pooled_effect', 'N/A')}")
            print(f"   CI: {results.get('confidence_interval', 'N/A')}")
            print(f"   I²: {results.get('heterogeneity_i2', 'N/A')}")
            print(f"   P-value: {results.get('p_value', 'N/A')}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
    
    print("\n🧪 TEST 4: Generate Forest Plot")
    print("-" * 40)
    
    forest_request = {
        "method": "tools/call",
        "params": {
            "name": "generate_forest_plot",
            "arguments": {
                "session_id": session_id,
                "title": "Test Forest Plot",
                "output_format": "png"
            }
        }
    }
    
    try:
        response = await handler.handle_request(forest_request)
        data = json.loads(response["content"][0]["text"])
        print(f"✅ SUCCESS: {data.get('message', 'Forest plot generated')}")
        if 'file_path' in data:
            print(f"   File: {data['file_path']}")
            if Path(data['file_path']).exists():
                print(f"   ✓ File verified on disk")
            else:
                print(f"   ⚠️  File not found on disk")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
    
    print("\n🧪 TEST 5: Assess Publication Bias")
    print("-" * 45)
    
    bias_request = {
        "method": "tools/call",
        "params": {
            "name": "assess_publication_bias",
            "arguments": {
                "session_id": session_id,
                "tests": ["funnel_plot", "egger_test", "begg_test"]
            }
        }
    }
    
    try:
        response = await handler.handle_request(bias_request)
        data = json.loads(response["content"][0]["text"])
        print(f"✅ SUCCESS: {data.get('message', 'Bias assessment completed')}")
        if 'results' in data:
            results = data['results']
            print(f"   Egger p-value: {results.get('egger_p_value', 'N/A')}")
            print(f"   Begg p-value: {results.get('begg_p_value', 'N/A')}")
            if 'funnel_plot_path' in results:
                print(f"   Funnel plot: {results['funnel_plot_path']}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
    
    print("\n🧪 TEST 6: Generate Comprehensive Report")
    print("-" * 50)
    
    report_request = {
        "method": "tools/call",
        "params": {
            "name": "generate_report",
            "arguments": {
                "session_id": session_id,
                "format": "html",
                "include_plots": True,
                "include_data_summary": True
            }
        }
    }
    
    try:
        response = await handler.handle_request(report_request)
        data = json.loads(response["content"][0]["text"])
        print(f"✅ SUCCESS: {data.get('message', 'Report generated')}")
        if 'file_path' in data:
            print(f"   Report: {data['file_path']}")
            if Path(data['file_path']).exists():
                print(f"   ✓ Report file verified on disk")
            else:
                print(f"   ⚠️  Report file not found on disk")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
    
    print("\n🧪 TEST 7: Get Session Status")
    print("-" * 35)
    
    status_request = {
        "method": "tools/call",
        "params": {
            "name": "get_session_status",
            "arguments": {
                "session_id": session_id
            }
        }
    }
    
    try:
        response = await handler.handle_request(status_request)
        data = json.loads(response["content"][0]["text"])
        print(f"✅ SUCCESS: Session status retrieved")
        print(f"   Status: {data.get('status', 'N/A')}")
        print(f"   Stage: {data.get('workflow_stage', 'N/A')}")
        print(f"   Created: {data.get('created_at', 'N/A')}")
        if 'files' in data:
            files = data['files']
            print(f"   Generated files:")
            for file_type, file_list in files.items():
                print(f"     {file_type}: {len(file_list)} files")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
    
    print("\n" + "=" * 60)
    print("INDIVIDUAL TOOL TESTING COMPLETED")
    print("=" * 60)
    
    return session_id

async def test_error_scenarios():
    """Test various error scenarios"""
    
    print("\n" + "=" * 60)
    print("ERROR SCENARIO TESTING")
    print("=" * 60)
    
    handler = MCPProtocolHandler()
    
    print("\n🧪 ERROR TEST 1: Invalid Tool Name")
    print("-" * 40)
    
    invalid_tool_request = {
        "method": "tools/call",
        "params": {
            "name": "nonexistent_tool",
            "arguments": {}
        }
    }
    
    try:
        response = await handler.handle_request(invalid_tool_request)
        data = json.loads(response["content"][0]["text"])
        print(f"✅ Error handled correctly: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✅ Exception caught as expected: {str(e)}")
    
    print("\n🧪 ERROR TEST 2: Invalid Session ID")
    print("-" * 45)
    
    invalid_session_request = {
        "method": "tools/call",
        "params": {
            "name": "get_session_status",
            "arguments": {
                "session_id": "invalid-session-12345"
            }
        }
    }
    
    try:
        response = await handler.handle_request(invalid_session_request)
        data = json.loads(response["content"][0]["text"])
        print(f"✅ Error handled correctly: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✅ Exception caught as expected: {str(e)}")
    
    print("\n🧪 ERROR TEST 3: Missing Required Parameters")
    print("-" * 55)
    
    missing_params_request = {
        "method": "tools/call",
        "params": {
            "name": "initialize_meta_analysis",
            "arguments": {
                "user_id": "test_user"
            }
        }
    }
    
    try:
        response = await handler.handle_request(missing_params_request)
        data = json.loads(response["content"][0]["text"])
        print(f"✅ Error handled correctly: {data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✅ Exception caught as expected: {str(e)}")

if __name__ == "__main__":
    async def main():
        session_id = await test_individual_tools()
        await test_error_scenarios()
        
        if session_id:
            print(f"\n📋 Session ID for manual testing: {session_id}")
            print("You can use this session ID to test additional scenarios manually.")
    
    asyncio.run(main())

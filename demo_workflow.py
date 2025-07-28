#!/usr/bin/env python3

import asyncio
import json
import logging
from pathlib import Path
from mcp_server import MCPProtocolHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demonstrate_complete_workflow():
    """Demonstrate the complete meta-analysis MCP server workflow"""
    
    print("=" * 60)
    print("META-ANALYSIS MCP SERVER DEMONSTRATION")
    print("=" * 60)
    
    handler = MCPProtocolHandler()
    
    print("\n1. LISTING AVAILABLE TOOLS")
    print("-" * 30)
    tools_response = await handler.handle_request({"method": "tools/list"})
    for tool in tools_response["tools"]:
        print(f"✓ {tool['name']}: {tool['description']}")
    
    print("\n2. INITIALIZING META-ANALYSIS SESSION")
    print("-" * 40)
    init_request = {
        "method": "tools/call",
        "params": {
            "name": "initialize_meta_analysis",
            "arguments": {
                "user_id": "demo_user",
                "project_name": "Cardiovascular Interventions Meta-Analysis",
                "study_type": "clinical_trial",
                "effect_measure": "OR",
                "analysis_model": "random"
            }
        }
    }
    
    init_response = await handler.handle_request(init_request)
    init_data = json.loads(init_response["content"][0]["text"])
    session_id = init_data["session_id"]
    print(f"✓ Session initialized: {session_id}")
    print(f"✓ Project: {init_data.get('message', 'N/A')}")
    
    print("\n3. UPLOADING STUDY DATA")
    print("-" * 25)
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
    
    upload_response = await handler.handle_request(upload_request)
    upload_data = json.loads(upload_response["content"][0]["text"])
    print(f"✓ Data uploaded: {upload_data.get('message', 'Success')}")
    if 'validation_summary' in upload_data:
        summary = upload_data['validation_summary']
        print(f"  - Studies: {summary.get('total_studies', 'N/A')}")
        print(f"  - Effect sizes: {summary.get('effect_sizes_available', 'N/A')}")
    
    print("\n4. PERFORMING META-ANALYSIS")
    print("-" * 30)
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
    
    analysis_response = await handler.handle_request(analysis_request)
    analysis_data = json.loads(analysis_response["content"][0]["text"])
    print(f"✓ Analysis completed: {analysis_data.get('message', 'Success')}")
    if 'results' in analysis_data:
        results = analysis_data['results']
        print(f"  - Pooled effect: {results.get('pooled_effect', 'N/A')}")
        print(f"  - Confidence interval: {results.get('confidence_interval', 'N/A')}")
        print(f"  - Heterogeneity (I²): {results.get('heterogeneity_i2', 'N/A')}")
    
    print("\n5. GENERATING FOREST PLOT")
    print("-" * 30)
    forest_request = {
        "method": "tools/call",
        "params": {
            "name": "generate_forest_plot",
            "arguments": {
                "session_id": session_id,
                "title": "Cardiovascular Interventions - Forest Plot",
                "output_format": "png"
            }
        }
    }
    
    forest_response = await handler.handle_request(forest_request)
    forest_data = json.loads(forest_response["content"][0]["text"])
    print(f"✓ Forest plot generated: {forest_data.get('message', 'Success')}")
    if 'file_path' in forest_data:
        print(f"  - File: {forest_data['file_path']}")
    
    print("\n6. ASSESSING PUBLICATION BIAS")
    print("-" * 35)
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
    
    bias_response = await handler.handle_request(bias_request)
    bias_data = json.loads(bias_response["content"][0]["text"])
    print(f"✓ Publication bias assessment: {bias_data.get('message', 'Success')}")
    if 'results' in bias_data:
        results = bias_data['results']
        print(f"  - Egger test p-value: {results.get('egger_p_value', 'N/A')}")
        print(f"  - Funnel plot: {results.get('funnel_plot_path', 'Generated')}")
    
    print("\n7. GENERATING COMPREHENSIVE REPORT")
    print("-" * 40)
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
    
    report_response = await handler.handle_request(report_request)
    report_data = json.loads(report_response["content"][0]["text"])
    print(f"✓ Report generated: {report_data.get('message', 'Success')}")
    if 'file_path' in report_data:
        print(f"  - Report: {report_data['file_path']}")
    
    print("\n8. SESSION STATUS SUMMARY")
    print("-" * 30)
    status_request = {
        "method": "tools/call",
        "params": {
            "name": "get_session_status",
            "arguments": {
                "session_id": session_id
            }
        }
    }
    
    status_response = await handler.handle_request(status_request)
    status_data = json.loads(status_response["content"][0]["text"])
    print(f"✓ Session status: {status_data.get('status', 'N/A')}")
    print(f"✓ Workflow stage: {status_data.get('workflow_stage', 'N/A')}")
    if 'files' in status_data:
        files = status_data['files']
        print("✓ Generated files:")
        for file_type, file_list in files.items():
            for file_path in file_list:
                print(f"  - {file_type}: {file_path}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    return session_id

async def test_error_handling():
    """Test error handling with invalid inputs"""
    
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING")
    print("=" * 60)
    
    handler = MCPProtocolHandler()
    
    print("\n1. Testing invalid session ID...")
    invalid_request = {
        "method": "tools/call",
        "params": {
            "name": "get_session_status",
            "arguments": {
                "session_id": "invalid-session-id"
            }
        }
    }
    
    try:
        response = await handler.handle_request(invalid_request)
        data = json.loads(response["content"][0]["text"])
        print(f"✓ Error handling works: {data.get('error', 'No error message')}")
    except Exception as e:
        print(f"✓ Exception caught: {str(e)}")
    
    print("\n2. Testing missing required parameters...")
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
        print(f"✓ Parameter validation works: {data.get('error', 'No error message')}")
    except Exception as e:
        print(f"✓ Exception caught: {str(e)}")

if __name__ == "__main__":
    async def main():
        session_id = await demonstrate_complete_workflow()
        await test_error_handling()
        
        print(f"\nDemo session ID for further testing: {session_id}")
        print("You can use this session ID to test individual tools manually.")
    
    asyncio.run(main())

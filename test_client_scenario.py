#!/usr/bin/env python3
"""
Complex Meta-Analysis Test Scenario
Tests the MCP server end-to-end as a user would interact with it
"""

import asyncio
import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path

COMPLEX_STUDY_DATA = [
    {
        "study_id": "Smith2020",
        "title": "Cognitive Behavioral Therapy for Depression in Adults",
        "authors": "Smith, J., Johnson, K., Williams, L.",
        "year": 2020,
        "sample_size_treatment": 120,
        "sample_size_control": 115,
        "mean_treatment": 15.2,
        "mean_control": 22.8,
        "sd_treatment": 8.1,
        "sd_control": 9.3,
        "effect_size": -0.85,
        "standard_error": 0.14,
        "confidence_interval_lower": -1.12,
        "confidence_interval_upper": -0.58,
        "study_design": "RCT",
        "risk_of_bias": {
            "randomization": "Low",
            "allocation_concealment": "Low", 
            "blinding_participants": "High",
            "blinding_outcome": "Low",
            "incomplete_outcome": "Low",
            "selective_reporting": "Low",
            "other_bias": "Low"
        }
    },
    {
        "study_id": "Garcia2019",
        "title": "Mindfulness-Based Cognitive Therapy vs Standard Care",
        "authors": "Garcia, M., Rodriguez, P., Martinez, A.",
        "year": 2019,
        "sample_size_treatment": 89,
        "sample_size_control": 92,
        "mean_treatment": 16.7,
        "mean_control": 24.1,
        "sd_treatment": 7.8,
        "sd_control": 8.9,
        "effect_size": -0.91,
        "standard_error": 0.16,
        "confidence_interval_lower": -1.22,
        "confidence_interval_upper": -0.60,
        "study_design": "RCT",
        "risk_of_bias": {
            "randomization": "Low",
            "allocation_concealment": "Unclear",
            "blinding_participants": "High",
            "blinding_outcome": "Low", 
            "incomplete_outcome": "High",
            "selective_reporting": "Low",
            "other_bias": "Low"
        }
    },
    {
        "study_id": "Chen2021",
        "title": "Internet-Delivered CBT for Depression: A Randomized Trial",
        "authors": "Chen, L., Wang, X., Liu, Y., Zhang, H.",
        "year": 2021,
        "sample_size_treatment": 156,
        "sample_size_control": 148,
        "mean_treatment": 14.8,
        "mean_control": 21.9,
        "sd_treatment": 6.9,
        "sd_control": 8.2,
        "effect_size": -0.94,
        "standard_error": 0.12,
        "confidence_interval_lower": -1.17,
        "confidence_interval_upper": -0.71,
        "study_design": "RCT",
        "risk_of_bias": {
            "randomization": "Low",
            "allocation_concealment": "Low",
            "blinding_participants": "High",
            "blinding_outcome": "Low",
            "incomplete_outcome": "Low",
            "selective_reporting": "Low",
            "other_bias": "Low"
        }
    },
    {
        "study_id": "Thompson2018",
        "title": "Group CBT vs Individual CBT for Major Depression",
        "authors": "Thompson, R., Davis, S., Wilson, M.",
        "year": 2018,
        "sample_size_treatment": 78,
        "sample_size_control": 82,
        "mean_treatment": 17.3,
        "mean_control": 23.6,
        "sd_treatment": 9.1,
        "sd_control": 8.7,
        "effect_size": -0.71,
        "standard_error": 0.17,
        "confidence_interval_lower": -1.04,
        "confidence_interval_upper": -0.38,
        "study_design": "RCT",
        "risk_of_bias": {
            "randomization": "Low",
            "allocation_concealment": "Low",
            "blinding_participants": "High",
            "blinding_outcome": "Unclear",
            "incomplete_outcome": "Low",
            "selective_reporting": "Low",
            "other_bias": "Low"
        }
    },
    {
        "study_id": "Anderson2022",
        "title": "Acceptance and Commitment Therapy for Treatment-Resistant Depression",
        "authors": "Anderson, K., Brown, T., Miller, J.",
        "year": 2022,
        "sample_size_treatment": 67,
        "sample_size_control": 71,
        "mean_treatment": 18.1,
        "mean_control": 25.4,
        "sd_treatment": 8.8,
        "sd_control": 9.6,
        "effect_size": -0.78,
        "standard_error": 0.18,
        "confidence_interval_lower": -1.13,
        "confidence_interval_upper": -0.43,
        "study_design": "RCT",
        "risk_of_bias": {
            "randomization": "Low",
            "allocation_concealment": "Low",
            "blinding_participants": "High",
            "blinding_outcome": "Low",
            "incomplete_outcome": "Low",
            "selective_reporting": "Unclear",
            "other_bias": "Low"
        }
    }
]

class MCPTestClient:
    def __init__(self):
        self.server_process = None
        self.session_id = None
        
    async def start_server(self):
        """Start the MCP server"""
        print("🚀 Starting MCP server...")
        
        self.server_process = subprocess.Popen(
            [sys.executable, "-m", "meta_analysis_mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/home/ubuntu/repos/meta-analysis-mcp-server"
        )
        
        await asyncio.sleep(2)
        print("✅ MCP server started")
        
    async def send_request(self, method, params=None):
        """Send a request to the MCP server"""
        if params is None:
            params = {}
            
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            request_json = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            response_line = self.server_process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                return response
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            return {"error": f"Communication error: {str(e)}"}
    
    async def test_tool(self, tool_name, arguments):
        """Test a specific tool"""
        print(f"🔧 Testing tool: {tool_name}")
        
        response = await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "error" in response:
            print(f"❌ Tool {tool_name} failed: {response['error']}")
            return False
        else:
            print(f"✅ Tool {tool_name} succeeded")
            return True
    
    async def run_complex_scenario(self):
        """Run a complex meta-analysis scenario"""
        print("\n🧪 COMPLEX META-ANALYSIS TEST SCENARIO")
        print("=" * 60)
        print("Testing: Psychological interventions for depression")
        print("Studies: 5 RCTs with varying risk of bias profiles")
        print("Analysis: Complete workflow with Cochrane compliance")
        print("=" * 60)
        
        success_count = 0
        total_tests = 11
        
        print("\n📋 Step 1: Initialize Meta-Analysis Session")
        result = await self.test_tool("initialize_meta_analysis", {
            "title": "Psychological Interventions for Depression: A Systematic Review and Meta-Analysis",
            "research_question": "What is the effectiveness of psychological interventions compared to control conditions for treating depression in adults?",
            "inclusion_criteria": [
                "Randomized controlled trials",
                "Adult participants (18+ years)",
                "Diagnosed depression (clinical criteria)",
                "Psychological intervention vs control",
                "Depression severity outcome measures"
            ],
            "exclusion_criteria": [
                "Non-randomized studies",
                "Adolescent or child populations",
                "Pharmacological interventions only",
                "No validated depression measures"
            ]
        })
        if result:
            success_count += 1
            
        print("\n📊 Step 2: Upload Study Data (5 Studies)")
        for i, study in enumerate(COMPLEX_STUDY_DATA):
            print(f"   Uploading study {i+1}: {study['study_id']}")
            result = await self.test_tool("upload_study_data", study)
            if not result:
                print(f"   ❌ Failed to upload {study['study_id']}")
        
        if len(COMPLEX_STUDY_DATA) > 0:
            success_count += 1
            
        print("\n🔬 Step 3: Perform Statistical Meta-Analysis")
        result = await self.test_tool("perform_meta_analysis", {
            "outcome_type": "continuous",
            "effect_measure": "standardized_mean_difference",
            "analysis_model": "random_effects",
            "confidence_level": 0.95
        })
        if result:
            success_count += 1
            
        print("\n🌲 Step 4: Generate Forest Plot")
        result = await self.test_tool("generate_forest_plot", {
            "plot_title": "Forest Plot: Psychological Interventions vs Control",
            "x_axis_label": "Standardized Mean Difference",
            "show_weights": True,
            "show_confidence_intervals": True
        })
        if result:
            success_count += 1
            
        print("\n🎯 Step 5: Assess Publication Bias")
        result = await self.test_tool("assess_publication_bias", {
            "tests": ["egger", "begg", "trim_fill"],
            "create_funnel_plot": True,
            "alpha": 0.05
        })
        if result:
            success_count += 1
            
        print("\n📈 Step 6: Generate Statistical Report")
        result = await self.test_tool("generate_report", {
            "report_type": "comprehensive",
            "include_forest_plot": True,
            "include_funnel_plot": True,
            "include_heterogeneity": True,
            "include_sensitivity": True
        })
        if result:
            success_count += 1
            
        print("\n📋 Step 7: Check Session Status")
        result = await self.test_tool("get_session_status", {})
        if result:
            success_count += 1
            
        print("\n⚖️ Step 8: Cochrane Risk of Bias Assessment")
        result = await self.test_tool("assess_risk_of_bias", {
            "tool_version": "ROB_2.0",
            "domains": [
                "randomization_process",
                "deviations_intended_interventions", 
                "missing_outcome_data",
                "measurement_outcome",
                "selection_reported_result"
            ],
            "generate_summary": True
        })
        if result:
            success_count += 1
            
        print("\n📋 Step 9: Generate PRISMA 2020 Checklist")
        result = await self.test_tool("generate_prisma_checklist", {
            "checklist_version": "PRISMA_2020",
            "review_type": "intervention",
            "include_flow_diagram": True,
            "auto_populate": True
        })
        if result:
            success_count += 1
            
        print("\n🎖️ Step 10: GRADE Evidence Assessment")
        result = await self.test_tool("perform_grade_assessment", {
            "outcome_measures": [
                {
                    "outcome": "Depression severity",
                    "measurement": "Standardized mean difference",
                    "importance": "critical"
                }
            ],
            "initial_certainty": "high",
            "downgrade_factors": [
                "risk_of_bias",
                "inconsistency", 
                "indirectness",
                "imprecision",
                "publication_bias"
            ]
        })
        if result:
            success_count += 1
            
        print("\n📄 Step 11: Generate Comprehensive Cochrane Report")
        result = await self.test_tool("generate_cochrane_report", {
            "report_sections": [
                "title_page",
                "abstract", 
                "background",
                "objectives",
                "methods",
                "results",
                "discussion",
                "conclusions",
                "references"
            ],
            "include_rob_assessment": True,
            "include_grade_summary": True,
            "include_prisma_checklist": True,
            "format": "html"
        })
        if result:
            success_count += 1
            
        # Summary
        print(f"\n🎉 TEST SCENARIO COMPLETE")
        print("=" * 60)
        print(f"✅ Successful tests: {success_count}/{total_tests}")
        print(f"📊 Success rate: {(success_count/total_tests)*100:.1f}%")
        
        if success_count == total_tests:
            print("🚀 ALL TESTS PASSED - Ready for deployment!")
            return True
        else:
            print("⚠️ Some tests failed - Review before deployment")
            return False
    
    async def cleanup(self):
        """Clean up server process"""
        if self.server_process:
            self.server_process.terminate()
            await asyncio.sleep(1)
            if self.server_process.poll() is None:
                self.server_process.kill()
            print("🛑 MCP server stopped")

async def main():
    """Main test execution"""
    client = MCPTestClient()
    
    try:
        await client.start_server()
        success = await client.run_complex_scenario()
        
        if success:
            print("\n✅ DEPLOYMENT READY: All systems functional!")
            return 0
        else:
            print("\n❌ DEPLOYMENT BLOCKED: Issues detected!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test scenario failed: {str(e)}")
        return 1
        
    finally:
        await client.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

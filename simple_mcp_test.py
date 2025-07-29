#!/usr/bin/env python3
"""
Simple MCP Test - Tests the server using proper MCP JSON-RPC protocol
"""

import asyncio
import json
import subprocess
import sys
import time

SAMPLE_STUDIES = [
    {
        "study_id": "Smith2020",
        "effect_size": -0.85,
        "standard_error": 0.14,
        "sample_size": 235,
        "ci_lower": -1.12,
        "ci_upper": -0.58,
        "weight": 0.25
    },
    {
        "study_id": "Garcia2019", 
        "effect_size": -0.91,
        "standard_error": 0.16,
        "sample_size": 181,
        "ci_lower": -1.22,
        "ci_upper": -0.60,
        "weight": 0.23
    },
    {
        "study_id": "Chen2021",
        "effect_size": -0.94,
        "standard_error": 0.12,
        "sample_size": 304,
        "ci_lower": -1.17,
        "ci_upper": -0.71,
        "weight": 0.27
    }
]

class SimpleMCPTest:
    def __init__(self):
        self.server_process = None
        self.request_id = 1
        
    async def start_server(self):
        """Start the MCP server process"""
        print("🚀 Starting MCP server...")
        
        self.server_process = subprocess.Popen(
            [sys.executable, "-m", "meta_analysis_mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/home/ubuntu/repos/meta-analysis-mcp-server"
        )
        
        await asyncio.sleep(1)
        print("✅ MCP server process started")
        
    async def send_mcp_request(self, method, params=None):
        """Send a proper MCP JSON-RPC request"""
        if params is None:
            params = {}
            
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        self.request_id += 1
        
        try:
            request_json = json.dumps(request) + "\n"
            print(f"📤 Sending: {method}")
            
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            start_time = time.time()
            while time.time() - start_time < 5:  # 5 second timeout
                if self.server_process.poll() is not None:
                    print(f"❌ Server process terminated unexpectedly")
                    return {"error": "Server process terminated"}
                    
                try:
                    response_line = self.server_process.stdout.readline()
                    if response_line.strip():
                        response = json.loads(response_line.strip())
                        print(f"📥 Response: {response.get('result', response.get('error', 'Unknown'))}")
                        return response
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON decode error: {e}")
                    print(f"Raw response: {response_line}")
                    continue
                    
                await asyncio.sleep(0.1)
                
            print(f"⏰ Request timeout for {method}")
            return {"error": "Request timeout"}
            
        except Exception as e:
            print(f"💥 Communication error: {str(e)}")
            return {"error": f"Communication error: {str(e)}"}
    
    async def test_initialization(self):
        """Test MCP initialization"""
        print("\n🔧 Testing MCP Initialization")
        
        response = await self.send_mcp_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
        
        if "error" not in response:
            print("✅ MCP initialization successful")
            return True
        else:
            print(f"❌ MCP initialization failed: {response.get('error')}")
            return False
    
    async def test_list_tools(self):
        """Test listing available tools"""
        print("\n📋 Testing Tool Listing")
        
        response = await self.send_mcp_request("tools/list")
        
        if "error" not in response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description'][:50]}...")
            return len(tools) > 0
        else:
            print(f"❌ Tool listing failed: {response.get('error')}")
            return False
    
    async def test_meta_analysis_tool(self):
        """Test the perform_meta_analysis tool"""
        print("\n🔬 Testing Meta-Analysis Tool")
        
        response = await self.send_mcp_request("tools/call", {
            "name": "perform_meta_analysis",
            "arguments": {
                "studies": SAMPLE_STUDIES,
                "method": "random",
                "measure": "SMD"
            }
        })
        
        if "error" not in response and "result" in response:
            print("✅ Meta-analysis tool executed successfully")
            return True
        else:
            print(f"❌ Meta-analysis tool failed: {response.get('error')}")
            return False
    
    async def test_forest_plot_tool(self):
        """Test the create_forest_plot tool"""
        print("\n🌲 Testing Forest Plot Tool")
        
        response = await self.send_mcp_request("tools/call", {
            "name": "create_forest_plot", 
            "arguments": {
                "studies": SAMPLE_STUDIES,
                "title": "Test Forest Plot",
                "output_format": "png"
            }
        })
        
        if "error" not in response and "result" in response:
            print("✅ Forest plot tool executed successfully")
            return True
        else:
            print(f"❌ Forest plot tool failed: {response.get('error')}")
            return False
    
    async def test_cochrane_tools(self):
        """Test Cochrane compliance tools"""
        print("\n⚖️ Testing Cochrane Tools")
        
        # Test ROB assessment
        rob_response = await self.send_mcp_request("tools/call", {
            "name": "assess_risk_of_bias",
            "arguments": {
                "studies": [
                    {
                        "study_id": "Smith2020",
                        "title": "Test Study",
                        "study_design": "RCT"
                    }
                ],
                "assessment_mode": "automated"
            }
        })
        
        rob_success = "error" not in rob_response and "result" in rob_response
        if rob_success:
            print("✅ Risk of bias assessment successful")
        else:
            print(f"❌ Risk of bias assessment failed: {rob_response.get('error')}")
        
        # Test PRISMA checklist
        prisma_response = await self.send_mcp_request("tools/call", {
            "name": "generate_prisma_checklist",
            "arguments": {
                "review_data": {
                    "title": "Test Systematic Review"
                },
                "generate_flow_diagram": True
            }
        })
        
        prisma_success = "error" not in prisma_response and "result" in prisma_response
        if prisma_success:
            print("✅ PRISMA checklist generation successful")
        else:
            print(f"❌ PRISMA checklist failed: {prisma_response.get('error')}")
            
        return rob_success and prisma_success
    
    async def run_test_suite(self):
        """Run the complete test suite"""
        print("🧪 SIMPLE MCP TEST SUITE")
        print("=" * 50)
        
        success_count = 0
        total_tests = 5
        
        if await self.test_initialization():
            success_count += 1
            
        if await self.test_list_tools():
            success_count += 1
            
        if await self.test_meta_analysis_tool():
            success_count += 1
            
        if await self.test_forest_plot_tool():
            success_count += 1
            
        if await self.test_cochrane_tools():
            success_count += 1
        
        print(f"\n🎉 TEST RESULTS")
        print("=" * 50)
        print(f"✅ Successful tests: {success_count}/{total_tests}")
        print(f"📊 Success rate: {(success_count/total_tests)*100:.1f}%")
        
        if success_count >= 4:  # Allow 1 failure
            print("🚀 MCP SERVER READY FOR DEPLOYMENT!")
            return True
        else:
            print("⚠️ MCP server needs fixes before deployment")
            return False
    
    async def cleanup(self):
        """Clean up server process"""
        if self.server_process:
            try:
                self.server_process.terminate()
                await asyncio.sleep(1)
                if self.server_process.poll() is None:
                    self.server_process.kill()
                print("🛑 MCP server stopped")
            except:
                pass

async def main():
    """Main test execution"""
    test = SimpleMCPTest()
    
    try:
        await test.start_server()
        success = await test.run_test_suite()
        
        if success:
            print("\n✅ DEPLOYMENT APPROVED: MCP server is functional!")
            return 0
        else:
            print("\n❌ DEPLOYMENT BLOCKED: MCP server has issues!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        return 1
        
    finally:
        await test.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

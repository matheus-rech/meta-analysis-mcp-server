#!/usr/bin/env python3
"""
Debug script to test MCP server startup and basic functionality
"""

import sys
import traceback
import asyncio

def test_imports():
    """Test all imports to identify any import errors"""
    print("🔍 Testing imports...")
    
    try:
        print("  - Testing meta_analysis_mcp_server import...")
        import meta_analysis_mcp_server
        print("  ✅ meta_analysis_mcp_server imported successfully")
        
        print("  - Testing server module import...")
        from meta_analysis_mcp_server import server
        print("  ✅ server module imported successfully")
        
        print("  - Testing MetaAnalysisServer class...")
        server_instance = server.MetaAnalysisServer()
        print("  ✅ MetaAnalysisServer instantiated successfully")
        
        print("  - Testing tool modules...")
        from meta_analysis_mcp_server.tools import meta_analysis
        from meta_analysis_mcp_server.tools import cochrane_compliance
        print("  ✅ Tool modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import error: {str(e)}")
        print(f"  📋 Traceback:")
        traceback.print_exc()
        return False

def test_server_creation():
    """Test server creation and basic setup"""
    print("\n🏗️ Testing server creation...")
    
    try:
        from meta_analysis_mcp_server.server import MetaAnalysisServer
        
        print("  - Creating server instance...")
        server = MetaAnalysisServer()
        print("  ✅ Server instance created successfully")
        
        print("  - Testing server.server attribute...")
        if hasattr(server, 'server'):
            print("  ✅ Server has 'server' attribute")
        else:
            print("  ❌ Server missing 'server' attribute")
            
        print("  - Testing meta_tools attribute...")
        if hasattr(server, 'meta_tools'):
            print("  ✅ Server has 'meta_tools' attribute")
        else:
            print("  ❌ Server missing 'meta_tools' attribute")
            
        print("  - Testing cochrane_tools attribute...")
        if hasattr(server, 'cochrane_tools'):
            print("  ✅ Server has 'cochrane_tools' attribute")
        else:
            print("  ❌ Server missing 'cochrane_tools' attribute")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Server creation error: {str(e)}")
        print(f"  📋 Traceback:")
        traceback.print_exc()
        return False

async def test_tool_listing():
    """Test tool listing functionality"""
    print("\n📋 Testing tool listing...")
    
    try:
        from meta_analysis_mcp_server.server import MetaAnalysisServer
        
        server = MetaAnalysisServer()
        
        print("  - Testing list_tools method...")
        tools_result = await server.list_tools()
        print(f"  ✅ list_tools returned {len(tools_result.tools)} tools")
        
        for tool in tools_result.tools:
            print(f"    - {tool.name}: {tool.description[:50]}...")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Tool listing error: {str(e)}")
        print(f"  📋 Traceback:")
        traceback.print_exc()
        return False

async def test_simple_tool_call():
    """Test a simple tool call"""
    print("\n🔧 Testing simple tool call...")
    
    try:
        from meta_analysis_mcp_server.server import MetaAnalysisServer
        from mcp.types import CallToolRequest
        
        server = MetaAnalysisServer()
        
        print("  - Testing get_session_status tool call...")
        
        request = CallToolRequest(
            name="get_session_status",
            arguments={}
        )
        
        result = await server.call_tool(request)
        print(f"  ✅ get_session_status call succeeded")
        print(f"    Result type: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Tool call error: {str(e)}")
        print(f"  📋 Traceback:")
        traceback.print_exc()
        return False

async def main():
    """Main debug execution"""
    print("🐛 MCP SERVER DEBUG SCRIPT")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    if test_imports():
        success_count += 1
        
    if test_server_creation():
        success_count += 1
        
    if await test_tool_listing():
        success_count += 1
        
    if await test_simple_tool_call():
        success_count += 1
    
    print(f"\n🎉 DEBUG RESULTS")
    print("=" * 50)
    print(f"✅ Successful tests: {success_count}/{total_tests}")
    print(f"📊 Success rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🚀 All debug tests passed - Server should work!")
        return 0
    else:
        print("⚠️ Some debug tests failed - Server has issues")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

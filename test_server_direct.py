#!/usr/bin/env python3
"""
Test server directly to identify crash causes
"""

import sys
import traceback

def test_server_import_and_run():
    """Test server import and basic functionality"""
    print("🔍 Testing server import and basic functionality...")
    
    try:
        print("  - Importing server module...")
        from meta_analysis_mcp_server.server import MetaAnalysisServer, main
        print("  ✅ Server module imported successfully")
        
        print("  - Creating server instance...")
        server = MetaAnalysisServer()
        print("  ✅ Server instance created successfully")
        
        print("  - Testing server attributes...")
        print(f"    - server.server: {type(server.server)}")
        print(f"    - server.meta_tools: {type(server.meta_tools)}")
        print(f"    - server.cochrane_tools: {type(server.cochrane_tools)}")
        
        print("  - Testing MCP imports...")
        import mcp.server.stdio
        import mcp.types as types
        print("  ✅ MCP imports successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        print("  📋 Traceback:")
        traceback.print_exc()
        return False

def test_tool_modules():
    """Test tool module imports"""
    print("\n🔧 Testing tool modules...")
    
    try:
        print("  - Importing meta_analysis tools...")
        from meta_analysis_mcp_server.tools.meta_analysis import MetaAnalysisTools
        meta_tools = MetaAnalysisTools()
        print("  ✅ MetaAnalysisTools imported and instantiated")
        
        print("  - Importing cochrane_compliance tools...")
        from meta_analysis_mcp_server.tools.cochrane_compliance import CochraneComplianceTools
        cochrane_tools = CochraneComplianceTools()
        print("  ✅ CochraneComplianceTools imported and instantiated")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        print("  📋 Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🐛 DIRECT SERVER TEST")
    print("=" * 30)
    
    success_count = 0
    
    if test_server_import_and_run():
        success_count += 1
        
    if test_tool_modules():
        success_count += 1
    
    print(f"\n🎉 Results: {success_count}/2 tests passed")
    
    if success_count == 2:
        print("✅ Server components work - issue may be in MCP protocol handling")
    else:
        print("❌ Server has fundamental issues")

#!/usr/bin/env python3
"""
Test script to verify deployment readiness for the meta-analysis MCP server.
This checks if the application can start properly and all dependencies are available.
"""

import sys
import subprocess
import importlib.util

def test_import(module_name):
    """Test if a module can be imported successfully."""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False, f"Module {module_name} not found"
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, f"Module {module_name} imported successfully"
    except Exception as e:
        return False, f"Failed to import {module_name}: {str(e)}"

def test_server_import():
    """Test if the MCP server can be imported."""
    try:
        from meta_analysis_mcp_server.server import MetaAnalysisServer, main
        server = MetaAnalysisServer()
        return True, "MCP server imported and instantiated successfully"
    except Exception as e:
        return False, f"Failed to import MCP server: {str(e)}"

def test_r_availability():
    """Test if R is available and can run basic commands."""
    try:
        result = subprocess.run(['R', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, "R is available and working"
        else:
            return False, f"R command failed: {result.stderr}"
    except FileNotFoundError:
        return False, "R is not installed or not in PATH"
    except subprocess.TimeoutExpired:
        return False, "R command timed out"
    except Exception as e:
        return False, f"Error testing R: {str(e)}"

def main():
    """Run all deployment readiness tests."""
    print("=== Meta-Analysis MCP Server Deployment Readiness Test ===\n")
    
    tests = [
        ("Core Dependencies", [
            ("mcp", test_import),
            ("fastapi", test_import),
            ("uvicorn", test_import),
            ("pydantic", test_import),
            ("jinja2", test_import),
        ]),
        ("Analysis Dependencies", [
            ("pandas", test_import),
            ("numpy", test_import),
            ("scipy", test_import),
            ("statsmodels", test_import),
        ]),
        ("Visualization Dependencies", [
            ("matplotlib", test_import),
            ("seaborn", test_import),
        ]),
        ("Server Components", [
            ("MCP Server", test_server_import),
        ]),
        ("External Tools", [
            ("R Environment", test_r_availability),
        ])
    ]
    
    all_passed = True
    
    for category, category_tests in tests:
        print(f"--- {category} ---")
        category_passed = True
        
        for test_name, test_func in category_tests:
            if test_func == test_import:
                success, message = test_func(test_name.lower())
            else:
                success, message = test_func()
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name} - {message}")
            
            if not success:
                category_passed = False
                all_passed = False
        
        print()
    
    print("=== Summary ===")
    if all_passed:
        print("✅ All tests passed! The application is ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please review the issues above before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

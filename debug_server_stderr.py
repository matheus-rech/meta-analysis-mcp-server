#!/usr/bin/env python3
"""
Debug script to capture server stderr and identify crash cause
"""

import subprocess
import sys
import time

def test_server_startup():
    """Test server startup and capture stderr"""
    print("🔍 Testing server startup with stderr capture...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "meta_analysis_mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/home/ubuntu/repos/meta-analysis-mcp-server"
        )
        
        print("✅ Server process started, waiting for output...")
        
        time.sleep(2)
        
        if process.poll() is not None:
            print(f"❌ Server process terminated with return code: {process.returncode}")
            
            stderr_output = process.stderr.read()
            if stderr_output:
                print("📋 STDERR OUTPUT:")
                print(stderr_output)
            else:
                print("📋 No stderr output captured")
                
            stdout_output = process.stdout.read()
            if stdout_output:
                print("📋 STDOUT OUTPUT:")
                print(stdout_output)
            else:
                print("📋 No stdout output captured")
                
        else:
            print("✅ Server process is still running")
            
            print("📤 Sending test request...")
            try:
                process.stdin.write('{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}\n')
                process.stdin.flush()
                
                time.sleep(2)
                
                if process.poll() is not None:
                    print(f"❌ Server crashed after request with return code: {process.returncode}")
                    
                    stderr_output = process.stderr.read()
                    if stderr_output:
                        print("📋 STDERR OUTPUT AFTER REQUEST:")
                        print(stderr_output)
                        
                else:
                    print("✅ Server handled request without crashing")
                    
            except Exception as e:
                print(f"💥 Error sending request: {e}")
        
        if process.poll() is None:
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
                
    except Exception as e:
        print(f"💥 Failed to start server: {e}")

def test_direct_import():
    """Test direct import to catch import errors"""
    print("\n🔍 Testing direct import...")
    
    try:
        print("  - Importing meta_analysis_mcp_server...")
        import meta_analysis_mcp_server
        print("  ✅ meta_analysis_mcp_server imported successfully")
        
        print("  - Testing main function...")
        print("  ✅ main function accessible")
        
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🐛 SERVER STDERR DEBUG")
    print("=" * 40)
    
    test_direct_import()
    test_server_startup()

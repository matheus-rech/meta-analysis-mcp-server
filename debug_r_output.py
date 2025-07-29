#!/usr/bin/env python3
"""
Debug R script output to identify why genuine results aren't being returned
"""

import subprocess
import json

def debug_r_meta_analysis():
    """Debug R meta-analysis function output directly"""
    print("🔍 Debugging R meta-analysis output...")
    
    test_data = {
        "effect_sizes": [-0.5, -0.3, -0.7, -0.4, -0.6],
        "standard_errors": [0.15, 0.12, 0.18, 0.14, 0.16],
        "study_ids": ["Study_A", "Study_B", "Study_C", "Study_D", "Study_E"],
        "method": "REML"
    }
    
    try:
        result = subprocess.run(
            ["Rscript", "r_scripts/meta_analysis.R", "perform_meta_analysis", json.dumps(test_data)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/home/ubuntu/repos/meta-analysis-mcp-server"
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: '{result.stdout}'")
        print(f"STDERR: '{result.stderr}'")
        
        if result.stdout.strip():
            try:
                parsed = json.loads(result.stdout.strip())
                print(f"Parsed JSON: {parsed}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw output: {repr(result.stdout)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_simple_r_command():
    """Test simple R command to verify R is working"""
    print("\n🧮 Testing simple R computation...")
    
    simple_r_code = '''
    result <- list(test_value = 42, computation = 2 + 2)
    cat(jsonlite::toJSON(result, auto_unbox = TRUE))
    '''
    
    try:
        result = subprocess.run(
            ["Rscript", "-e", simple_r_code],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"Simple R test - Return code: {result.returncode}")
        print(f"Simple R test - STDOUT: '{result.stdout}'")
        print(f"Simple R test - STDERR: '{result.stderr}'")
        
    except Exception as e:
        print(f"Simple R test error: {e}")

if __name__ == "__main__":
    print("🐛 R OUTPUT DEBUG")
    print("=" * 30)
    
    test_simple_r_command()
    debug_r_meta_analysis()

#!/usr/bin/env python3
"""Test script to verify R integration status in meta-analysis tools."""

import sys
import os
import json
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from meta_analysis_mcp_server.tools.meta_analysis import run_r_script, perform_meta_analysis

def test_r_script_direct():
    """Test direct R script execution."""
    print("=== Testing Direct R Script Execution ===")
    
    test_data = {
        "studies": [
            {"study_id": "Study_1", "effect_size": 0.5, "standard_error": 0.1, "sample_size": 100},
            {"study_id": "Study_2", "effect_size": 0.3, "standard_error": 0.15, "sample_size": 80},
            {"study_id": "Study_3", "effect_size": 0.7, "standard_error": 0.12, "sample_size": 120},
            {"study_id": "Study_4", "effect_size": 0.2, "standard_error": 0.18, "sample_size": 60}
        ]
    }
    
    try:
        print("Calling run_r_script with perform_meta_analysis function...")
        r_result = run_r_script("perform_meta_analysis", test_data)
        print(f"R Script Result: {json.dumps(r_result, indent=2)}")
        return True
    except Exception as e:
        print(f"R Script Execution Failed: {e}")
        return False

def test_python_meta_analysis():
    """Test Python meta-analysis function."""
    print("\n=== Testing Python Meta-Analysis Function ===")
    
    # Test data
    studies_data = [
        {"study_id": "Study_1", "effect_size": 0.5, "standard_error": 0.1, "sample_size": 100},
        {"study_id": "Study_2", "effect_size": 0.3, "standard_error": 0.15, "sample_size": 80},
        {"study_id": "Study_3", "effect_size": 0.7, "standard_error": 0.12, "sample_size": 120},
        {"study_id": "Study_4", "effect_size": 0.2, "standard_error": 0.18, "sample_size": 60}
    ]
    
    try:
        print("Calling Python perform_meta_analysis function...")
        python_result = perform_meta_analysis(studies_data)
        print(f"Python Result Type: {type(python_result)}")
        
        if hasattr(python_result, 'model_dump'):
            result_dict = python_result.model_dump()
        elif hasattr(python_result, '__dict__'):
            result_dict = python_result.__dict__
        else:
            result_dict = python_result
            
        print(f"Python Result: {json.dumps(result_dict, indent=2, default=str)}")
        return True
    except Exception as e:
        print(f"Python Meta-Analysis Failed: {e}")
        return False

def check_r_environment():
    """Check if R is available and has required packages."""
    print("\n=== Checking R Environment ===")
    
    try:
        result = subprocess.run(['R', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ R is available")
            print(f"R Version: {result.stdout.split()[2]}")
        else:
            print("❌ R is not available")
            return False
    except Exception as e:
        print(f"❌ R check failed: {e}")
        return False
    
    try:
        r_check_script = '''
        required_packages <- c("meta", "metafor", "jsonlite")
        installed_packages <- installed.packages()[,"Package"]
        missing_packages <- required_packages[!required_packages %in% installed_packages]
        
        if(length(missing_packages) == 0) {
            cat("All required packages are installed\\n")
        } else {
            cat("Missing packages:", paste(missing_packages, collapse=", "), "\\n")
        }
        '''
        
        result = subprocess.run(['R', '--slave', '-e', r_check_script], 
                              capture_output=True, text=True, timeout=10)
        print(f"Package Check: {result.stdout.strip()}")
        return "All required packages are installed" in result.stdout
    except Exception as e:
        print(f"❌ Package check failed: {e}")
        return False

def analyze_code_paths():
    """Analyze which code paths use R vs Python."""
    print("\n=== Analyzing Code Paths ===")
    
    meta_analysis_file = Path(__file__).parent / "meta_analysis_mcp_server" / "tools" / "meta_analysis.py"
    
    if meta_analysis_file.exists():
        with open(meta_analysis_file, 'r') as f:
            content = f.read()
            
        r_calls = content.count('run_r_script')
        subprocess_calls = content.count('subprocess')
        
        print(f"Found {r_calls} calls to run_r_script")
        print(f"Found {subprocess_calls} subprocess calls")
        
        functions_using_r = []
        if 'run_r_script("perform_meta_analysis"' in content:
            functions_using_r.append("perform_meta_analysis")
        if 'run_r_script("generate_forest_plot"' in content:
            functions_using_r.append("generate_forest_plot")
        if 'run_r_script("assess_publication_bias"' in content:
            functions_using_r.append("assess_publication_bias")
            
        print(f"Functions using R: {functions_using_r}")
        
        python_calculations = []
        if 'np.average' in content or 'numpy' in content:
            python_calculations.append("numpy calculations")
        if 'scipy.stats' in content:
            python_calculations.append("scipy statistics")
        if 'plt.figure' in content or 'matplotlib' in content:
            python_calculations.append("matplotlib plotting")
            
        print(f"Python calculations found: {python_calculations}")
    else:
        print("❌ meta_analysis.py file not found")

if __name__ == "__main__":
    print("Meta-Analysis R Integration Status Check")
    print("=" * 50)
    
    # Run all tests
    r_env_ok = check_r_environment()
    analyze_code_paths()
    r_direct_ok = test_r_script_direct()
    python_ok = test_python_meta_analysis()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"R Environment: {'✅' if r_env_ok else '❌'}")
    print(f"R Script Direct: {'✅' if r_direct_ok else '❌'}")
    print(f"Python Meta-Analysis: {'✅' if python_ok else '❌'}")
    
    if r_direct_ok and python_ok:
        print("\n🔍 CONCLUSION: Both R and Python implementations are available")
        print("   Need to verify which one is actually being used in the workflow")
    elif python_ok and not r_direct_ok:
        print("\n⚠️  CONCLUSION: Only Python implementation is working")
        print("   R integration exists but is not functional")
    elif r_direct_ok and not python_ok:
        print("\n✅ CONCLUSION: R implementation is working")
        print("   Python fallback may have issues")
    else:
        print("\n❌ CONCLUSION: Neither implementation is working properly")

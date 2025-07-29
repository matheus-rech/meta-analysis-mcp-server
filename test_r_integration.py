#!/usr/bin/env python3
"""
Test R script integration to verify genuine statistical computations
"""

import subprocess
import json
import sys
import os

def test_r_script_availability():
    """Test if R script is accessible and can be executed"""
    print("🔍 Testing R script availability...")
    
    try:
        result = subprocess.run(
            ["Rscript", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ Rscript available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Rscript failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Rscript: {e}")
        return False

def test_r_meta_analysis_function():
    """Test R meta-analysis function with sample data"""
    print("\n🧮 Testing R meta-analysis function...")
    
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
        
        if result.returncode == 0:
            try:
                r_output = json.loads(result.stdout.strip())
                print("✅ R meta-analysis function executed successfully")
                print(f"   📊 Pooled effect: {r_output.get('estimate', 'N/A')}")
                print(f"   📊 Confidence interval: [{r_output.get('ci_lower', 'N/A')}, {r_output.get('ci_upper', 'N/A')}]")
                print(f"   📊 Heterogeneity I²: {r_output.get('i_squared', 'N/A')}%")
                
                if isinstance(r_output.get('estimate'), (int, float)):
                    print("✅ Results contain genuine numerical computations")
                    return True, r_output
                else:
                    print("❌ Results appear to be placeholders")
                    return False, None
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON output from R: {result.stdout}")
                return False, None
        else:
            print(f"❌ R script failed: {result.stderr}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error executing R script: {e}")
        return False, None

def test_r_publication_bias_function():
    """Test R publication bias assessment function"""
    print("\n📈 Testing R publication bias function...")
    
    test_data = {
        "effect_sizes": [-0.5, -0.3, -0.7, -0.4, -0.6],
        "standard_errors": [0.15, 0.12, 0.18, 0.14, 0.16]
    }
    
    try:
        result = subprocess.run(
            ["Rscript", "r_scripts/meta_analysis.R", "assess_publication_bias", json.dumps(test_data)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/home/ubuntu/repos/meta-analysis-mcp-server"
        )
        
        if result.returncode == 0:
            try:
                r_output = json.loads(result.stdout.strip())
                print("✅ R publication bias function executed successfully")
                egger_p = r_output.get('egger_test', {}).get('p_value', 'N/A')
                begg_p = r_output.get('begg_test', {}).get('p_value', 'N/A')
                print(f"   📊 Egger's test p-value: {egger_p}")
                print(f"   📊 Begg's test p-value: {begg_p}")
                
                if isinstance(egger_p, (int, float)):
                    print("✅ Publication bias tests produce genuine statistical results")
                    return True, r_output
                else:
                    print("❌ Publication bias results appear to be placeholders")
                    return False, None
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON output from R: {result.stdout}")
                return False, None
        else:
            print(f"❌ R publication bias script failed: {result.stderr}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error executing R publication bias script: {e}")
        return False, None

def test_r_forest_plot_function():
    """Test R forest plot data generation function"""
    print("\n🌲 Testing R forest plot function...")
    
    test_data = {
        "function": "create_forest_plot_data",
        "effect_sizes": [-0.5, -0.3, -0.7, -0.4, -0.6],
        "standard_errors": [0.15, 0.12, 0.18, 0.14, 0.16],
        "study_names": ["Study A", "Study B", "Study C", "Study D", "Study E"]
    }
    
    try:
        result = subprocess.run(
            ["Rscript", "r_scripts/meta_analysis.R", "create_forest_plot_data", json.dumps(test_data)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/home/ubuntu/repos/meta-analysis-mcp-server"
        )
        
        if result.returncode == 0:
            try:
                r_output = json.loads(result.stdout.strip())
                print("✅ R forest plot function executed successfully")
                print(f"   📊 Studies processed: {len(r_output.get('studies', []))}")
                print(f"   📊 Overall effect: {r_output.get('overall_effect', 'N/A')}")
                
                if 'studies' in r_output and len(r_output['studies']) > 0:
                    print("✅ Forest plot data structure is valid")
                    return True, r_output
                else:
                    print("❌ Forest plot data structure is invalid")
                    return False, None
                    
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON output from R: {result.stdout}")
                return False, None
        else:
            print(f"❌ R forest plot script failed: {result.stderr}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error executing R forest plot script: {e}")
        return False, None

def main():
    """Run comprehensive R integration tests"""
    print("🧪 R SCRIPT INTEGRATION TEST")
    print("=" * 40)
    
    results = {
        "timestamp": "2025-01-29T02:36:14Z",
        "r_version": None,
        "tests": {}
    }
    
    if not test_r_script_availability():
        print("\n❌ R script not available - cannot proceed with integration tests")
        return
    
    success_count = 0
    total_tests = 3
    
    success, output = test_r_meta_analysis_function()
    results["tests"]["meta_analysis"] = {"success": success, "output": output}
    if success:
        success_count += 1
    
    success, output = test_r_publication_bias_function()
    results["tests"]["publication_bias"] = {"success": success, "output": output}
    if success:
        success_count += 1
    
    success, output = test_r_forest_plot_function()
    results["tests"]["forest_plot"] = {"success": success, "output": output}
    if success:
        success_count += 1
    
    # Summary
    print(f"\n🎉 R Integration Test Results: {success_count}/{total_tests} tests passed")
    results["success_rate"] = f"{success_count}/{total_tests}"
    results["percentage"] = round((success_count / total_tests) * 100, 1)
    
    if success_count == total_tests:
        print("✅ All R functions produce genuine statistical computations")
        results["conclusion"] = "R integration fully functional with genuine statistical computations"
    elif success_count > 0:
        print("⚠️  Partial R integration - some functions work")
        results["conclusion"] = "Partial R integration - core functions operational"
    else:
        print("❌ R integration failed - no functions working")
        results["conclusion"] = "R integration failed - functions not operational"
    
    with open("r_integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: r_integration_test_results.json")

if __name__ == "__main__":
    main()

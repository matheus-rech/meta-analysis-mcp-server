#!/usr/bin/env python3
"""
Test script to specifically debug and fix visualization tools
"""

import os
import json
import sys
import subprocess
from pathlib import Path
import traceback

REPO_ROOT = Path("/home/ubuntu/repos/meta-analysis-mcp-server")
R_SCRIPTS_DIR = REPO_ROOT / "r_scripts"
OUTPUT_DIR = REPO_ROOT / "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_r_script(function_name, input_data):
    """Run R script with the given function name and input data"""
    print(f"🔄 Running R function: {function_name}")
    
    try:
        result = subprocess.run(
            ["Rscript", str(R_SCRIPTS_DIR / "meta_analysis.R"), function_name, json.dumps(input_data)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"❌ R script failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return None
            
        try:
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON output: {result.stdout}")
            return None
            
    except Exception as e:
        print(f"❌ Exception running R script: {e}")
        traceback.print_exc()
        return None

def test_forest_plot():
    """Test forest plot generation"""
    print("\n🌲 TESTING FOREST PLOT GENERATION")
    print("=" * 50)
    
    test_data = {
        "effect_sizes": [-0.85, -0.91, -0.94, -0.76, -0.88],
        "standard_errors": [0.14, 0.16, 0.12, 0.18, 0.15],
        "study_names": ["Smith 2020 (CBT)", "Garcia 2019 (MBCT)", "Chen 2021 (IPT)", "Brown 2018 (BA)", "Taylor 2022 (ACT)"],
        "output_file": str(OUTPUT_DIR / "forest_plot.png"),
        "title": "Forest Plot: Psychological Interventions for Depression",
        "x_label": "Standardized Mean Difference",
        "width": 1000,
        "height": 600
    }
    
    result = run_r_script("create_forest_plot", test_data)
    
    if result and result.get("success"):
        print(f"✅ Forest plot generated successfully: {result.get('output_file')}")
        return True
    else:
        print("❌ Failed to generate forest plot")
        if result:
            print(f"Error: {result.get('error', 'Unknown error')}")
        return False

def test_funnel_plot():
    """Test funnel plot generation for publication bias"""
    print("\n📊 TESTING FUNNEL PLOT GENERATION")
    print("=" * 50)
    
    test_data = {
        "effect_sizes": [-0.85, -0.91, -0.94, -0.76, -0.88],
        "standard_errors": [0.14, 0.16, 0.12, 0.18, 0.15],
        "output_file": str(OUTPUT_DIR / "funnel_plot.png"),
        "title": "Funnel Plot: Publication Bias Assessment",
        "width": 800,
        "height": 600
    }
    
    result = run_r_script("create_funnel_plot", test_data)
    
    if result and result.get("success"):
        print(f"✅ Funnel plot generated successfully: {result.get('output_file')}")
        return True
    else:
        print("❌ Failed to generate funnel plot")
        if result:
            print(f"Error: {result.get('error', 'Unknown error')}")
        return False

def install_r_packages():
    """Install required R packages"""
    print("\n📦 INSTALLING REQUIRED R PACKAGES")
    print("=" * 50)
    
    r_install_script = """
    install_packages <- function() {
      required_packages <- c("meta", "metafor", "ggplot2", "dplyr", "jsonlite")
      
      for (pkg in required_packages) {
        if (!requireNamespace(pkg, quietly = TRUE)) {
          install.packages(pkg, repos = "https://cloud.r-project.org")
        }
      }
      
      all_installed <- all(sapply(required_packages, requireNamespace, quietly = TRUE))
      
      return(list(success = all_installed, packages = required_packages))
    }
    
    result <- install_packages()
    cat(jsonlite::toJSON(result, auto_unbox = TRUE))
    """
    
    try:
        result = subprocess.run(
            ["Rscript", "-e", r_install_script],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to install R packages: {result.stderr}")
            return False
            
        try:
            output = json.loads(result.stdout.strip())
            if output.get("success"):
                print(f"✅ R packages installed successfully: {', '.join(output.get('packages', []))}")
                return True
            else:
                print("❌ Failed to install all required R packages")
                return False
                
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Exception installing R packages: {e}")
        traceback.print_exc()
        return False

def check_r_environment():
    """Check R environment and capabilities"""
    print("\n🔍 CHECKING R ENVIRONMENT")
    print("=" * 50)
    
    r_check_script = """
    check_environment <- function() {
      r_version <- paste(R.version$major, R.version$minor, sep = ".")
      
      packages <- c("meta", "metafor", "ggplot2", "dplyr", "jsonlite")
      pkg_status <- sapply(packages, requireNamespace, quietly = TRUE)
      
      graphics_capabilities <- capabilities()
      
      list(
        r_version = r_version,
        packages = as.list(pkg_status),
        graphics_capabilities = as.list(graphics_capabilities)
      )
    }
    
    result <- check_environment()
    cat(jsonlite::toJSON(result, auto_unbox = TRUE))
    """
    
    try:
        result = subprocess.run(
            ["Rscript", "-e", r_check_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to check R environment: {result.stderr}")
            return False
            
        try:
            output = json.loads(result.stdout.strip())
            print(f"✅ R version: {output.get('r_version', 'Unknown')}")
            
            print("\n📦 Package availability:")
            for pkg, status in output.get('packages', {}).items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {pkg}")
            
            print("\n🎨 Graphics capabilities:")
            for cap, status in output.get('graphics_capabilities', {}).items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {cap}")
                
            return True
            
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Exception checking R environment: {e}")
        traceback.print_exc()
        return False

def update_r_script():
    """Update R script to fix visualization issues"""
    print("\n🔧 UPDATING R SCRIPT")
    print("=" * 50)
    
    r_script_path = R_SCRIPTS_DIR / "meta_analysis.R"
    
    if not r_script_path.exists():
        print(f"❌ R script not found at {r_script_path}")
        return False
    
    with open(r_script_path, "r") as f:
        r_script_content = f.read()
    
    if "create_forest_plot <- function" in r_script_content and "create_funnel_plot <- function" in r_script_content:
        print("✅ R script already contains visualization functions")
        return True
    
    visualization_functions = """
create_forest_plot <- function(params_json) {
  tryCatch({
    params <- fromJSON(params_json)
    
    effect_sizes <- params$effect_sizes
    standard_errors <- params$standard_errors
    study_names <- params$study_names
    output_file <- params$output_file
    title <- params$title
    x_label <- params$x_label
    width <- params$width
    height <- params$height
    
    if (is.null(title)) title <- "Forest Plot"
    if (is.null(x_label)) x_label <- "Effect Size"
    if (is.null(width)) width <- 800
    if (is.null(height)) height <- 600
    
    data <- data.frame(
      study = study_names,
      effect = effect_sizes,
      se = standard_errors
    )
    
    data$lower <- data$effect - 1.96 * data$se
    data$upper <- data$effect + 1.96 * data$se
    
    meta_result <- metafor::rma(yi = effect, sei = se, data = data, method = "REML")
    
    forest_plot <- metafor::forest(
      meta_result,
      slab = study_names,
      xlab = x_label,
      main = title,
      cex = 0.8,
      cex.lab = 0.8,
      cex.axis = 0.8
    )
    
    if (!is.null(output_file)) {
      dir.create(dirname(output_file), showWarnings = FALSE, recursive = TRUE)
      
      png(output_file, width = width, height = height)
      metafor::forest(
        meta_result,
        slab = study_names,
        xlab = x_label,
        main = title,
        cex = 0.8,
        cex.lab = 0.8,
        cex.axis = 0.8
      )
      dev.off()
    }
    
    return(toJSON(list(
      success = TRUE,
      output_file = output_file,
      pooled_effect = meta_result$b,
      ci_lower = meta_result$ci.lb,
      ci_upper = meta_result$ci.ub
    ), auto_unbox = TRUE))
    
  }, error = function(e) {
    return(toJSON(list(
      success = FALSE,
      error = as.character(e)
    ), auto_unbox = TRUE))
  })
}

# Create funnel plot
create_funnel_plot <- function(params_json) {
  tryCatch({
    params <- fromJSON(params_json)
    
    effect_sizes <- params$effect_sizes
    standard_errors <- params$standard_errors
    output_file <- params$output_file
    title <- params$title
    width <- params$width
    height <- params$height
    
    if (is.null(title)) title <- "Funnel Plot"
    if (is.null(width)) width <- 800
    if (is.null(height)) height <- 600
    
    data <- data.frame(
      effect = effect_sizes,
      se = standard_errors
    )
    
    meta_result <- metafor::rma(yi = effect, sei = se, data = data, method = "REML")
    
    # Create funnel plot
    funnel_plot <- metafor::funnel(
      meta_result,
      main = title,
      xlab = "Effect Size",
      ylab = "Standard Error"
    )
    
    if (!is.null(output_file)) {
      dir.create(dirname(output_file), showWarnings = FALSE, recursive = TRUE)
      
      png(output_file, width = width, height = height)
      metafor::funnel(
        meta_result,
        main = title,
        xlab = "Effect Size",
        ylab = "Standard Error"
      )
      dev.off()
    }
    
    return(toJSON(list(
      success = TRUE,
      output_file = output_file,
      egger_test = list(
        statistic = meta_result$zval,
        p_value = meta_result$pval
      )
    ), auto_unbox = TRUE))
    
  }, error = function(e) {
    return(toJSON(list(
      success = FALSE,
      error = as.character(e)
    ), auto_unbox = TRUE))
  })
}
"""
    
    updated_r_script = r_script_content + "\n" + visualization_functions
    
    with open(r_script_path, "w") as f:
        f.write(updated_r_script)
    
    print(f"✅ R script updated with visualization functions: {r_script_path}")
    return True

def main():
    """Main function"""
    print("🧪 VISUALIZATION TOOLS TEST")
    print("=" * 50)
    
    check_r_environment()
    
    install_r_packages()
    
    update_r_script()
    
    forest_plot_success = test_forest_plot()
    
    funnel_plot_success = test_funnel_plot()
    
    print("\n📋 VISUALIZATION TEST SUMMARY")
    print("=" * 50)
    print(f"Forest Plot: {'✅ Success' if forest_plot_success else '❌ Failed'}")
    print(f"Funnel Plot: {'✅ Success' if funnel_plot_success else '❌ Failed'}")
    
    if forest_plot_success and funnel_plot_success:
        print("\n🎉 All visualization tools working successfully!")
        print(f"Forest Plot: {OUTPUT_DIR}/forest_plot.png")
        print(f"Funnel Plot: {OUTPUT_DIR}/funnel_plot.png")
    else:
        print("\n⚠️ Some visualization tools failed. See above for details.")

if __name__ == "__main__":
    main()

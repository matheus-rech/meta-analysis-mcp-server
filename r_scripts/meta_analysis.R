#!/usr/bin/env Rscript

# Meta-Analysis R Script for MCP Server
# Provides statistical meta-analysis functionality using metafor package

library(metafor)
library(dmetar)
library(meta)
library(jsonlite)

# Function to perform meta-analysis
perform_meta_analysis <- function(effect_sizes, standard_errors, study_ids, method = "REML") {
  tryCatch({
    # Create meta-analysis object
    ma_result <- rma(yi = effect_sizes, sei = standard_errors, 
                     slab = study_ids, method = method)
    
    # Extract results
    result <- list(
      estimate = as.numeric(ma_result$beta),
      se = as.numeric(ma_result$se),
      ci_lower = as.numeric(ma_result$ci.lb),
      ci_upper = as.numeric(ma_result$ci.ub),
      z_value = as.numeric(ma_result$zval),
      p_value = as.numeric(ma_result$pval),
      tau_squared = as.numeric(ma_result$tau2),
      i_squared = as.numeric(ma_result$I2),
      h_squared = as.numeric(ma_result$H2),
      q_statistic = as.numeric(ma_result$QE),
      q_df = as.numeric(ma_result$k - ma_result$p),
      q_p_value = as.numeric(ma_result$QEp)
    )
    
    return(toJSON(result, auto_unbox = TRUE))
    
  }, error = function(e) {
    return(toJSON(list(error = paste("Meta-analysis failed:", e$message)), auto_unbox = TRUE))
  })
}

# Function to assess publication bias
assess_publication_bias <- function(effect_sizes, standard_errors, study_ids) {
  tryCatch({
    # Egger's test
    egger_result <- regtest(effect_sizes, standard_errors, model = "lm")
    
    # Begg's test  
    begg_result <- ranktest(effect_sizes, standard_errors)
    
    # Trim and fill
    tf_result <- trimfill(rma(yi = effect_sizes, sei = standard_errors))
    
    result <- list(
      egger_test = list(
        statistic = as.numeric(egger_result$zval),
        p_value = as.numeric(egger_result$pval),
        significant = as.numeric(egger_result$pval) < 0.05
      ),
      begg_test = list(
        statistic = as.numeric(begg_result$tau),
        p_value = as.numeric(begg_result$pval),
        significant = as.numeric(begg_result$pval) < 0.05
      ),
      trim_fill = list(
        k0 = as.numeric(tf_result$k0),
        side = tf_result$side,
        estimate_adjusted = as.numeric(tf_result$beta),
        se_adjusted = as.numeric(tf_result$se)
      )
    )
    
    return(toJSON(result, auto_unbox = TRUE))
    
  }, error = function(e) {
    return(toJSON(list(error = paste("Publication bias assessment failed:", e$message)), auto_unbox = TRUE))
  })
}

# Function to create forest plot data
create_forest_plot_data <- function(effect_sizes, standard_errors, study_ids, 
                                   ci_lower, ci_upper, weights) {
  tryCatch({
    # Prepare data for forest plot
    plot_data <- data.frame(
      study = study_ids,
      effect = effect_sizes,
      se = standard_errors,
      ci_lb = ci_lower,
      ci_ub = ci_upper,
      weight = weights
    )
    
    return(toJSON(plot_data, auto_unbox = FALSE))
    
  }, error = function(e) {
    return(toJSON(list(error = paste("Forest plot data creation failed:", e$message)), auto_unbox = TRUE))
  })
}

# Main execution
if (!interactive()) {
  args <- commandArgs(trailingOnly = TRUE)
  
  if (length(args) < 1) {
    cat("Usage: Rscript meta_analysis.R <function_name> [arguments]\n")
    quit(status = 1)
  }
  
  func_name <- args[1]
  
  if (func_name == "perform_meta_analysis") {
    # Parse JSON input
    input_data <- fromJSON(args[2])
    result <- perform_meta_analysis(
      input_data$effect_sizes,
      input_data$standard_errors, 
      input_data$study_ids,
      input_data$method
    )
    cat(result)
    
  } else if (func_name == "assess_publication_bias") {
    input_data <- fromJSON(args[2])
    result <- assess_publication_bias(
      input_data$effect_sizes,
      input_data$standard_errors,
      input_data$study_ids
    )
    cat(result)
    
  } else if (func_name == "create_forest_plot_data") {
    input_data <- fromJSON(args[2])
    result <- create_forest_plot_data(
      input_data$effect_sizes,
      input_data$standard_errors,
      input_data$study_ids,
      input_data$ci_lower,
      input_data$ci_upper,
      input_data$weights
    )
    cat(result)
    
  } else {
    cat("Unknown function:", func_name, "\n")
    quit(status = 1)
  }
}

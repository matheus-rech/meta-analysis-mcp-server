#!/usr/bin/env Rscript

# Meta-Analysis R Script for MCP Server
# Provides statistical meta-analysis functionality using metafor and meta packages

# Set library path
.libPaths(c("~/R/library", .libPaths()))

# Load required libraries
suppressMessages({
  library(jsonlite)
  library(metafor)
  library(meta)
  library(ggplot2)
})

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
    # Create rma object for metafor
    ma_obj <- rma(yi = effect_sizes, sei = standard_errors, slab = study_ids)
    
    # Egger's test for funnel plot asymmetry
    egger_result <- regtest(ma_obj)
    
    # Begg's rank correlation test
    begg_result <- ranktest(ma_obj)
    
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
      interpretation = ifelse(egger_result$pval < 0.05, "Significant asymmetry detected", "No significant asymmetry")
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

# Create forest plot
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
    if (is.null(width)) width <- 1200
    if (is.null(height)) height <- max(800, length(study_names) * 50)
    
    data <- data.frame(
      study = study_names,
      effect = effect_sizes,
      se = standard_errors
    )
    
    data$lower <- data$effect - 1.96 * data$se
    data$upper <- data$effect + 1.96 * data$se
    
    meta_result <- metafor::rma(yi = effect, sei = se, data = data, method = "REML")
    
    if (!is.null(output_file)) {
      dir.create(dirname(output_file), showWarnings = FALSE, recursive = TRUE)
      
      png(output_file, width = width, height = height, res = 150)
      forest(meta_result,
             main = title,
             xlab = x_label,
             comb.fixed = FALSE,
             comb.random = TRUE,
             overall = TRUE,
             hetstat = TRUE,
             print.tau2 = TRUE,
             print.I2 = TRUE,
             col.diamond = "blue",
             col.diamond.lines = "black",
             col.square = "red",
             col.square.lines = "black",
             col.inside = "white",
             fontsize = 12,
             spacing = 1.2)
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
    
    if (!is.null(output_file)) {
      dir.create(dirname(output_file), showWarnings = FALSE, recursive = TRUE)
      
      png(output_file, width = width, height = height, res = 150)
      funnel(meta_result,
             main = title,
             xlab = "Effect Size",
             ylab = "Standard Error",
             col = "blue",
             pch = 16,
             cex = 1.2)
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

# Function to perform meta-analysis with file input
perform_meta_analysis_file <- function(data_file, output_dir, method = "random", measure = "OR") {
  tryCatch({
    # Read data
    data <- read.csv(data_file)
    
    # Validate required columns
    required_cols <- c("study_id", "effect_size", "se")
    if (!all(required_cols %in% colnames(data))) {
      stop(paste("Missing required columns:", paste(setdiff(required_cols, colnames(data)), collapse = ", ")))
    }
    
    # Perform meta-analysis using meta package
    if (measure == "OR" && all(c("events_treatment", "n_treatment", "events_control", "n_control") %in% colnames(data))) {
      # Binary outcome meta-analysis
      meta_method <- if(method == "random") "Inverse" else "MH"
      meta_result <- metabin(
        event.e = data$events_treatment,
        n.e = data$n_treatment,
        event.c = data$events_control,
        n.c = data$n_control,
        studlab = data$study_id,
        method = meta_method,
        sm = "OR"
      )
    } else {
      # Generic inverse variance meta-analysis
      meta_result <- metagen(
        TE = log(data$effect_size),
        seTE = data$se,
        studlab = data$study_id,
        method.tau = if(method == "random") "REML" else "FE",
        sm = measure
      )
    }
    
    # Extract results
    results <- list(
      pooled_effect = exp(meta_result$TE.random),
      pooled_effect_log = meta_result$TE.random,
      se_pooled = meta_result$seTE.random,
      confidence_interval = paste0("[", round(exp(meta_result$lower.random), 3), ", ", round(exp(meta_result$upper.random), 3), "]"),
      p_value = meta_result$pval.random,
      heterogeneity_tau2 = meta_result$tau2,
      heterogeneity_i2 = paste0(round(meta_result$I2 * 100, 1), "%"),
      heterogeneity_q = meta_result$Q,
      heterogeneity_p = meta_result$pval.Q,
      n_studies = meta_result$k
    )
    
    # Save results
    results_file <- file.path(output_dir, "meta_analysis_results.json")
    writeLines(jsonlite::toJSON(results, pretty = TRUE), results_file)
    
    # Save R object for plotting
    rds_file <- file.path(output_dir, "meta_analysis_object.rds")
    saveRDS(meta_result, rds_file)
    
    return(toJSON(results, auto_unbox = TRUE))
    
  }, error = function(e) {
    return(toJSON(list(error = paste("Meta-analysis failed:", e$message)), auto_unbox = TRUE))
  })
}

# Function to generate forest plot from file
generate_forest_plot <- function(meta_object_file, output_file, title = "Forest Plot") {
  tryCatch({
    # Load meta-analysis object
    meta_result <- readRDS(meta_object_file)
    
    # Generate forest plot
    png(output_file, width = 1200, height = 800, res = 150)
    
    forest(meta_result,
           main = title,
           xlab = "Effect Size (OR)",
           comb.fixed = FALSE,
           comb.random = TRUE,
           overall = TRUE,
           hetstat = TRUE,
           print.tau2 = TRUE,
           print.I2 = TRUE,
           col.diamond = "blue",
           col.diamond.lines = "black",
           col.square = "red",
           col.square.lines = "black",
           col.inside = "white",
           fontsize = 12,
           spacing = 1.2)
    
    dev.off()
    
    return(toJSON(list(
      success = TRUE,
      output_file = output_file
    ), auto_unbox = TRUE))
    
  }, error = function(e) {
    return(toJSON(list(
      success = FALSE,
      error = as.character(e)
    ), auto_unbox = TRUE))
  })
}

# Function to generate funnel plot from file
generate_funnel_plot <- function(meta_object_file, output_file, title = "Funnel Plot") {
  tryCatch({
    # Load meta-analysis object
    meta_result <- readRDS(meta_object_file)
    
    # Generate funnel plot
    png(output_file, width = 800, height = 600, res = 150)
    
    funnel(meta_result,
           main = title,
           xlab = "Effect Size (log OR)",
           ylab = "Standard Error",
           col = "blue",
           pch = 16,
           cex = 1.2)
    
    dev.off()
    
    return(toJSON(list(
      success = TRUE,
      output_file = output_file
    ), auto_unbox = TRUE))
    
  }, error = function(e) {
    return(toJSON(list(
      success = FALSE,
      error = as.character(e)
    ), auto_unbox = TRUE))
  })
}

# Function to perform publication bias tests from file
assess_publication_bias_file <- function(meta_object_file, output_dir) {
  tryCatch({
    # Load meta-analysis object
    meta_result <- readRDS(meta_object_file)
    
    # Egger's test
    egger_test <- metabias(meta_result, method = "linreg")
    
    # Begg's test (rank correlation)
    begg_test <- metabias(meta_result, method = "rank")
    
    # Results
    bias_results <- list(
      egger_test = list(
        statistic = egger_test$statistic,
        p_value = egger_test$p.value,
        method = "Egger's linear regression test"
      ),
      begg_test = list(
        statistic = begg_test$statistic,
        p_value = begg_test$p.value,
        method = "Begg's rank correlation test"
      )
    )
    
    # Save results
    bias_file <- file.path(output_dir, "publication_bias_results.json")
    writeLines(jsonlite::toJSON(bias_results, pretty = TRUE), bias_file)
    
    return(toJSON(bias_results, auto_unbox = TRUE))
    
  }, error = function(e) {
    return(toJSON(list(
      error = paste("Publication bias assessment failed:", e$message)
    ), auto_unbox = TRUE))
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
    # Provide default study IDs if not provided
    study_ids <- if(is.null(input_data$study_ids)) paste0("Study_", 1:length(input_data$effect_sizes)) else input_data$study_ids
    result <- assess_publication_bias(
      input_data$effect_sizes,
      input_data$standard_errors,
      study_ids
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
    
  } else if (func_name == "create_forest_plot") {
    result <- create_forest_plot(args[2])
    cat(result)
    
  } else if (func_name == "create_funnel_plot") {
    result <- create_funnel_plot(args[2])
    cat(result)
    
  } else if (func_name == "analyze") {
    # File-based meta-analysis
    data_file <- args[2]
    output_dir <- args[3]
    method <- if (length(args) > 3) args[4] else "random"
    measure <- if (length(args) > 4) args[5] else "OR"
    
    # Create output directory if it doesn't exist
    dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
    
    result <- perform_meta_analysis_file(data_file, output_dir, method, measure)
    cat(result)
    
  } else if (func_name == "forest") {
    # File-based forest plot
    meta_object_file <- args[2]
    output_file <- args[3]
    title <- if (length(args) > 3) args[4] else "Forest Plot"
    
    result <- generate_forest_plot(meta_object_file, output_file, title)
    cat(result)
    
  } else if (func_name == "funnel") {
    # File-based funnel plot
    meta_object_file <- args[2]
    output_file <- args[3]
    title <- if (length(args) > 3) args[4] else "Funnel Plot"
    
    result <- generate_funnel_plot(meta_object_file, output_file, title)
    cat(result)
    
  } else if (func_name == "bias") {
    # File-based publication bias assessment
    meta_object_file <- args[2]
    output_dir <- args[3]
    
    # Create output directory if it doesn't exist
    dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
    
    result <- assess_publication_bias_file(meta_object_file, output_dir)
    cat(result)
    
  } else {
    cat("Unknown function:", func_name, "\n")
    quit(status = 1)
  }
}

#!/usr/bin/env Rscript

# Meta-Analysis R Script
# This script performs meta-analysis using the meta package

# Set library path
.libPaths(c("~/R/library", .libPaths()))

# Load required libraries
suppressMessages({
  library(meta)
  library(metafor)
  library(ggplot2)
})

# Function to perform meta-analysis
perform_meta_analysis <- function(data_file, output_dir, method = "random", measure = "OR") {
  
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
  
  return(results)
}

# Function to generate forest plot
generate_forest_plot <- function(meta_object_file, output_file, title = "Forest Plot") {
  
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
  
  return(output_file)
}

# Function to generate funnel plot
generate_funnel_plot <- function(meta_object_file, output_file, title = "Funnel Plot") {
  
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
  
  return(output_file)
}

# Function to perform publication bias tests
assess_publication_bias <- function(meta_object_file, output_dir) {
  
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
  
  return(bias_results)
}

# Command line interface
if (!interactive()) {
  args <- commandArgs(trailingOnly = TRUE)
  
  if (length(args) < 3) {
    cat("Usage: Rscript meta_analysis.R <command> <data_file> <output_dir> [additional_args]\n")
    cat("Commands:\n")
    cat("  analyze - Perform meta-analysis\n")
    cat("  forest - Generate forest plot\n")
    cat("  funnel - Generate funnel plot\n")
    cat("  bias - Assess publication bias\n")
    quit(status = 1)
  }
  
  command <- args[1]
  data_file <- args[2]
  output_dir <- args[3]
  
  # Create output directory if it doesn't exist
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  
  if (command == "analyze") {
    method <- if (length(args) > 3) args[4] else "random"
    measure <- if (length(args) > 4) args[5] else "OR"
    results <- perform_meta_analysis(data_file, output_dir, method, measure)
    cat("Meta-analysis completed successfully\n")
    
  } else if (command == "forest") {
    meta_object_file <- file.path(output_dir, "meta_analysis_object.rds")
    output_file <- file.path(output_dir, "forest_plot.png")
    title <- if (length(args) > 3) args[4] else "Forest Plot"
    generate_forest_plot(meta_object_file, output_file, title)
    cat("Forest plot generated:", output_file, "\n")
    
  } else if (command == "funnel") {
    meta_object_file <- file.path(output_dir, "meta_analysis_object.rds")
    output_file <- file.path(output_dir, "funnel_plot.png")
    title <- if (length(args) > 3) args[4] else "Funnel Plot"
    generate_funnel_plot(meta_object_file, output_file, title)
    cat("Funnel plot generated:", output_file, "\n")
    
  } else if (command == "bias") {
    meta_object_file <- file.path(output_dir, "meta_analysis_object.rds")
    results <- assess_publication_bias(meta_object_file, output_dir)
    cat("Publication bias assessment completed\n")
    
  } else {
    cat("Unknown command:", command, "\n")
    quit(status = 1)
  }
}

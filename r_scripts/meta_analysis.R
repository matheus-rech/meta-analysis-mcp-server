.libPaths(c("~/R/library", .libPaths()))
#!/usr/bin/env Rscript

# Meta-Analysis R Script for MCP Server
# Provides statistical meta-analysis functionality using metafor package

library(metafor)
library(jsonlite)

# Note: dmetar and meta packages not available, using metafor only

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
    input_data <- fromJSON(args[2])
    result <- create_forest_plot(args[2])
    cat(result)
    
  } else if (func_name == "create_funnel_plot") {
    input_data <- fromJSON(args[2])
    result <- create_funnel_plot(args[2])
    cat(result)
    
  } else {
    cat("Unknown function:", func_name, "\n")
    quit(status = 1)
  }
}


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

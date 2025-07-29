# Install required R packages to user library
.libPaths(c("~/R/library", .libPaths()))
cat("Using library paths:", .libPaths(), "\n")

# List of required packages
required_packages <- c("meta", "metafor", "ggplot2", "dplyr", "jsonlite")

# Install missing packages
for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    cat("Installing package:", pkg, "\n")
    install.packages(pkg, repos = "https://cloud.r-project.org", lib = "~/R/library")
  } else {
    cat("Package already installed:", pkg, "\n")
  }
}

# Check if all packages are installed
for (pkg in required_packages) {
  if (requireNamespace(pkg, quietly = TRUE)) {
    cat("✓ Package loaded successfully:", pkg, "\n")
  } else {
    cat("✗ Failed to load package:", pkg, "\n")
  }
}

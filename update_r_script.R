# Update R script to use the correct library path
.libPaths(c("~/R/library", .libPaths()))
cat("Using library paths:", .libPaths(), "\n")

# List installed packages
installed_packages <- installed.packages()
cat("Installed packages in user library:\n")
user_packages <- installed_packages[installed_packages[,"LibPath"] == "~/R/library", "Package"]
print(user_packages)

# Check if meta package is available
if ("meta" %in% rownames(installed_packages)) {
  cat("✓ meta package is installed at:", installed_packages["meta", "LibPath"], "\n")
} else {
  cat("✗ meta package is not installed\n")
}

# Create a modified version of the R script that sets the library path
r_script_path <- "r_scripts/meta_analysis.R"
r_script <- readLines(r_script_path)

# Add library path setting at the beginning of the script
library_path_line <- ".libPaths(c(\"~/R/library\", .libPaths()))"
if (!any(grepl(".libPaths", r_script))) {
  r_script <- c(library_path_line, r_script)
  writeLines(r_script, r_script_path)
  cat("✓ Updated R script with library path\n")
} else {
  cat("✓ R script already has library path setting\n")
}

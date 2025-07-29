# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including R
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    r-base \
    r-base-dev \
    git \
    curl \
    libxml2-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libfontconfig1-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Install R packages
RUN R -e "install.packages(c('meta', 'metafor', 'metaSEM', 'nloptr', 'xml2', 'lme4', 'jsonlite', 'DT', 'rmarkdown', 'knitr', 'ggplot2'), repos='https://cran.rstudio.com/')"

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir mcp pydantic statsmodels seaborn kaleido aiohttp aiohttp-cors

# Copy the application code
COPY meta_analysis_mcp_server/ ./meta_analysis_mcp_server/
COPY r_scripts/ ./r_scripts/
COPY templates/ ./templates/
COPY README.md ./

# Install the package
RUN pip install -e .

# Create output directory for R-generated plots
RUN mkdir -p /app/output
RUN chmod +x r_scripts/*.R

# Expose port for HTTP server
EXPOSE 8080

# Set environment variables for HTTP mode
ENV PYTHONPATH=/app
ENV PORT=8080
ENV HTTP_MODE=true
ENV HOST=0.0.0.0
ENV R_LIBS_USER=/usr/local/lib/R/site-library

# Health check using HTTP endpoint  
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the server in HTTP mode
CMD ["python", "-m", "meta_analysis_mcp_server"]

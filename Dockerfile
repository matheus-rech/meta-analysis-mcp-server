# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir mcp pydantic statsmodels seaborn kaleido

# Copy the application code
COPY meta_analysis_mcp_server/ ./meta_analysis_mcp_server/
COPY README.md ./

# Install the package
RUN pip install -e .

# Expose port (for web interface if needed)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import meta_analysis_mcp_server; print('OK')" || exit 1

# Run the server
CMD ["meta-analysis-mcp-server"]
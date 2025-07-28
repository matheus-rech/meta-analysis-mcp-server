FROM rocker/r-ver:4.3.0

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
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

RUN R -e "install.packages(c('meta', 'metafor', 'metaSEM', 'nloptr', 'xml2', 'lme4', 'jsonlite', 'DT', 'rmarkdown', 'knitr', 'ggplot2'), repos='https://cran.rstudio.com/', lib='/usr/local/lib/R/site-library')"

COPY requirements-deploy.txt .
RUN pip3 install --no-cache-dir -r requirements-deploy.txt

COPY . .

RUN chmod +x r_scripts/*.R

EXPOSE 8000

ENV PYTHONPATH=/app
ENV R_LIBS_USER=/usr/local/lib/R/site-library

CMD ["python3", "-c", "from extended_protocol_handler import ExtendedMCPProtocolHandler; import asyncio; import json; handler = ExtendedMCPProtocolHandler(); print('Meta-Analysis MCP Server with Cochrane Compliance Started'); print('Available tools:', len(asyncio.run(handler.handle_request({'method': 'tools/list'}))['tools'])); import time; time.sleep(3600)"]

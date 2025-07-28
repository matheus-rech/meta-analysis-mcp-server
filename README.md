# Meta-Analysis MCP Server with Cochrane Compliance

A comprehensive Model Context Protocol (MCP) server for conducting systematic reviews and meta-analyses following Cochrane Handbook guidelines and PRISMA 2020 reporting standards.

## 🎯 Features

### Original Meta-Analysis Tools (7)
- **initialize_meta_analysis**: Start new meta-analysis project with guided setup
- **upload_study_data**: Upload and validate study data with comprehensive checks
- **perform_meta_analysis**: Execute meta-analysis with automated statistical methods
- **generate_forest_plot**: Create publication-ready forest plots
- **assess_publication_bias**: Perform publication bias assessment with multiple tests
- **generate_report**: Create comprehensive meta-analysis reports
- **get_session_status**: Get current session status and generated files

### Cochrane Compliance Tools (4)
- **assess_risk_of_bias**: Cochrane ROB 2.0 risk of bias assessment
- **generate_prisma_checklist**: PRISMA 2020 compliance checklist with flowchart
- **perform_grade_assessment**: GRADE evidence quality assessment
- **generate_cochrane_report**: Comprehensive Cochrane-compliant systematic review report

## 🚀 Quick Start

### Local Development

1. **Install R Dependencies**
```bash
Rscript -e "install.packages(c('meta', 'metafor', 'metaSEM', 'nloptr', 'xml2', 'lme4', 'jsonlite', 'DT', 'rmarkdown', 'knitr', 'ggplot2'), repos='https://cran.rstudio.com/')"
```

2. **Install Python Dependencies**
```bash
pip install -r requirements-deploy.txt
```

3. **Run Demo Workflow**
```bash
python3 demo_cochrane_workflow.py
```

### Docker Deployment

```bash
docker build -t meta-analysis-mcp .
docker run -p 8000:8000 meta-analysis-mcp
```

## 🌐 Free Cloud Deployment Options

### Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Deploy using the included `railway.json` configuration
3. Automatic builds with Dockerfile

### Fly.io
```bash
flyctl launch --config fly.toml
flyctl deploy
```

### Heroku
```bash
heroku create your-app-name
heroku container:push web
heroku container:release web
```

## 📊 Usage Examples

### Basic Meta-Analysis Workflow
```python
from extended_protocol_handler import ExtendedMCPProtocolHandler
import asyncio
import json

async def basic_workflow():
    handler = ExtendedMCPProtocolHandler()
    
    # Initialize session
    init_response = await handler.handle_request({
        "method": "tools/call",
        "params": {
            "name": "initialize_meta_analysis",
            "arguments": {
                "user_id": "researcher_001",
                "project_name": "My Systematic Review",
                "study_type": "clinical_trial",
                "effect_measure": "OR"
            }
        }
    })
    
    session_data = json.loads(init_response["content"][0]["text"])
    session_id = session_data["session_id"]
    
    # Upload data and perform analysis...
```

### Cochrane Compliance Workflow
```python
# After basic meta-analysis, add Cochrane compliance
rob_response = await handler.handle_request({
    "method": "tools/call",
    "params": {
        "name": "assess_risk_of_bias",
        "arguments": {
            "session_id": session_id,
            "assessment_type": "automated",
            "rob_version": "rob2"
        }
    }
})

prisma_response = await handler.handle_request({
    "method": "tools/call",
    "params": {
        "name": "generate_prisma_checklist",
        "arguments": {
            "session_id": session_id,
            "review_type": "intervention",
            "include_flowchart": True
        }
    }
})
```

## 🏥 Cochrane Handbook Compliance

This server implements guidelines from:
- **Cochrane Handbook Chapter 8**: Risk of bias assessment using ROB 2.0
- **Cochrane Handbook Chapter 10**: Statistical analysis and meta-analysis methods
- **Cochrane Handbook Chapter 12**: Synthesis and presentation of results

## 📋 PRISMA 2020 Compliance

Includes full PRISMA 2020 checklist with:
- 27-item checklist for systematic reviews
- Flow diagram generation
- Compliance scoring and recommendations
- Integration with systematic review reporting

## 🔬 GRADE Evidence Assessment

Implements GRADE methodology for:
- Risk of bias evaluation
- Inconsistency assessment
- Indirectness evaluation
- Imprecision analysis
- Publication bias detection

## 📁 File Structure

```
meta_analysis_mcp/
├── mcp_server.py                    # Original MCP server (7 tools)
├── extended_mcp_server.py           # Extended server with Cochrane tools
├── extended_protocol_handler.py     # Protocol handler for extended server
├── cochrane_tools.py               # Cochrane compliance implementations
├── demo_workflow.py                # Original workflow demonstration
├── demo_cochrane_workflow.py       # Extended workflow demonstration
├── r_scripts/
│   └── meta_analysis.R             # R statistical analysis scripts
├── templates/
│   ├── report_template.Rmd         # Original report template
│   └── cochrane_report_template.Rmd # Cochrane-compliant template
├── sample_data.csv                 # Sample study data
├── Dockerfile                      # Container configuration
├── requirements-deploy.txt         # Python dependencies
├── railway.json                    # Railway deployment config
├── fly.toml                       # Fly.io deployment config
└── README.md                      # This file
```

## 🧪 Testing

### Test Original Functionality
```bash
python3 demo_workflow.py
```

### Test Cochrane Compliance Features
```bash
python3 demo_cochrane_workflow.py
```

### Test Individual Tools
```bash
python3 test_individual_tools.py
```

## 🤝 Contributing

This server maintains backward compatibility with all original functionality while adding Cochrane compliance features. When contributing:

1. Preserve all existing tool functionality
2. Follow Cochrane Handbook guidelines
3. Maintain PRISMA 2020 compliance
4. Include comprehensive testing

## 📚 References

1. Higgins JPT, Thomas J, Chandler J, et al. Cochrane Handbook for Systematic Reviews of Interventions version 6.3. Cochrane, 2022.
2. Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. BMJ 2021;372:n71.
3. Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. BMJ 2008;336:924-6.

## 📄 License

MIT License - see LICENSE file for details.

---

*Meta-Analysis MCP Server with Cochrane Compliance - Democratizing systematic reviews through guided workflows and automated R execution.*

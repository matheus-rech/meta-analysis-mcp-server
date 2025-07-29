# Meta-Analysis MCP Server

A Model Context Protocol (MCP) server for meta-analysis with comprehensive Cochrane compliance features and PRISMA 2020 reporting.

## Features

### Core Meta-Analysis Tools
- Statistical meta-analysis with forest plots
- Effect size calculations (standardized mean difference, odds ratio, etc.)
- Heterogeneity assessment (I², τ², Q-test)
- Publication bias detection (funnel plots, Egger's test)
- Subgroup analysis and meta-regression

### Cochrane Compliance Tools (New!)
1. **assess_risk_of_bias** - Cochrane ROB 2.0 risk of bias assessment
2. **generate_prisma_checklist** - PRISMA 2020 compliance checklist with 27 items
3. **perform_grade_assessment** - GRADE evidence quality assessment
4. **generate_cochrane_report** - Cochrane-compliant systematic review reports

## Installation

```bash
# Install from source
git clone https://github.com/matheus-rech/meta-analysis-mcp-server.git
cd meta-analysis-mcp-server
pip install -e .
```

## Usage

### Running the Server
```bash
meta-analysis-mcp-server
```

### MCP Client Configuration
Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "meta-analysis": {
      "command": "meta-analysis-mcp-server",
      "args": []
    }
  }
}
```

## Available Tools

### Core Meta-Analysis
- `perform_meta_analysis` - Conduct statistical meta-analysis
- `create_forest_plot` - Generate forest plots
- `assess_heterogeneity` - Evaluate between-study heterogeneity
- `detect_publication_bias` - Assess publication bias
- `perform_subgroup_analysis` - Conduct subgroup analyses

### Cochrane Compliance
- `assess_risk_of_bias` - ROB 2.0 assessment with automated and manual modes
- `generate_prisma_checklist` - PRISMA 2020 compliance with 90%+ scoring
- `perform_grade_assessment` - GRADE evidence quality evaluation
- `generate_cochrane_report` - Publication-ready Cochrane reports

## Deployment

### Docker
```bash
docker build -t meta-analysis-mcp-server .
docker run -p 8080:8080 meta-analysis-mcp-server
```

### Railway
Deploy directly from GitHub repository.

### Fly.io
```bash
fly deploy
```

## Development

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black .

# Type checking
mypy .
```

## License

MIT License. See LICENSE file for details.

## Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.
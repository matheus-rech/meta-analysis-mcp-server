# Meta-Analysis MCP Server Usage Guide

## Quick Start

### Installation
```bash
git clone https://github.com/matheus-rech/meta-analysis-mcp-server.git
cd meta-analysis-mcp-server
pip install -e .
```

### Basic Usage
```bash
# Start the MCP server
meta-analysis-mcp-server
```

## Tool Categories

### 1. Core Meta-Analysis Tools

#### `perform_meta_analysis`
Conduct statistical meta-analysis with effect size calculations.

**Parameters:**
- `studies`: Array of study data with `effect_size`, `standard_error`, `sample_size`
- `method`: "fixed" or "random" (default: "random")
- `measure`: Effect measure - "SMD", "MD", "OR", "RR", "RD" (default: "SMD")

**Example:**
```json
{
  "studies": [
    {
      "study_id": "Smith_2023",
      "effect_size": 0.5,
      "standard_error": 0.1,
      "sample_size": 100
    },
    {
      "study_id": "Jones_2022",
      "effect_size": 0.3,
      "standard_error": 0.12,
      "sample_size": 80
    }
  ],
  "method": "random",
  "measure": "SMD"
}
```

**Returns:**
- Pooled effect size with confidence intervals
- Heterogeneity statistics (I², τ², Q-test)
- Individual study results with weights
- Clinical interpretation

#### `create_forest_plot`
Generate forest plot visualizations.

**Parameters:**
- `studies`: Study data with `effect_size`, `ci_lower`, `ci_upper`, `weight`
- `title`: Plot title (optional)
- `output_format`: "png", "svg", or "html" (default: "png")

#### `assess_heterogeneity`
Evaluate between-study heterogeneity.

**Parameters:**
- `studies`: Study data with `effect_size` and `variance`

**Returns:**
- Q-statistic and p-value
- I² and τ² estimates
- Clinical interpretation and recommendations

#### `detect_publication_bias`
Assess publication bias using statistical tests and funnel plots.

**Parameters:**
- `studies`: Study data with `effect_size` and `standard_error`
- `tests`: Array of tests - "egger", "begg", "trim_fill" (default: ["egger"])

### 2. Cochrane Compliance Tools

#### `assess_risk_of_bias`
Cochrane ROB 2.0 risk of bias assessment with automated and manual modes.

**Parameters:**
- `studies`: Array of studies with metadata
- `assessment_mode`: "automated", "manual", or "hybrid" (default: "hybrid")
- `domains`: ROB domains to assess (default: all 5 domains)

**ROB Domains:**
1. `randomization` - Randomization process
2. `deviations` - Deviations from intended interventions
3. `missing_outcome_data` - Missing outcome data
4. `outcome_measurement` - Measurement of the outcome
5. `selective_reporting` - Selection of the reported result

**Example:**
```json
{
  "studies": [
    {
      "study_id": "RCT_001",
      "title": "Randomized trial of intervention X",
      "randomization_method": "Computer-generated sequence",
      "blinding": "Double-blind",
      "attrition_rate": 5.2
    }
  ],
  "assessment_mode": "automated"
}
```

#### `generate_prisma_checklist`
Generate PRISMA 2020 compliance checklist with 27 items and automated scoring.

**Parameters:**
- `review_data`: Systematic review metadata
- `generate_flow_diagram`: Generate PRISMA flow diagram (default: true)
- `screening_data`: Study screening numbers (optional)

**Required Review Data:**
- `title`: Review title
- `abstract`: Structured abstract
- `search_strategy`: Search methods
- `inclusion_criteria`: Study selection criteria
- `data_extraction`: Data extraction methods

**Example:**
```json
{
  "review_data": {
    "title": "Systematic review and meta-analysis of intervention X",
    "abstract": "Background: ... Objectives: ... Methods: ... Results: ... Conclusions: ...",
    "search_strategy": "MEDLINE, Embase, and Cochrane Library searched",
    "inclusion_criteria": "Randomized controlled trials"
  },
  "screening_data": {
    "records_identified": 2847,
    "records_screened": 847,
    "full_text_assessed": 23,
    "studies_included": 5
  }
}
```

**Returns:**
- Compliance score (percentage and grade)
- Item-by-item assessment
- PRISMA flow diagram
- Recommendations for improvement

#### `perform_grade_assessment`
GRADE evidence quality assessment with comprehensive bias evaluation.

**Parameters:**
- `evidence_profile`: Evidence data for assessment
- `assessment_criteria`: Which GRADE criteria to assess (optional)

**GRADE Domains:**
1. Risk of bias
2. Inconsistency
3. Indirectness
4. Imprecision
5. Publication bias

**Example:**
```json
{
  "evidence_profile": {
    "outcome": "Primary outcome measure",
    "studies": 5,
    "participants": 500,
    "study_design": "RCT",
    "risk_of_bias": "Some concerns",
    "inconsistency": "Moderate heterogeneity (I² = 45%)"
  }
}
```

**Returns:**
- Overall certainty rating (High, Moderate, Low, Very Low)
- Domain-specific downgrades
- Summary of findings table
- Clinical implications

#### `generate_cochrane_report`
Generate Cochrane-compliant systematic review report with publication-ready HTML output.

**Parameters:**
- `review_metadata`: Review content and metadata
- `analysis_results`: Meta-analysis results (optional)
- `rob_assessment`: Risk of bias results (optional)
- `prisma_checklist`: PRISMA checklist results (optional)
- `grade_assessment`: GRADE assessment results (optional)
- `output_format`: "html", "pdf", or "docx" (default: "html")

## Complete Workflow Example

### Step 1: Prepare Study Data
```python
studies = [
    {
        "study_id": "Johnson_2023",
        "effect_size": 0.45,
        "standard_error": 0.12,
        "sample_size": 150,
        "title": "RCT of cognitive therapy",
        "randomization_method": "Computer-generated",
        "blinding": "Double-blind",
        "attrition_rate": 8.2
    }
    # ... more studies
]
```

### Step 2: Perform Meta-Analysis
```json
{
  "tool": "perform_meta_analysis",
  "parameters": {
    "studies": [...],
    "method": "random",
    "measure": "SMD"
  }
}
```

### Step 3: Assess Risk of Bias
```json
{
  "tool": "assess_risk_of_bias",
  "parameters": {
    "studies": [...],
    "assessment_mode": "automated"
  }
}
```

### Step 4: Generate PRISMA Checklist
```json
{
  "tool": "generate_prisma_checklist",
  "parameters": {
    "review_data": {
      "title": "Systematic review of...",
      "abstract": "Structured abstract...",
      "search_strategy": "Database search...",
      "inclusion_criteria": "RCTs of..."
    }
  }
}
```

### Step 5: Perform GRADE Assessment
```json
{
  "tool": "perform_grade_assessment",
  "parameters": {
    "evidence_profile": {
      "outcome": "Primary outcome",
      "studies": 5,
      "participants": 790,
      "study_design": "RCT"
    }
  }
}
```

### Step 6: Generate Final Report
```json
{
  "tool": "generate_cochrane_report",
  "parameters": {
    "review_metadata": {...},
    "analysis_results": {...},
    "rob_assessment": {...},
    "prisma_checklist": {...},
    "grade_assessment": {...}
  }
}
```

## Compliance Scoring

### PRISMA 2020 Compliance
- **90%+**: A+ (Excellent) - Ready for publication
- **85-89%**: A (Very Good) - Minor improvements needed
- **80-84%**: B+ (Good) - Some improvements recommended
- **75-79%**: B (Satisfactory) - Several improvements needed
- **70-74%**: C+ (Acceptable) - Substantial improvements required
- **<70%**: Poor - Major revisions needed

### GRADE Certainty Levels
- **High**: Very confident in effect estimate
- **Moderate**: Moderately confident, true effect likely close to estimate
- **Low**: Limited confidence, true effect may be substantially different
- **Very Low**: Very little confidence in effect estimate

### Risk of Bias Categories
- **Low Risk**: Bias unlikely to affect results
- **Some Concerns**: Bias possible but unlikely to seriously alter results
- **High Risk**: Bias likely to seriously undermine confidence in results

## Integration with MCP Clients

### Claude Desktop Configuration
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

### Usage in Claude
```
I need to perform a meta-analysis of 5 RCTs examining the effectiveness of cognitive behavioral therapy for anxiety. Can you help me:

1. Perform the statistical meta-analysis
2. Assess risk of bias using Cochrane ROB 2.0
3. Generate a PRISMA 2020 checklist
4. Perform GRADE assessment
5. Create a Cochrane-compliant report

Here are my study data: [study details...]
```

## Advanced Features

### Custom Forest Plots
- Interactive Plotly-based visualizations
- Customizable styling and layout
- Support for subgroup analysis
- Export in multiple formats (PNG, SVG, HTML)

### Publication Bias Detection
- Egger's regression test
- Begg's rank correlation test
- Funnel plot generation
- Trim-and-fill analysis

### Heterogeneity Assessment
- Q-statistic and chi-square test
- I² statistic interpretation
- Tau-squared estimation
- Clinical significance assessment

### Automated ROB Assessment
- Rule-based assessment algorithms
- Confidence scoring
- Signaling question guidance
- Traffic light plot generation

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Empty Results**: Check study data format and required fields
3. **Low PRISMA Scores**: Review missing metadata fields
4. **ROB Assessment Errors**: Verify study design information

### Debug Mode
Set environment variable for detailed logging:
```bash
export LOG_LEVEL=DEBUG
meta-analysis-mcp-server
```

## Contributing

See [Contributing Guide](CONTRIBUTING.md) for development setup and contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
"""Base Meta-Analysis MCP Server."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Sequence

# Handle MCP import gracefully for development
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP not available - running in development mode")

from .tools.meta_analysis import MetaAnalysisTools
from .tools.cochrane_compliance import CochraneComplianceTools

logger = logging.getLogger(__name__)


class MetaAnalysisServer:
    """Base Meta-Analysis MCP Server."""

    def __init__(self):
        """Initialize the server."""
        self.server = Server("meta-analysis-mcp-server")
        self.meta_tools = MetaAnalysisTools()
        self.cochrane_tools = CochraneComplianceTools()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools."""
            tools = []
            
            # Core meta-analysis tools
            tools.extend([
                types.Tool(
                    name="perform_meta_analysis",
                    description="Perform statistical meta-analysis with effect size calculations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "studies": {
                                "type": "array",
                                "description": "Array of study data",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "study_id": {"type": "string"},
                                        "effect_size": {"type": "number"},
                                        "standard_error": {"type": "number"},
                                        "sample_size": {"type": "integer"},
                                        "weight": {"type": "number", "description": "Optional weight"}
                                    },
                                    "required": ["study_id", "effect_size", "standard_error", "sample_size"]
                                }
                            },
                            "method": {
                                "type": "string",
                                "enum": ["fixed", "random"],
                                "default": "random",
                                "description": "Meta-analysis method"
                            },
                            "measure": {
                                "type": "string",
                                "enum": ["SMD", "MD", "OR", "RR", "RD"],
                                "default": "SMD",
                                "description": "Effect measure"
                            }
                        },
                        "required": ["studies"]
                    }
                ),
                types.Tool(
                    name="create_forest_plot",
                    description="Generate forest plot visualization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "studies": {
                                "type": "array",
                                "description": "Array of study data for forest plot",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "study_id": {"type": "string"},
                                        "effect_size": {"type": "number"},
                                        "ci_lower": {"type": "number"},
                                        "ci_upper": {"type": "number"},
                                        "weight": {"type": "number"}
                                    },
                                    "required": ["study_id", "effect_size", "ci_lower", "ci_upper", "weight"]
                                }
                            },
                            "title": {"type": "string", "description": "Plot title"},
                            "output_format": {
                                "type": "string",
                                "enum": ["png", "svg", "html"],
                                "default": "png"
                            }
                        },
                        "required": ["studies"]
                    }
                ),
                types.Tool(
                    name="assess_heterogeneity",
                    description="Evaluate between-study heterogeneity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "studies": {
                                "type": "array",
                                "description": "Array of study data",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "study_id": {"type": "string"},
                                        "effect_size": {"type": "number"},
                                        "variance": {"type": "number"}
                                    },
                                    "required": ["study_id", "effect_size", "variance"]
                                }
                            }
                        },
                        "required": ["studies"]
                    }
                ),
                types.Tool(
                    name="detect_publication_bias",
                    description="Assess publication bias using funnel plots and statistical tests",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "studies": {
                                "type": "array",
                                "description": "Array of study data",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "study_id": {"type": "string"},
                                        "effect_size": {"type": "number"},
                                        "standard_error": {"type": "number"}
                                    },
                                    "required": ["study_id", "effect_size", "standard_error"]
                                }
                            },
                            "tests": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["egger", "begg", "trim_fill"]},
                                "default": ["egger"]
                            }
                        },
                        "required": ["studies"]
                    }
                )
            ])
            
            # Cochrane compliance tools
            tools.extend([
                types.Tool(
                    name="assess_risk_of_bias",
                    description="Cochrane ROB 2.0 risk of bias assessment with automated and manual modes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "studies": {
                                "type": "array",
                                "description": "Array of studies to assess",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "study_id": {"type": "string"},
                                        "title": {"type": "string"},
                                        "authors": {"type": "string"},
                                        "year": {"type": "integer"},
                                        "study_design": {"type": "string"},
                                        "randomization_method": {"type": "string"},
                                        "blinding": {"type": "string"},
                                        "outcome_assessment": {"type": "string"},
                                        "attrition_rate": {"type": "number"},
                                        "selective_reporting": {"type": "string"}
                                    },
                                    "required": ["study_id", "title"]
                                }
                            },
                            "assessment_mode": {
                                "type": "string",
                                "enum": ["automated", "manual", "hybrid"],
                                "default": "hybrid"
                            },
                            "domains": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "randomization",
                                        "deviations",
                                        "missing_outcome_data",
                                        "outcome_measurement",
                                        "selective_reporting"
                                    ]
                                },
                                "default": [
                                    "randomization",
                                    "deviations", 
                                    "missing_outcome_data",
                                    "outcome_measurement",
                                    "selective_reporting"
                                ]
                            }
                        },
                        "required": ["studies"]
                    }
                ),
                types.Tool(
                    name="generate_prisma_checklist",
                    description="Generate PRISMA 2020 compliance checklist with 27 items and automated scoring",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "review_data": {
                                "type": "object",
                                "description": "Systematic review metadata",
                                "properties": {
                                    "title": {"type": "string"},
                                    "abstract": {"type": "string"},
                                    "search_strategy": {"type": "string"},
                                    "inclusion_criteria": {"type": "string"},
                                    "exclusion_criteria": {"type": "string"},
                                    "data_extraction": {"type": "string"},
                                    "risk_of_bias": {"type": "string"},
                                    "statistical_analysis": {"type": "string"},
                                    "results_summary": {"type": "string"},
                                    "limitations": {"type": "string"},
                                    "conclusions": {"type": "string"},
                                    "funding": {"type": "string"},
                                    "conflicts_of_interest": {"type": "string"}
                                },
                                "required": ["title"]
                            },
                            "generate_flow_diagram": {
                                "type": "boolean",
                                "default": true
                            },
                            "screening_data": {
                                "type": "object",
                                "properties": {
                                    "records_identified": {"type": "integer"},
                                    "records_screened": {"type": "integer"},
                                    "full_text_assessed": {"type": "integer"},
                                    "studies_included": {"type": "integer"},
                                    "exclusion_reasons": {"type": "object"}
                                }
                            }
                        },
                        "required": ["review_data"]
                    }
                ),
                types.Tool(
                    name="perform_grade_assessment",
                    description="GRADE evidence quality assessment with comprehensive bias evaluation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "evidence_profile": {
                                "type": "object",
                                "description": "Evidence profile for GRADE assessment",
                                "properties": {
                                    "outcome": {"type": "string"},
                                    "studies": {"type": "integer"},
                                    "participants": {"type": "integer"},
                                    "study_design": {"type": "string"},
                                    "risk_of_bias": {"type": "string"},
                                    "inconsistency": {"type": "string"},
                                    "indirectness": {"type": "string"},
                                    "imprecision": {"type": "string"},
                                    "publication_bias": {"type": "string"},
                                    "effect_size": {"type": "number"},
                                    "confidence_interval": {"type": "string"}
                                },
                                "required": ["outcome", "studies", "participants"]
                            },
                            "assessment_criteria": {
                                "type": "object",
                                "properties": {
                                    "assess_risk_of_bias": {"type": "boolean", "default": true},
                                    "assess_inconsistency": {"type": "boolean", "default": true},
                                    "assess_indirectness": {"type": "boolean", "default": true},
                                    "assess_imprecision": {"type": "boolean", "default": true},
                                    "assess_publication_bias": {"type": "boolean", "default": true}
                                }
                            }
                        },
                        "required": ["evidence_profile"]
                    }
                ),
                types.Tool(
                    name="generate_cochrane_report",
                    description="Generate Cochrane-compliant systematic review report with publication-ready HTML output",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "review_metadata": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "authors": {"type": "array", "items": {"type": "string"}},
                                    "abstract": {"type": "string"},
                                    "background": {"type": "string"},
                                    "objectives": {"type": "string"},
                                    "methods": {"type": "string"},
                                    "results": {"type": "string"},
                                    "discussion": {"type": "string"},
                                    "conclusions": {"type": "string"},
                                    "references": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["title", "authors", "abstract"]
                            },
                            "analysis_results": {
                                "type": "object",
                                "description": "Meta-analysis results to include"
                            },
                            "rob_assessment": {
                                "type": "object",
                                "description": "Risk of bias assessment results"
                            },
                            "prisma_checklist": {
                                "type": "object",
                                "description": "PRISMA checklist results"
                            },
                            "grade_assessment": {
                                "type": "object", 
                                "description": "GRADE assessment results"
                            },
                            "output_format": {
                                "type": "string",
                                "enum": ["html", "pdf", "docx"],
                                "default": "html"
                            }
                        },
                        "required": ["review_metadata"]
                    }
                )
            ])
            
            return tools

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls."""
            if arguments is None:
                arguments = {}

            try:
                # Core meta-analysis tools
                if name == "perform_meta_analysis":
                    result = await self.meta_tools.perform_meta_analysis(**arguments)
                elif name == "create_forest_plot":
                    result = await self.meta_tools.create_forest_plot(**arguments)
                elif name == "assess_heterogeneity":
                    result = await self.meta_tools.assess_heterogeneity(**arguments)
                elif name == "detect_publication_bias":
                    result = await self.meta_tools.detect_publication_bias(**arguments)
                
                # Cochrane compliance tools
                elif name == "assess_risk_of_bias":
                    result = await self.cochrane_tools.assess_risk_of_bias(**arguments)
                elif name == "generate_prisma_checklist":
                    result = await self.cochrane_tools.generate_prisma_checklist(**arguments)
                elif name == "perform_grade_assessment":
                    result = await self.cochrane_tools.perform_grade_assessment(**arguments)
                elif name == "generate_cochrane_report":
                    result = await self.cochrane_tools.generate_cochrane_report(**arguments)
                
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self) -> None:
        """Run the server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="meta-analysis-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )


def main() -> None:
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)
    server = MetaAnalysisServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
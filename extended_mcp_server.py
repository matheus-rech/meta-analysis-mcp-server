#!/usr/bin/env python3

from mcp_server import MetaAnalysisMCPServer, MCPProtocolHandler
from cochrane_tools import CochraneComplianceHandler
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ExtendedMetaAnalysisMCPServer(MetaAnalysisMCPServer):
    """Extended MCP Server with Cochrane compliance features"""
    
    def __init__(self, work_dir: str = "/tmp/meta_analysis_sessions"):
        super().__init__(work_dir)
        self.cochrane_handler = CochraneComplianceHandler()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return all tools (original + Cochrane extensions)"""
        original_tools = super().get_tools()
        cochrane_tools = [
            {
                "name": "assess_risk_of_bias",
                "description": "Perform Cochrane risk of bias assessment following Cochrane Handbook Chapter 8",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "assessment_type": {"type": "string", "enum": ["automated", "manual"], "default": "automated"},
                        "rob_version": {"type": "string", "enum": ["rob2", "robins-i"], "default": "rob2"}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "generate_prisma_checklist",
                "description": "Generate PRISMA 2020 compliance checklist for systematic review reporting",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "review_type": {"type": "string", "enum": ["intervention", "diagnostic", "prognostic"], "default": "intervention"},
                        "include_flowchart": {"type": "boolean", "default": True}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "perform_grade_assessment",
                "description": "Conduct GRADE evidence quality assessment for systematic review outcomes",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "outcomes": {"type": "array", "items": {"type": "string"}},
                        "assessment_domains": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["risk_of_bias", "inconsistency", "indirectness", "imprecision", "publication_bias"]},
                            "default": ["risk_of_bias", "inconsistency", "indirectness", "imprecision", "publication_bias"]
                        }
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "generate_cochrane_report",
                "description": "Create comprehensive Cochrane-compliant systematic review report with PRISMA compliance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "format": {"type": "string", "enum": ["html", "pdf"], "default": "html"},
                        "include_rob_assessment": {"type": "boolean", "default": True},
                        "include_grade_tables": {"type": "boolean", "default": True},
                        "include_prisma_checklist": {"type": "boolean", "default": True}
                    },
                    "required": ["session_id"]
                }
            }
        ]
        return original_tools + cochrane_tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool calls to appropriate handlers"""
        
        if tool_name == "assess_risk_of_bias":
            return await self._assess_risk_of_bias(arguments)
        elif tool_name == "generate_prisma_checklist":
            return await self._generate_prisma_checklist(arguments)
        elif tool_name == "perform_grade_assessment":
            return await self._perform_grade_assessment(arguments)
        elif tool_name == "generate_cochrane_report":
            return await self._generate_cochrane_report(arguments)
        else:
            return await super().call_tool(tool_name, arguments)
    
    async def _assess_risk_of_bias(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform risk of bias assessment using Cochrane guidelines"""
        session_id = args["session_id"]
        
        if session_id not in self.sessions:
            return {"error": f"Session {session_id} not found"}
        
        session = self.sessions[session_id]
        session_dir = self.work_dir / session_id
        
        try:
            assessment_type = args.get("assessment_type", "automated")
            rob_version = args.get("rob_version", "rob2")
            
            data_file = session_dir / "input" / "study_data.csv"
            if not data_file.exists():
                return {"error": "No study data found. Please upload data first."}
            
            assessment_result = await self.cochrane_handler.assess_risk_of_bias(
                str(data_file), assessment_type, rob_version
            )
            
            output_file = session_dir / "output" / "risk_of_bias_assessment.json"
            with open(output_file, 'w') as f:
                json.dump(assessment_result, f, indent=2)
            
            session.files["generated"].append(str(output_file))
            session.workflow_stage = "risk_assessment_completed"
            
            return {
                "message": f"Risk of bias assessment completed using {rob_version.upper()}",
                "assessment_file": str(output_file),
                "summary": assessment_result.get("summary", {}),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Risk of bias assessment failed: {str(e)}")
            return {"error": f"Risk of bias assessment failed: {str(e)}"}
    
    async def _generate_prisma_checklist(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PRISMA 2020 compliance checklist"""
        session_id = args["session_id"]
        
        if session_id not in self.sessions:
            return {"error": f"Session {session_id} not found"}
        
        session = self.sessions[session_id]
        session_dir = self.work_dir / session_id
        
        try:
            review_type = args.get("review_type", "intervention")
            include_flowchart = args.get("include_flowchart", True)
            
            checklist_result = await self.cochrane_handler.generate_prisma_checklist(
                session_id, review_type, include_flowchart
            )
            
            output_file = session_dir / "output" / "prisma_checklist.json"
            with open(output_file, 'w') as f:
                json.dump(checklist_result, f, indent=2)
            
            if include_flowchart:
                flowchart_file = session_dir / "output" / "prisma_flowchart.html"
                with open(flowchart_file, 'w') as f:
                    f.write(checklist_result.get("flowchart_html", ""))
                session.files["generated"].append(str(flowchart_file))
            
            session.files["generated"].append(str(output_file))
            
            return {
                "message": f"PRISMA 2020 checklist generated for {review_type} review",
                "checklist_file": str(output_file),
                "flowchart_file": str(flowchart_file) if include_flowchart else None,
                "compliance_score": checklist_result.get("compliance_score", 0),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"PRISMA checklist generation failed: {str(e)}")
            return {"error": f"PRISMA checklist generation failed: {str(e)}"}
    
    async def _perform_grade_assessment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform GRADE evidence quality assessment"""
        session_id = args["session_id"]
        
        if session_id not in self.sessions:
            return {"error": f"Session {session_id} not found"}
        
        session = self.sessions[session_id]
        session_dir = self.work_dir / session_id
        
        try:
            outcomes = args.get("outcomes", ["Primary outcome"])
            assessment_domains = args.get("assessment_domains", 
                ["risk_of_bias", "inconsistency", "indirectness", "imprecision", "publication_bias"])
            
            results_file = session_dir / "output" / "meta_analysis_results.json"
            if not results_file.exists():
                return {"error": "No meta-analysis results found. Please perform meta-analysis first."}
            
            grade_result = await self.cochrane_handler.perform_grade_assessment(
                str(results_file), outcomes, assessment_domains
            )
            
            output_file = session_dir / "output" / "grade_assessment.json"
            with open(output_file, 'w') as f:
                json.dump(grade_result, f, indent=2)
            
            session.files["generated"].append(str(output_file))
            
            return {
                "message": f"GRADE assessment completed for {len(outcomes)} outcome(s)",
                "grade_file": str(output_file),
                "evidence_quality": grade_result.get("overall_quality", "Unknown"),
                "recommendations": grade_result.get("recommendations", []),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"GRADE assessment failed: {str(e)}")
            return {"error": f"GRADE assessment failed: {str(e)}"}
    
    async def _generate_cochrane_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive Cochrane-compliant report"""
        session_id = args["session_id"]
        
        if session_id not in self.sessions:
            return {"error": f"Session {session_id} not found"}
        
        session = self.sessions[session_id]
        session_dir = self.work_dir / session_id
        
        try:
            format_type = args.get("format", "html")
            include_rob = args.get("include_rob_assessment", True)
            include_grade = args.get("include_grade_tables", True)
            include_prisma = args.get("include_prisma_checklist", True)
            
            template_file = self.templates_dir / "cochrane_report_template.Rmd"
            if not template_file.exists():
                return {"error": "Cochrane report template not found"}
            
            output_file = session_dir / "output" / f"cochrane_systematic_review.{format_type}"
            
            r_script = f"""
library(rmarkdown)
.libPaths(c("~/R/library", .libPaths()))

render(
    input = "{template_file}",
    output_file = "{output_file}",
    output_format = "{format_type}_document",
    params = list(
        session_id = "{session_id}",
        include_rob = {str(include_rob).lower()},
        include_grade = {str(include_grade).lower()},
        include_prisma = {str(include_prisma).lower()}
    )
)
"""
            
            r_script_file = session_dir / "processing" / "generate_cochrane_report.R"
            with open(r_script_file, 'w') as f:
                f.write(r_script)
            
            result = subprocess.run(
                ["Rscript", str(r_script_file)],
                cwd=str(session_dir),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                return {"error": f"Report generation failed: {result.stderr}"}
            
            session.files["generated"].append(str(output_file))
            session.workflow_stage = "cochrane_report_completed"
            
            return {
                "message": f"Cochrane-compliant systematic review report generated",
                "file_path": str(output_file),
                "format": format_type,
                "includes": {
                    "risk_of_bias": include_rob,
                    "grade_tables": include_grade,
                    "prisma_checklist": include_prisma
                },
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Cochrane report generation failed: {str(e)}")
            return {"error": f"Cochrane report generation failed: {str(e)}"}

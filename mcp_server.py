#!/usr/bin/env python3

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import uuid
import subprocess
import tempfile
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MetaAnalysisSession:
    """Represents a meta-analysis session"""
    id: str
    user_id: str
    project_name: str
    created_at: datetime
    status: str
    workflow_stage: str
    files: Dict[str, List[str]]
    parameters: Dict[str, Any]
    results: Dict[str, Any]

class MetaAnalysisMCPServer:
    """MCP Server for Meta-Analysis"""
    
    def __init__(self, work_dir: str = "/tmp/meta_analysis_sessions"):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        self.sessions: Dict[str, MetaAnalysisSession] = {}
        self.r_scripts_dir = Path(__file__).parent / "r_scripts"
        self.templates_dir = Path(__file__).parent / "templates"
        
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return available MCP tools"""
        return [
            {
                "name": "initialize_meta_analysis",
                "description": "Start new meta-analysis project with guided setup",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "project_name": {"type": "string"},
                        "study_type": {"type": "string", "enum": ["clinical_trial", "observational", "diagnostic"]},
                        "effect_measure": {"type": "string", "enum": ["OR", "RR", "MD", "SMD", "HR"]},
                        "analysis_model": {"type": "string", "enum": ["fixed", "random", "auto"]}
                    },
                    "required": ["user_id", "project_name", "study_type", "effect_measure"]
                }
            },
            {
                "name": "upload_study_data",
                "description": "Upload and validate study data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "data_content": {"type": "string"},
                        "data_format": {"type": "string", "enum": ["csv", "excel", "json"]},
                        "validation_level": {"type": "string", "enum": ["basic", "comprehensive"], "default": "basic"}
                    },
                    "required": ["session_id", "data_content", "data_format"]
                }
            },
            {
                "name": "perform_meta_analysis",
                "description": "Execute meta-analysis with automated checks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "heterogeneity_test": {"type": "boolean", "default": True},
                        "publication_bias": {"type": "boolean", "default": True},
                        "sensitivity_analysis": {"type": "boolean", "default": False}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "generate_forest_plot",
                "description": "Create publication-ready forest plot",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "plot_style": {"type": "string", "enum": ["classic", "modern"], "default": "modern"},
                        "confidence_level": {"type": "number", "default": 0.95},
                        "title": {"type": "string", "default": "Forest Plot"}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "assess_publication_bias",
                "description": "Perform publication bias assessment",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "methods": {
                            "type": "array", 
                            "items": {"type": "string", "enum": ["funnel_plot", "egger_test", "begg_test"]},
                            "default": ["funnel_plot", "egger_test"]
                        }
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "generate_report",
                "description": "Create comprehensive meta-analysis report",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "format": {"type": "string", "enum": ["html", "pdf"], "default": "html"},
                        "include_code": {"type": "boolean", "default": False}
                    },
                    "required": ["session_id"]
                }
            },
            {
                "name": "get_session_status",
                "description": "Get current session status and files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"}
                    },
                    "required": ["session_id"]
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        try:
            if tool_name == "initialize_meta_analysis":
                return await self._initialize_meta_analysis(arguments)
            elif tool_name == "upload_study_data":
                return await self._upload_study_data(arguments)
            elif tool_name == "perform_meta_analysis":
                return await self._perform_meta_analysis(arguments)
            elif tool_name == "generate_forest_plot":
                return await self._generate_forest_plot(arguments)
            elif tool_name == "assess_publication_bias":
                return await self._assess_publication_bias(arguments)
            elif tool_name == "generate_report":
                return await self._generate_report(arguments)
            elif tool_name == "get_session_status":
                return await self._get_session_status(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": str(e)}
    
    async def _initialize_meta_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a new meta-analysis session"""
        session_id = str(uuid.uuid4())
        session_dir = self.work_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        (session_dir / "input").mkdir(exist_ok=True)
        (session_dir / "processing").mkdir(exist_ok=True)
        (session_dir / "output").mkdir(exist_ok=True)
        (session_dir / "logs").mkdir(exist_ok=True)
        
        session = MetaAnalysisSession(
            id=session_id,
            user_id=args["user_id"],
            project_name=args["project_name"],
            created_at=datetime.now(),
            status="initialized",
            workflow_stage="setup",
            files={"uploaded": [], "generated": []},
            parameters={
                "study_type": args["study_type"],
                "effect_measure": args["effect_measure"],
                "analysis_model": args.get("analysis_model", "random")
            },
            results={}
        )
        
        self.sessions[session_id] = session
        
        return {
            "success": True,
            "session_id": session_id,
            "message": f"Meta-analysis session initialized for project: {args['project_name']}",
            "parameters": session.parameters,
            "next_step": "upload_study_data"
        }
    
    async def _upload_study_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Upload and validate study data"""
        session_id = args["session_id"]
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        session_dir = self.work_dir / session_id
        
        data_file = session_dir / "input" / f"study_data.{args['data_format']}"
        
        if args["data_format"] == "csv":
            try:
                import io
                df = pd.read_csv(io.StringIO(args["data_content"]))
                df.to_csv(data_file, index=False)
            except Exception as e:
                return {"error": f"Failed to parse CSV data: {str(e)}"}
        else:
            with open(data_file, 'w') as f:
                f.write(args["data_content"])
        
        validation_result = await self._validate_data(data_file, session.parameters, args.get("validation_level", "basic"))
        
        session.files["uploaded"].append(str(data_file.name))
        session.workflow_stage = "data_uploaded"
        session.status = "data_ready" if validation_result["valid"] else "validation_errors"
        
        return {
            "success": True,
            "message": "Data uploaded successfully",
            "validation": validation_result,
            "next_step": "perform_meta_analysis" if validation_result["valid"] else "fix_data_issues"
        }
    
    async def _validate_data(self, data_file: Path, parameters: Dict[str, Any], level: str) -> Dict[str, Any]:
        """Validate uploaded data"""
        try:
            df = pd.read_csv(data_file)
            
            validation = {
                "valid": True,
                "warnings": [],
                "errors": [],
                "summary": {
                    "n_studies": len(df),
                    "columns": list(df.columns)
                }
            }
            
            required_columns = ["study_id", "effect_size", "se", "n_treatment", "n_control"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                validation["errors"].append(f"Missing required columns: {missing_columns}")
                validation["valid"] = False
            
            if df.isnull().any().any():
                validation["warnings"].append("Dataset contains missing values")
            
            if "n_treatment" in df.columns and "n_control" in df.columns:
                small_samples = df[(df["n_treatment"] < 10) | (df["n_control"] < 10)]
                if len(small_samples) > 0:
                    validation["warnings"].append(f"{len(small_samples)} studies have small sample sizes (<10)")
            
            effect_measure = parameters.get("effect_measure", "OR")
            if effect_measure in ["OR", "RR"] and "effect_size" in df.columns:
                if any(df["effect_size"] <= 0):
                    validation["errors"].append("Odds ratios and risk ratios must be positive")
                    validation["valid"] = False
            
            return validation
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to validate data: {str(e)}"],
                "warnings": [],
                "summary": {}
            }
    
    async def _perform_meta_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Perform meta-analysis using R"""
        session_id = args["session_id"]
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        session_dir = self.work_dir / session_id
        
        r_script = self._generate_r_analysis_script(session, args)
        script_file = session_dir / "processing" / "analysis.R"
        
        with open(script_file, 'w') as f:
            f.write(r_script)
        
        try:
            result = subprocess.run(
                ["Rscript", str(script_file)],
                cwd=str(session_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "R analysis failed",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }
            
            results_file = session_dir / "processing" / "results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    analysis_results = json.load(f)
            else:
                analysis_results = {"message": "Analysis completed but no results file generated"}
            
            session.results = analysis_results
            session.workflow_stage = "analysis_complete"
            session.status = "ready_for_visualization"
            
            return {
                "success": True,
                "message": "Meta-analysis completed successfully",
                "results": analysis_results,
                "next_step": "generate_forest_plot"
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "R analysis timed out"}
        except Exception as e:
            return {"error": f"Failed to execute R analysis: {str(e)}"}
    
    def _generate_r_analysis_script(self, session: MetaAnalysisSession, args: Dict[str, Any]) -> str:
        """Generate R script for meta-analysis"""
        script = f"""
library(meta)
library(metafor)
library(jsonlite)

.libPaths(c("~/R/library", .libPaths()))

data <- read.csv("input/study_data.csv")

effect_measure <- "{session.parameters['effect_measure']}"
analysis_model <- "{session.parameters['analysis_model']}"

if (effect_measure %in% c("OR", "RR")) {{
    if (analysis_model == "fixed") {{
        ma_result <- metabin(
            event.e = events_treatment,
            n.e = n_treatment,
            event.c = events_control,
            n.c = n_control,
            data = data,
            studlab = study_id,
            sm = effect_measure,
            method = "Inverse"
        )
    }} else {{
        ma_result <- metabin(
            event.e = events_treatment,
            n.e = n_treatment,
            event.c = events_control,
            n.c = n_control,
            data = data,
            studlab = study_id,
            sm = effect_measure,
            method = "DL"
        )
    }}
}} else if (effect_measure %in% c("MD", "SMD")) {{
    if (analysis_model == "fixed") {{
        ma_result <- metacont(
            n.e = n_treatment,
            mean.e = mean_treatment,
            sd.e = sd_treatment,
            n.c = n_control,
            mean.c = mean_control,
            sd.c = sd_control,
            data = data,
            studlab = study_id,
            sm = effect_measure,
            method.tau = "FE"
        )
    }} else {{
        ma_result <- metacont(
            n.e = n_treatment,
            mean.e = mean_treatment,
            sd.e = sd_treatment,
            n.c = n_control,
            mean.c = mean_control,
            sd.c = sd_control,
            data = data,
            studlab = study_id,
            sm = effect_measure,
            method.tau = "DL"
        )
    }}
}} else {{
    ma_result <- metagen(
        TE = log(effect_size),
        seTE = se,
        data = data,
        studlab = study_id,
        sm = effect_measure
    )
}}

results <- list(
    summary = list(
        n_studies = ma_result$k,
        effect_size = ma_result$TE.fixed,
        se = ma_result$seTE.fixed,
        ci_lower = ma_result$lower.fixed,
        ci_upper = ma_result$upper.fixed,
        p_value = ma_result$pval.fixed,
        heterogeneity = list(
            tau2 = ma_result$tau2,
            I2 = ma_result$I2,
            H = ma_result$H,
            Q = ma_result$Q,
            p_heterogeneity = ma_result$pval.Q
        )
    ),
    individual_studies = data.frame(
        study = ma_result$studlab,
        effect = ma_result$TE,
        se = ma_result$seTE,
        weight = ma_result$w.fixed
    )
)

write_json(results, "processing/results.json", pretty = TRUE)

save.image("processing/analysis_workspace.RData")

cat("Meta-analysis completed successfully\\n")
"""
        return script
    
    async def _generate_forest_plot(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate forest plot"""
        session_id = args["session_id"]
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        session_dir = self.work_dir / session_id
        
        r_script = f"""
library(meta)
library(ggplot2)

.libPaths(c("~/R/library", .libPaths()))

load("processing/analysis_workspace.RData")

png("output/forest_plot.png", width = 800, height = 600, res = 300)
forest(ma_result, 
       main = "{args.get('title', 'Forest Plot')}",
       xlab = "Effect Size",
       comb.fixed = TRUE,
       comb.random = TRUE)
dev.off()

cat("Forest plot generated successfully\\n")
"""
        
        script_file = session_dir / "processing" / "forest_plot.R"
        with open(script_file, 'w') as f:
            f.write(r_script)
        
        try:
            result = subprocess.run(
                ["Rscript", str(script_file)],
                cwd=str(session_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Forest plot generation failed",
                    "stderr": result.stderr
                }
            
            plot_file = session_dir / "output" / "forest_plot.png"
            if plot_file.exists():
                session.files["generated"].append("forest_plot.png")
                return {
                    "success": True,
                    "message": "Forest plot generated successfully",
                    "file": str(plot_file),
                    "next_step": "assess_publication_bias"
                }
            else:
                return {"error": "Forest plot file not created"}
                
        except Exception as e:
            return {"error": f"Failed to generate forest plot: {str(e)}"}
    
    async def _assess_publication_bias(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Assess publication bias"""
        session_id = args["session_id"]
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        session_dir = self.work_dir / session_id
        
        methods = args.get("methods", ["funnel_plot", "egger_test"])
        
        r_script = f"""
library(meta)
library(metafor)

.libPaths(c("~/R/library", .libPaths()))

load("processing/analysis_workspace.RData")

bias_results <- list()

if ("funnel_plot" %in% c({', '.join([f'"{m}"' for m in methods])})) {{
    png("output/funnel_plot.png", width = 600, height = 600, res = 300)
    funnel(ma_result, main = "Funnel Plot")
    dev.off()
    bias_results$funnel_plot <- "Generated"
}}

if ("egger_test" %in% c({', '.join([f'"{m}"' for m in methods])})) {{
    egger_result <- metabias(ma_result, method = "linreg")
    bias_results$egger_test <- list(
        statistic = egger_result$statistic,
        p_value = egger_result$p.value,
        interpretation = ifelse(egger_result$p.value < 0.05, "Significant bias detected", "No significant bias")
    )
}}

if ("begg_test" %in% c({', '.join([f'"{m}"' for m in methods])})) {{
    begg_result <- metabias(ma_result, method = "rank")
    bias_results$begg_test <- list(
        statistic = begg_result$statistic,
        p_value = begg_result$p.value,
        interpretation = ifelse(begg_result$p.value < 0.05, "Significant bias detected", "No significant bias")
    )
}}

library(jsonlite)
write_json(bias_results, "processing/bias_results.json", pretty = TRUE)

cat("Publication bias assessment completed\\n")
"""
        
        script_file = session_dir / "processing" / "bias_assessment.R"
        with open(script_file, 'w') as f:
            f.write(r_script)
        
        try:
            result = subprocess.run(
                ["Rscript", str(script_file)],
                cwd=str(session_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Publication bias assessment failed",
                    "stderr": result.stderr
                }
            
            results_file = session_dir / "processing" / "bias_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    bias_results = json.load(f)
                
                if "funnel_plot" in methods:
                    session.files["generated"].append("funnel_plot.png")
                
                return {
                    "success": True,
                    "message": "Publication bias assessment completed",
                    "results": bias_results,
                    "next_step": "generate_report"
                }
            else:
                return {"error": "Bias assessment results not found"}
                
        except Exception as e:
            return {"error": f"Failed to assess publication bias: {str(e)}"}
    
    async def _generate_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report"""
        session_id = args["session_id"]
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        session_dir = self.work_dir / session_id
        
        rmd_content = f"""---
title: "Meta-Analysis Report: {session.project_name}"
author: "Meta-Analysis MCP Server"
date: "`r Sys.Date()`"
output: html_document
---

```{{r setup, include=FALSE}}
knitr::opts_chunk$set(echo = {str(args.get('include_code', False)).lower()}, warning = FALSE, message = FALSE)
.libPaths(c("~/R/library", .libPaths()))
library(meta)
library(knitr)
library(jsonlite)
```


- **Project**: {session.project_name}
- **Study Type**: {session.parameters['study_type']}
- **Effect Measure**: {session.parameters['effect_measure']}
- **Analysis Model**: {session.parameters['analysis_model']}

```{{r load_data}}
load("processing/analysis_workspace.RData")
results <- fromJSON("processing/results.json")
```


```{{r summary}}
cat("Number of studies:", results$summary$n_studies, "\\n")
cat("Overall effect size:", round(results$summary$effect_size, 3), "\\n")
cat("95% CI: [", round(results$summary$ci_lower, 3), ", ", round(results$summary$ci_upper, 3), "]\\n")
cat("P-value:", round(results$summary$p_value, 4), "\\n")
cat("I² heterogeneity:", round(results$summary$heterogeneity$I2, 1), "%\\n")
```


```{{r forest_plot, fig.width=10, fig.height=8}}
forest(ma_result, main = "Forest Plot")
```


```{{r funnel_plot, fig.width=8, fig.height=6}}
if (file.exists("output/funnel_plot.png")) {{
    knitr::include_graphics("output/funnel_plot.png")
}} else {{
    funnel(ma_result, main = "Funnel Plot")
}}
```


```{{r individual_studies}}
kable(results$individual_studies, digits = 3, caption = "Individual Study Results")
```

---
*Report generated on `r Sys.Date()` using Meta-Analysis MCP Server*
"""
        
        rmd_file = session_dir / "output" / "report.Rmd"
        with open(rmd_file, 'w') as f:
            f.write(rmd_content)
        
        r_script = f"""
library(rmarkdown)
.libPaths(c("~/R/library", .libPaths()))
render("output/report.Rmd", output_format = "{args.get('format', 'html')}_document")
"""
        
        script_file = session_dir / "processing" / "render_report.R"
        with open(script_file, 'w') as f:
            f.write(r_script)
        
        try:
            result = subprocess.run(
                ["Rscript", str(script_file)],
                cwd=str(session_dir),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Report generation failed",
                    "stderr": result.stderr
                }
            
            report_file = session_dir / "output" / f"report.{args.get('format', 'html')}"
            if report_file.exists():
                session.files["generated"].append(f"report.{args.get('format', 'html')}")
                session.workflow_stage = "complete"
                session.status = "finished"
                
                return {
                    "success": True,
                    "message": "Report generated successfully",
                    "file": str(report_file),
                    "session_complete": True
                }
            else:
                return {"error": "Report file not created"}
                
        except Exception as e:
            return {"error": f"Failed to generate report: {str(e)}"}
    
    async def _get_session_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get session status"""
        session_id = args["session_id"]
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session.id,
            "project_name": session.project_name,
            "status": session.status,
            "workflow_stage": session.workflow_stage,
            "created_at": session.created_at.isoformat(),
            "parameters": session.parameters,
            "files": session.files,
            "results_available": bool(session.results)
        }

class MCPProtocolHandler:
    """Handles MCP protocol communication"""
    
    def __init__(self):
        self.server = MetaAnalysisMCPServer()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        try:
            if request.get("method") == "tools/list":
                return {
                    "tools": self.server.get_tools()
                }
            elif request.get("method") == "tools/call":
                tool_name = request["params"]["name"]
                arguments = request["params"].get("arguments", {})
                result = await self.server.call_tool(tool_name, arguments)
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            else:
                return {"error": f"Unknown method: {request.get('method')}"}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    async def test_server():
        handler = MCPProtocolHandler()
        
        tools_response = await handler.handle_request({"method": "tools/list"})
        print("Available tools:")
        for tool in tools_response["tools"]:
            print(f"- {tool['name']}: {tool['description']}")
        
        init_request = {
            "method": "tools/call",
            "params": {
                "name": "initialize_meta_analysis",
                "arguments": {
                    "user_id": "test_user",
                    "project_name": "Test Meta-Analysis",
                    "study_type": "clinical_trial",
                    "effect_measure": "OR"
                }
            }
        }
        
        init_response = await handler.handle_request(init_request)
        print("\nInitialization response:")
        print(init_response["content"][0]["text"])
    
    asyncio.run(test_server())

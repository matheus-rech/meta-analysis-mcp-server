#!/usr/bin/env python3

from extended_mcp_server import ExtendedMetaAnalysisMCPServer
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ExtendedMCPProtocolHandler:
    """Extended Protocol Handler with Cochrane compliance"""
    
    def __init__(self):
        self.server = ExtendedMetaAnalysisMCPServer()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        try:
            method = request.get("method")
            
            if method == "tools/list":
                tools = self.server.get_tools()
                return {
                    "tools": tools
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = await self.server.call_tool(tool_name, arguments)
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            
            else:
                return {"error": f"Unknown method: {method}"}
                
        except Exception as e:
            logger.error(f"Request handling failed: {str(e)}")
            return {"error": str(e)}

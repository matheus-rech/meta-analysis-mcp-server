"""HTTP server wrapper for Meta-Analysis MCP Server."""

import asyncio
import json
import logging
from typing import Any, Dict
from aiohttp import web, web_request, web_response
import aiohttp_cors
from .server import MetaAnalysisServer

logger = logging.getLogger(__name__)


class HTTPMetaAnalysisServer:
    """HTTP wrapper for Meta-Analysis MCP Server."""

    def __init__(self):
        """Initialize the HTTP server."""
        self.mcp_server = MetaAnalysisServer()
        self.app = web.Application()
        self._setup_routes()
        self._setup_cors()

    def _setup_cors(self):
        """Setup CORS for the application."""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)

    def _setup_routes(self):
        """Setup HTTP routes."""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/', self.index)
        self.app.router.add_post('/mcp', self.handle_mcp_request)
        self.app.router.add_get('/tools', self.list_tools)
        self.app.router.add_post('/tools/{tool_name}', self.call_tool)

    async def health_check(self, request: web_request.Request) -> web_response.Response:
        """Health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "service": "meta-analysis-mcp-server",
            "version": "1.0.0"
        })

    async def index(self, request: web_request.Request) -> web_response.Response:
        """Index endpoint with server information."""
        return web.json_response({
            "name": "Meta-Analysis MCP Server",
            "version": "1.0.0",
            "description": "Statistical meta-analysis and Cochrane compliance tools",
            "endpoints": {
                "health": "/health",
                "tools": "/tools",
                "mcp": "/mcp"
            },
            "tools_count": 11,
            "capabilities": [
                "meta-analysis",
                "forest-plots", 
                "heterogeneity-assessment",
                "publication-bias-detection",
                "cochrane-rob-assessment",
                "prisma-checklist",
                "grade-assessment",
                "cochrane-reports"
            ]
        })

    async def list_tools(self, request: web_request.Request) -> web_response.Response:
        """List available MCP tools."""
        try:
            tools = await self.mcp_server._setup_handlers.__wrapped__(self.mcp_server)
            tools_list = []
            
            for tool in tools:
                tools_list.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                })
            
            return web.json_response({
                "tools": tools_list,
                "count": len(tools_list)
            })
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return web.json_response(
                {"error": f"Failed to list tools: {str(e)}"}, 
                status=500
            )

    async def call_tool(self, request: web_request.Request) -> web_response.Response:
        """Call a specific MCP tool."""
        tool_name = request.match_info['tool_name']
        
        try:
            if request.content_type == 'application/json':
                arguments = await request.json()
            else:
                arguments = {}
            
            result = await self.mcp_server._setup_handlers.__wrapped__(self.mcp_server)
            
            handler = getattr(self.mcp_server, '_setup_handlers', None)
            if handler:
                if hasattr(self.mcp_server.meta_tools, tool_name):
                    method = getattr(self.mcp_server.meta_tools, tool_name)
                    result = await method(**arguments)
                elif hasattr(self.mcp_server.cochrane_tools, tool_name):
                    method = getattr(self.mcp_server.cochrane_tools, tool_name)
                    result = await method(**arguments)
                else:
                    return web.json_response(
                        {"error": f"Tool '{tool_name}' not found"}, 
                        status=404
                    )
                
                return web.json_response({
                    "tool": tool_name,
                    "result": result,
                    "success": True
                })
            else:
                return web.json_response(
                    {"error": "MCP server not properly initialized"}, 
                    status=500
                )
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return web.json_response(
                {"error": f"Tool execution failed: {str(e)}"}, 
                status=500
            )

    async def handle_mcp_request(self, request: web_request.Request) -> web_response.Response:
        """Handle MCP protocol requests over HTTP."""
        try:
            rpc_request = await request.json()
            
            if not isinstance(rpc_request, dict) or 'method' not in rpc_request:
                return web.json_response(
                    {"error": "Invalid JSON-RPC request"}, 
                    status=400
                )
            
            method = rpc_request['method']
            params = rpc_request.get('params', {})
            request_id = rpc_request.get('id')
            
            if method == 'tools/list':
                tools = await self.mcp_server._setup_handlers.__wrapped__(self.mcp_server)
                tools_data = []
                for tool in tools:
                    tools_data.append({
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    })
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools_data}
                }
                
            elif method == 'tools/call':
                tool_name = params.get('name')
                arguments = params.get('arguments', {})
                
                response = {
                    "jsonrpc": "2.0", 
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": "MCP tool call not fully implemented"}]}
                }
                
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"}
                }
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return web.json_response({
                "jsonrpc": "2.0",
                "id": rpc_request.get('id') if 'rpc_request' in locals() else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }, status=500)

    async def start_server(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the HTTP server."""
        logger.info(f"Starting Meta-Analysis MCP HTTP Server on {host}:{port}")
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"Server started successfully on http://{host}:{port}")
        logger.info("Available endpoints:")
        logger.info("  GET  /health - Health check")
        logger.info("  GET  / - Server information")
        logger.info("  GET  /tools - List available tools")
        logger.info("  POST /tools/{tool_name} - Call specific tool")
        logger.info("  POST /mcp - MCP protocol endpoint")
        
        return runner


async def main():
    """Main entry point for HTTP server."""
    import os
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    server = HTTPMetaAnalysisServer()
    runner = await server.start_server(host, port)
    
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

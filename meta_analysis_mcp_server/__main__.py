"""Main entry point for meta-analysis MCP server package."""

import os
import asyncio
from .server import main as stdio_main
from .http_server import main as http_main

def main():
    """Main entry point - choose between stdio and HTTP mode."""
    if os.getenv("HTTP_MODE", "false").lower() == "true" or os.getenv("PORT"):
        asyncio.run(http_main())
    else:
        stdio_main()

if __name__ == "__main__":
    main()

"""Entry point for running MCP server as a module.

Usage:
    python -m contextframe.mcp /path/to/dataset.lance
"""

import asyncio
from contextframe.mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())
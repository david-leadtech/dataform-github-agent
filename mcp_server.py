#!/usr/bin/env python3
"""
MCP Server for Data Engineering Copilot
Exposes the agent's capabilities to Cursor via Model Context Protocol (MCP)
"""

import asyncio
import sys
from typing import Any, Sequence

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

from agent import root_agent


# Create MCP server instance
server = Server("data-engineering-copilot")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for the data engineering copilot."""
    return [
        Tool(
            name="run_agent_task",
            description="Run a data engineering task using the Data Engineering Copilot. "
                       "The agent can work with Dataform, dbt, PySpark (Dataproc/Databricks), "
                       "BigQuery, GitHub, and GCS. Examples: 'Create a new Dataform source', "
                       "'Debug the data pipeline', 'Check pipeline health', 'Create a PR with changes'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The task or question for the data engineering copilot"
                    }
                },
                "required": ["prompt"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls from Cursor."""
    if name == "run_agent_task":
        prompt = arguments.get("prompt", "")
        if not prompt:
            return [TextContent(
                type="text",
                text="Error: 'prompt' parameter is required"
            )]
        
        try:
            # Run the agent synchronously (ADK agents are synchronous)
            # We run it in a thread pool to avoid blocking
            import concurrent.futures
            loop = asyncio.get_event_loop()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor,
                    lambda: root_agent.run(prompt)
                )
            
            return [TextContent(
                type="text",
                text=str(response)
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error running agent: {str(e)}"
            )]
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())


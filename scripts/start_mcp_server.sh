#!/bin/bash
# Start MCP server for Cursor integration

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$AGENT_DIR"

echo "🚀 Starting Data Engineering Copilot MCP Server..."
echo ""

# Check if mcp is installed
if ! python -c "import mcp" 2>/dev/null; then
    echo "❌ MCP SDK not installed"
    echo "Installing dependencies..."
    pip install mcp
fi

# Check if agent is installed
if ! python -c "from agent import root_agent" 2>/dev/null; then
    echo "❌ Agent not installed"
    echo "Installing agent in editable mode..."
    pip install -e .
fi

echo "✅ Starting MCP server..."
echo ""
echo "📖 To use in Cursor:"
echo "   1. Add to Cursor MCP settings (Cursor Settings → MCP):"
echo "   {"
echo "     \"mcpServers\": {"
echo "       \"data-engineering-copilot\": {"
echo "         \"command\": \"python\","
echo "         \"args\": [\"$AGENT_DIR/mcp_server.py\"]"
echo "       }"
echo "     }"
echo "   }"
echo ""
echo "   2. Restart Cursor"
echo "   3. Ask Cursor: 'Use the data engineering copilot to...'"
echo ""

# Run MCP server
python mcp_server.py




#!/bin/bash
# Start REST API server for Data Engineering Copilot

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$AGENT_DIR"

echo "🚀 Starting Data Engineering Copilot API Server..."
echo ""

# Check if FastAPI is installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ FastAPI not installed"
    echo "Installing dependencies..."
    pip install fastapi uvicorn[standard]
fi

# Check if agent is installed
if ! python -c "from agent import root_agent" 2>/dev/null; then
    echo "❌ Agent not installed"
    echo "Installing agent in editable mode..."
    pip install -e .
fi

# Get port from environment or use default
PORT=${API_PORT:-8000}
HOST=${API_HOST:-0.0.0.0}

echo "✅ Starting API server on http://${HOST}:${PORT}"
echo ""
echo "📖 Available endpoints:"
echo "   - API Docs: http://localhost:${PORT}/docs"
echo "   - Health: http://localhost:${PORT}/health"
echo "   - Run Agent: POST http://localhost:${PORT}/agent/run"
echo ""
echo "💡 Example usage:"
echo "   curl -X POST http://localhost:${PORT}/agent/run \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"prompt\": \"Check the health of the data pipeline\"}'"
echo ""

# Run API server
python api_server.py


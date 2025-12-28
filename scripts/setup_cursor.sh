#!/bin/bash
# Setup script for using Dataform GitHub Agent in Cursor

set -e

echo "🚀 Setting up Dataform GitHub Agent for Cursor..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$AGENT_DIR"

echo "📦 Installing agent in editable mode..."
pip install -e .

echo "✅ Agent installed!"
echo ""
echo "📝 Next steps:"
echo "1. Create a .env file with your configuration (see README.md)"
echo "2. Authenticate with Google Cloud:"
echo "   gcloud auth application-default login"
echo "3. Use in Cursor:"
echo "   - Import: from dataform_github_agent.agent import root_agent"
echo "   - Or run: adk web"
echo ""
echo "📖 See CURSOR_INTEGRATION.md for detailed usage instructions"


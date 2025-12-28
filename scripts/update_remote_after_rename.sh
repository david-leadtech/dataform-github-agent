#!/bin/bash
# Update git remote after repository rename on GitHub
# Run this AFTER renaming the repository on GitHub

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
AGENT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$AGENT_DIR"

echo "🔄 Updating git remote after repository rename..."
echo ""

# Update remote URL
echo "Updating remote URL to: https://github.com/david-leadtech/data-engineering-copilot.git"
git remote set-url origin https://github.com/david-leadtech/data-engineering-copilot.git

# Verify
echo ""
echo "✅ Remote updated! Current remotes:"
git remote -v

echo ""
echo "✅ Done! You can now push/pull normally."




#!/bin/bash

# Script to initialize git, create GitHub repo, and push code
# Usage: ./setup_and_push.sh

set -e

REPO_NAME="dataform-github-agent"
ORG_NAME="david-leadtech"
FULL_REPO="${ORG_NAME}/${REPO_NAME}"

echo "🚀 Setting up Git and pushing to GitHub"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Initialize git
echo -e "${YELLOW}Step 1: Initializing git repository...${NC}"
if [ -d ".git" ]; then
    echo -e "  ${GREEN}✅${NC} Git repository already initialized"
else
    git init
    echo -e "  ${GREEN}✅${NC} Git repository initialized"
fi
echo ""

# Step 2: Configure git user (if not already configured)
echo -e "${YELLOW}Step 2: Configuring git user...${NC}"
git config user.email "david.sanchezcamacho@leadtech.com" || true
git config user.name "David Sánchez Camacho" || true
echo -e "  ${GREEN}✅${NC} Git user configured"
echo ""

# Step 3: Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo -e "${YELLOW}Step 3: Creating .gitignore...${NC}"
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# ADK
.adk/

# Logs
*.log
EOF
    echo -e "  ${GREEN}✅${NC} .gitignore created"
else
    echo -e "  ${GREEN}✅${NC} .gitignore already exists"
fi
echo ""

# Step 4: Add all files
echo -e "${YELLOW}Step 4: Adding files to git...${NC}"
git add .
echo -e "  ${GREEN}✅${NC} Files added"
echo ""

# Step 5: Create initial commit
echo -e "${YELLOW}Step 5: Creating initial commit...${NC}"
if git diff --cached --quiet; then
    echo -e "  ${YELLOW}⚠️${NC}  No changes to commit"
else
    git commit -m "Initial commit: Dataform GitHub Agent with dbt and PySpark support

- Comprehensive Dataform pipeline management
- Full dbt support (run, test, compile, docs, seed, snapshot, etc.)
- PySpark/Dataproc integration for distributed processing
- GitHub integration (branches, PRs, file sync)
- BigQuery performance analysis and monitoring
- Pipeline health monitoring and documentation generation"
    echo -e "  ${GREEN}✅${NC} Initial commit created"
fi
echo ""

# Step 6: Create GitHub repository
echo -e "${YELLOW}Step 6: Creating GitHub repository...${NC}"
if gh repo view "${FULL_REPO}" &>/dev/null; then
    echo -e "  ${YELLOW}⚠️${NC}  Repository ${FULL_REPO} already exists"
    echo -e "  ${YELLOW}⚠️${NC}  Skipping repository creation"
else
    gh repo create "${FULL_REPO}" \
        --public \
        --description "AI-powered data engineering agent with Dataform, dbt, PySpark/Dataproc, and GitHub integration" \
        --source=. \
        --remote=origin \
        --push || {
        echo -e "  ${RED}❌${NC} Failed to create repository"
        echo -e "  ${YELLOW}Trying to add remote manually...${NC}"
        git remote add origin "https://github.com/${FULL_REPO}.git" || git remote set-url origin "https://github.com/${FULL_REPO}.git"
    }
    echo -e "  ${GREEN}✅${NC} Repository created: https://github.com/${FULL_REPO}"
fi
echo ""

# Step 7: Set default branch to main
echo -e "${YELLOW}Step 7: Setting default branch...${NC}"
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
if [ "$CURRENT_BRANCH" != "main" ]; then
    git branch -M main 2>/dev/null || true
    echo -e "  ${GREEN}✅${NC} Branch renamed to main"
else
    echo -e "  ${GREEN}✅${NC} Already on main branch"
fi
echo ""

# Step 8: Push to GitHub
echo -e "${YELLOW}Step 8: Pushing to GitHub...${NC}"
if git remote get-url origin &>/dev/null; then
    echo -e "  Remote: $(git remote get-url origin)"
    git push -u origin main || {
        echo -e "  ${YELLOW}⚠️${NC}  Push failed, trying with force (if needed)..."
        echo -e "  ${YELLOW}⚠️${NC}  You may need to run manually: git push -u origin main"
    }
    echo -e "  ${GREEN}✅${NC} Code pushed to GitHub"
else
    echo -e "  ${RED}❌${NC} No remote configured"
    echo -e "  ${YELLOW}Run manually:${NC}"
    echo -e "    git remote add origin https://github.com/${FULL_REPO}.git"
    echo -e "    git push -u origin main"
fi

echo ""
echo -e "${GREEN}========================================"
echo -e "✅ Setup Complete!${NC}"
echo -e "${GREEN}========================================"
echo ""
echo "Repository URL: https://github.com/${FULL_REPO}"
echo ""
echo "Next steps:"
echo "1. Visit the repository: https://github.com/${FULL_REPO}"
echo "2. Add a README badge if needed"
echo "3. Configure repository settings"
echo "4. Set up GitHub Actions if needed"


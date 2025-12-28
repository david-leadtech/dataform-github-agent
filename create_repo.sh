#!/bin/bash

# Script to create GitHub repository in david-leadtech organization
# Usage: ./create_repo.sh

echo "Creating repository 'dataform-github-agent' in david-leadtech organization..."

gh repo create david-leadtech/dataform-github-agent \
  --public \
  --description "AI-powered data engineering agent with Dataform, dbt, PySpark/Dataproc, and GitHub integration" \
  --clone=false \
  --add-readme=false \
  --gitignore=Python \
  --license=apache-2.0

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ Repository created successfully!"
  echo "   URL: https://github.com/david-leadtech/dataform-github-agent"
  echo ""
  echo "Next steps:"
  echo "1. Initialize git in this directory:"
  echo "   cd $(pwd)"
  echo "   git init"
  echo "   git remote add origin https://github.com/david-leadtech/dataform-github-agent.git"
  echo "   git add ."
  echo "   git commit -m 'Initial commit: Dataform GitHub Agent with dbt and PySpark support'"
  echo "   git push -u origin main"
else
  echo ""
  echo "❌ Failed to create repository"
  echo "Please check:"
  echo "- You're authenticated with GitHub CLI (gh auth login)"
  echo "- You have permissions to create repos in david-leadtech organization"
  echo "- The repository name doesn't already exist"
fi


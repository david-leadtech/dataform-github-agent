#!/bin/bash

# Release script for Data Engineering Copilot
# Usage: ./scripts/release.sh [major|minor|patch] [--dry-run]

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

RELEASE_TYPE="${1:-patch}"
DRY_RUN="${2:-}"

if [[ ! "$RELEASE_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo -e "${RED}Error: Release type must be 'major', 'minor', or 'patch'${NC}"
    echo "Usage: ./scripts/release.sh [major|minor|patch] [--dry-run]"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "0.0.0")
echo -e "${BLUE}Current version: ${CURRENT_VERSION}${NC}"

# Parse version
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

# Calculate new version
case $RELEASE_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
echo -e "${BLUE}New version: ${NEW_VERSION}${NC}"

if [ "$DRY_RUN" = "--dry-run" ]; then
    echo -e "${YELLOW}DRY RUN MODE - No changes will be made${NC}"
    echo ""
    echo "Would:"
    echo "  1. Update VERSION file to ${NEW_VERSION}"
    echo "  2. Create git tag v${NEW_VERSION}"
    echo "  3. Push tag to GitHub"
    echo "  4. Create GitHub release"
    exit 0
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}Error: Working directory is not clean. Commit or stash changes first.${NC}"
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}Warning: Not on main branch (currently on ${CURRENT_BRANCH})${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update VERSION file
echo -e "${YELLOW}Step 1: Updating VERSION file...${NC}"
echo "$NEW_VERSION" > VERSION
git add VERSION
echo -e "${GREEN}✅ VERSION updated${NC}"

# Update CHANGELOG (user will add entry manually)
echo -e "${YELLOW}Step 2: CHANGELOG update${NC}"
echo -e "${BLUE}Please add a changelog entry for version ${NEW_VERSION} in CHANGELOG.md${NC}"
echo -e "${BLUE}Press Enter when done, or Ctrl+C to cancel...${NC}"
read

git add CHANGELOG.md
echo -e "${GREEN}✅ CHANGELOG updated${NC}"

# Create commit
echo -e "${YELLOW}Step 3: Creating release commit...${NC}"
git commit -m "chore: release v${NEW_VERSION}

See CHANGELOG.md for details."
echo -e "${GREEN}✅ Commit created${NC}"

# Create tag
echo -e "${YELLOW}Step 4: Creating git tag...${NC}"
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}

See CHANGELOG.md for details."
echo -e "${GREEN}✅ Tag v${NEW_VERSION} created${NC}"

# Push to GitHub
echo -e "${YELLOW}Step 5: Pushing to GitHub...${NC}"
git push origin main
git push origin "v${NEW_VERSION}"
echo -e "${GREEN}✅ Pushed to GitHub${NC}"

# Create GitHub release
echo -e "${YELLOW}Step 6: Creating GitHub release...${NC}"

# Extract changelog entry for this version
CHANGELOG_ENTRY=$(awk "/^## \[${NEW_VERSION}\]/,/^## \[/" CHANGELOG.md | sed '/^## \[/d' | sed '/^$/d' | head -n -1)

if [ -z "$CHANGELOG_ENTRY" ]; then
    CHANGELOG_ENTRY="See CHANGELOG.md for details."
fi

gh release create "v${NEW_VERSION}" \
    --title "Release v${NEW_VERSION}" \
    --notes "$CHANGELOG_ENTRY" \
    --target main || {
    echo -e "${YELLOW}⚠️  GitHub release creation failed (may need manual creation)${NC}"
    echo -e "${BLUE}You can create it manually at:${NC}"
    echo -e "${BLUE}https://github.com/david-leadtech/dataform-github-agent/releases/new${NC}"
}

echo ""
echo -e "${GREEN}========================================"
echo -e "✅ Release v${NEW_VERSION} completed!${NC}"
echo -e "${GREEN}========================================"
echo ""
echo "Release URL: https://github.com/david-leadtech/dataform-github-agent/releases/tag/v${NEW_VERSION}"


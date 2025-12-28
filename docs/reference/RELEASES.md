# 🚀 Release Management

This document explains how to create releases for the Data Engineering Copilot.

> **← [Back to README](../../README.md)** | **[View All Documentation](../../README.md#-documentation)**

## Quick Start

```bash
# Create a patch release (1.0.0 -> 1.0.1)
./scripts/release.sh patch

# Create a minor release (1.0.0 -> 1.1.0)
./scripts/release.sh minor

# Create a major release (1.0.0 -> 2.0.0)
./scripts/release.sh major

# Dry run (see what would happen without making changes)
./scripts/release.sh patch --dry-run
```

## Release Process

### 1. Update CHANGELOG.md

Before creating a release, add an entry to `CHANGELOG.md`:

```markdown
## [1.0.1] - 2025-01-XX

### Added
- New feature X
- New tool Y

### Fixed
- Bug fix Z

### Changed
- Improvement to feature A
```

### 2. Run Release Script

```bash
./scripts/release.sh patch
```

The script will:
1. ✅ Calculate new version based on current version
2. ✅ Update `VERSION` file
3. ✅ Wait for you to update `CHANGELOG.md` (if not done)
4. ✅ Create a release commit
5. ✅ Create a git tag
6. ✅ Push to GitHub
7. ✅ Create GitHub release with changelog

### 3. Verify Release

Check the GitHub releases page:
https://github.com/david-leadtech/data-engineering-copilot/releases

## Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Breaking changes (incompatible API changes)
- **MINOR** version: New features (backward compatible)
- **PATCH** version: Bug fixes (backward compatible)

### Examples

- `1.0.0` → `1.0.1`: Bug fix
- `1.0.1` → `1.1.0`: New feature (backward compatible)
- `1.1.0` → `2.0.0`: Breaking change

## Automated Release Workflow

When you push a tag (e.g., `v1.0.1`), GitHub Actions automatically:
- Extracts the version from the tag
- Reads the changelog entry
- Creates a GitHub release with the changelog

## Manual Release (Alternative)

If you prefer to create releases manually:

```bash
# 1. Update VERSION file
echo "1.0.1" > VERSION

# 2. Update CHANGELOG.md
# (add entry manually)

# 3. Commit
git add VERSION CHANGELOG.md
git commit -m "chore: release v1.0.1"

# 4. Create and push tag
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin main
git push origin v1.0.1

# 5. Create GitHub release
gh release create v1.0.1 \
  --title "Release v1.0.1" \
  --notes-file CHANGELOG.md
```

## Release Checklist

Before creating a release:

- [ ] All tests pass (if applicable)
- [ ] Documentation is up to date
- [ ] CHANGELOG.md has entry for new version
- [ ] VERSION file will be updated correctly
- [ ] Working directory is clean (no uncommitted changes)
- [ ] You're on the `main` branch

## Version File

The `VERSION` file contains the current version number. This is used by:
- Release script to calculate next version
- README.md badge (if configured)
- Any version checks in the code

## Changelog Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

```markdown
## [Version] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing features

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security fixes
```

## Troubleshooting

### "Working directory is not clean"
Commit or stash your changes before creating a release.

### "Not on main branch"
Either switch to main branch or confirm you want to release from current branch.

### "GitHub release creation failed"
You may need to authenticate with GitHub CLI:
```bash
gh auth login
```

Or create the release manually on GitHub.


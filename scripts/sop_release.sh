#!/bin/bash
set -e
# SOP: Bump Version & Tag
# Usage: ./scripts/sop_release.sh <patch|minor|version_string>

MODE=$1

if [ -z "$MODE" ]; then
    echo "❌ Error: Usage: $0 <patch|minor|x.y.z>"
    exit 1
fi

cd "$(dirname "$0")/.."

# Get current version
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | head -n 1 | cut -d '"' -f 2)
echo "ℹ️  Current Version: $CURRENT_VERSION"

NEW_VERSION=""

if [[ "$MODE" == "patch" ]]; then
    IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"
    NEW_VERSION="$major.$minor.$((patch + 1))"
elif [[ "$MODE" == "minor" ]]; then
    IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"
    NEW_VERSION="$major.$((minor + 1)).0"
else
    # Assume explicit version
    NEW_VERSION="$MODE"
fi

# Basic validation (simple regex)
if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Error: Invalid version format '$NEW_VERSION'. Expected x.y.z"
    exit 1
fi

echo "🚀 [SOP] Bumping to $NEW_VERSION"

# Update pyproject.toml
perl -pi -e "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Update extension package.json
perl -pi -e "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$NEW_VERSION\"/" extensions/vscode/package.json

# Update server application.py
# Targets: server = TypedownLanguageServer("typedown-server", "x.y.z")
perl -pi -e "s/\"typedown-server\", \"$CURRENT_VERSION\"/\"typedown-server\", \"$NEW_VERSION\"/" src/typedown/server/application.py

# Git Commit & Tag
git add pyproject.toml extensions/vscode/package.json src/typedown/server/application.py
git commit -m "chore: bump version to v$NEW_VERSION"
git tag "v$NEW_VERSION"

echo "✅ Version bumped and tagged: v$NEW_VERSION"
echo "👉 Action Required: git push && git push --tags"

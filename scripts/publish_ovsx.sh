#!/bin/bash
set -e

# Configuration
PROJECT_ROOT=$(git rev-parse --show-toplevel)
EXTENSION_DIR="$PROJECT_ROOT/extensions/vscode"
OVSX_REGISTRY="https://open-vsx.org"

# Check for Token
if [ -z "$OVSX_PAT" ]; then
    echo "Error: OVSX_PAT environment variable is not set."
    echo "Please export your Open VSX Personal Access Token:"
    echo "  export OVSX_PAT=your_token_here"
    exit 1
fi

echo "🚀 Starting Open VSX Publication Process..."

# Navigate to extension directory
cd "$EXTENSION_DIR" || exit

echo "📦 Installing dependencies..."
npm ci

echo "🛠️  Compiling extension..."
npm run compile

echo "📦 Packaging extension..."
# use npx to run vsce without global install
npx vsce package

# Find the generated vsix file in the current directory
VSIX_FILE=$(ls ./*.vsix | head -n 1)

if [ -z "$VSIX_FILE" ]; then
    echo "Error: Could not locate .vsix file."
    exit 1
fi

echo "found package: $VSIX_FILE"

echo "🚀 Publishing to Open VSX..."
npx ovsx publish "$VSIX_FILE" --pat "$OVSX_PAT"

echo "✅ Published successfully!"

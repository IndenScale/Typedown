#!/bin/bash
set -e

# Configuration
EXTENSION_DIR="extensions/vscode"
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
npm install

echo "🛠️  Compiling extension..."
npm run compile

echo "📦 Packaging extension..."
# use npx to run vsce without global install
npx vsce package --out ./out/extension.vsix

# Find the generated vsix file
VSIX_FILE="./out/extension.vsix"

if [ ! -f "$VSIX_FILE" ]; then
    echo "Error: VSIX file not found at $VSIX_FILE"
    # fallback to root if out unavailable or path differs
    VSIX_FILE=$(find . -maxdepth 1 -name "*.vsix" | head -n 1)
fi

if [ -z "$VSIX_FILE" ]; then
    echo "Error: Could not locate .vsix file."
    exit 1
fi

echo "found package: $VSIX_FILE"

echo "🚀 Publishing to Open VSX..."
npx ovsx publish "$VSIX_FILE" --pat "$OVSX_PAT"

echo "✅ Published successfully!"

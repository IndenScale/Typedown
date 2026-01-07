#!/bin/bash
set -e
# SOP: Build WASM and move to website
# Usage: ./scripts/sop_build_wasm.sh

cd "$(dirname "$0")/.."

echo "📦 [SOP] Building Typedown Core..."
rm -rf dist
uv build

echo "🚚 [SOP] Moving wheel..."
WHEEL_FILE=$(ls dist/*.whl | head -n 1)
if [ -z "$WHEEL_FILE" ]; then
    echo "❌ Build failed: No wheel file found."
    exit 1
fi

TARGET="website/public/typedown-0.0.0-py3-none-any.whl"
cp "$WHEEL_FILE" "$TARGET"
echo "✅ WASM updated: $TARGET"

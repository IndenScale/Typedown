#!/bin/bash
set -e
# SOP: Core & Extension Tests
# Usage: ./scripts/sop_pre_release.sh

cd "$(dirname "$0")/.."

echo "🧪 [SOP] Running Core Tests..."
uv run --extra server python -m pytest tests

echo "🧩 [SOP] Verifying Extension Compile..."
cd extensions/vscode
npm run compile

echo "✅ Pre-release checks passed."

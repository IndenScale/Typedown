#!/bin/bash
set -e
# SOP: Check Website Health
# Usage: ./scripts/sop_check_website.sh

cd "$(dirname "$0")/../website"

echo "📦 [SOP] Checking Dependency Integrity..."
# 'npm ls' will exit with code 1 if the dependency tree is invalid or missing packages
if ! npm ls --depth=0 > /dev/null 2>&1; then
    echo "❌ Error: Node dependencies are out of sync or missing."
    echo "👉 Fix: Run 'npm install' or 'npm ci' in the website directory first."
    exit 1
fi
echo "✅ Dependencies look good."

echo "🌐 [SOP] Website Linting..."
npm run lint

echo "🏗️  [SOP] Website Build Test..."
npm run build

echo "✅ Website checks passed."

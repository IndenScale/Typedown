#!/bin/bash
# Run Integration Tests for Typedown Extension and Python Core

set -e

echo "=== Typedown Integration Tests ==="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Must run from project root"
    exit 1
fi

# Install dependencies if needed
echo "Installing dependencies..."
uv sync --extra server

echo ""
echo "Running integration tests..."
echo ""

# Run all integration tests
uv run pytest tests/integration/ -v "$@"

echo ""
echo "=== Integration Tests Complete ==="

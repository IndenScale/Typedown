#!/bin/bash
set -e

echo "=== Typedown CI Check ==="

echo "[1/2] Running Tests..."
uv run --extra server python -m pytest tests

# TODO: Add style checks (ruff/black) when dependencies are added
# echo "[2/2] Checking Style..."
# uv run ruff check .

echo "All checks passed! Match Point!"

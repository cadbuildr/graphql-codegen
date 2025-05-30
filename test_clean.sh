#!/bin/bash
set -e

echo "🧹 Cleaning generated code..."

# Remove only generated directories, preserve user code
rm -rf test/outputs/*/gen/

echo "🚀 Regenerating outputs..."

# Regenerate the test outputs
poetry run graphql-codegen test/inputs/smoothies/
poetry run graphql-codegen test/inputs/userpost/

echo "🧪 Running tests..."

# Run tests with proper PYTHONPATH
cd test/outputs
PYTHONPATH=. poetry run pytest -v

echo "✅ Clean test run complete!" 
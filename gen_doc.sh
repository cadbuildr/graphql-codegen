#!/bin/bash
set -e

echo "🚀 Generating DRY Documentation Examples"
echo "========================================"

# Create output directories
mkdir -p docs/outputs

# Define examples with their line ranges
declare -a examples=(
    "hello:12-33:Foundation: From basic scalars to complete objects"
    "interfaces_and_unions:12-50:Interfaces and implementations"
    "compute:1-66:@compute directive"
    "expand:1-108:@expand directive"
)

success_count=0
total_count=${#examples[@]}

# Generate each example
for item in "${examples[@]}"; do
    # Split example info
    example=$(echo "$item" | cut -d: -f1)
    lines=$(echo "$item" | cut -d: -f2)
    description=$(echo "$item" | cut -d: -f3-)
    
    echo
    echo "📝 Generating $example: $description (lines $lines)"
    
    # Create temporary config
    temp_config="/tmp/${example}_config.yaml"
    cat > "$temp_config" << EOF
package: $example
runtime_package: ${example}.runtime
codegen_version: "0.1"
flat_output: true
stdout: true

base_schema: "test/inputs/smoothies/schema.graphql"
schema_lines: "$lines"

scalars:
  String: str
  Float: float
EOF
    
    output_file="docs/outputs/${example}.py"
    
    # Generate using temporary config
    if poetry run python -c "
import sys
sys.path.append('.')
from graphql_codegen.config import CodegenConfig
from graphql_codegen.generator import generate_stdout_output
from graphql_codegen.parser import load_and_parse_schema_with_config
from pathlib import Path
import yaml

with open('$temp_config') as f:
    config_data = yaml.safe_load(f)
config = CodegenConfig(**config_data)
schema_info = load_and_parse_schema_with_config(Path('.'), config)
generate_stdout_output(config, schema_info)
" > "$output_file" 2>/dev/null; then
        echo "✅ Generated $output_file"
        ((success_count++))
    else
        echo "❌ Failed to generate $output_file"
    fi
    
    # Clean up temp config
    rm -f "$temp_config"
done

echo
echo "🎉 Generated $success_count/$total_count examples successfully!"

if [ $success_count -lt $total_count ]; then
    exit 1
fi

echo
echo "📚 Building documentation site..."
if poetry run mkdocs build; then
    echo "✅ Documentation built successfully!"
    echo "📖 View at: file://$(pwd)/site/index.html"
else
    echo "❌ Documentation build failed"
    exit 1
fi

echo
echo "🔍 Checking for documentation drift..."
if git diff --exit-code docs/examples; then
    echo "✅ Documentation is up to date!"
else
    echo "❌ Documentation has uncommitted changes!"
    echo "   Run this script and commit the updated docs."
    exit 1
fi 
#!/bin/bash
set -e
set -x  # Print every command as it executes

echo "🚀 Generating DRY Documentation Examples"
echo "========================================"

# Create output directories
echo "Creating docs/outputs directory..."
mkdir -p docs/outputs
echo "✅ Directory created"

# Define examples with their line ranges
declare -a examples=(
    "hello:12-33:Foundation: From basic scalars to complete objects"
    "interfaces_and_unions:12-50:Interfaces and implementations"
    "compute:1-66:@compute directive"
    "expand:1-108:@expand directive"
)

success_count=0
total_count=${#examples[@]}

echo "Total examples to process: $total_count"

# Generate each example
for item in "${examples[@]}"; do
    echo "=== PROCESSING ITEM: $item ==="
    
    # Split example info
    example=$(echo "$item" | cut -d: -f1)
    lines=$(echo "$item" | cut -d: -f2)
    description=$(echo "$item" | cut -d: -f3-)
    
    echo "Example: $example"
    echo "Lines: $lines" 
    echo "Description: $description"
    
    echo
    echo "📝 Generating $example: $description (lines $lines)"
    
    # Create temporary config using local temp directory instead of /tmp
    temp_config="./${example}_config.yaml"
    echo "Creating temp config at: $temp_config"
    
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
    
    echo "✅ Temp config created, contents:"
    cat "$temp_config"
    
    output_file="docs/outputs/${example}.py"
    echo "Output will be written to: $output_file"
    
    # Generate using temporary config with better error handling
    echo "  → Running generation command..."
    
    generation_cmd="poetry run python -c \"
import sys
sys.path.append('.')
from graphql_codegen.config import CodegenConfig
from graphql_codegen.generator import generate_stdout_output
from graphql_codegen.parser import load_and_parse_schema_with_config
from pathlib import Path
import yaml

try:
    print('Loading config from $temp_config', file=sys.stderr)
    with open('$temp_config') as f:
        config_data = yaml.safe_load(f)
    print('Config loaded successfully', file=sys.stderr)
    
    config = CodegenConfig(**config_data)
    print('CodegenConfig created', file=sys.stderr)
    
    schema_info = load_and_parse_schema_with_config(Path('.'), config)
    print('Schema parsed successfully', file=sys.stderr)
    
    generate_stdout_output(config, schema_info)
    print('Generation completed successfully', file=sys.stderr)
except Exception as e:
    print(f'ERROR in $example generation: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
\""
    
    echo "About to execute: $generation_cmd"
    
    if eval "$generation_cmd" > "$output_file"; then
        echo "✅ Generated $output_file"
        echo "File size: $(wc -l < "$output_file") lines"
        ((success_count++))
    else
        echo "❌ Failed to generate $output_file"
        echo "   Config used: $temp_config"
        echo "   Output would be: $output_file"
        echo "   Exit code: $?"
        echo "FAILING NOW!"
        exit 1
    fi
    
    # Clean up temp config
    echo "Cleaning up temp config: $temp_config"
    rm -f "$temp_config"
    echo "✅ Temp config cleaned up"
    
    echo "=== COMPLETED ITEM: $example ==="
    echo "Success count so far: $success_count"
    echo
done

echo
echo "🎉 Generated $success_count/$total_count examples successfully!"

if [ $success_count -lt $total_count ]; then
    echo "❌ Not all examples generated successfully!"
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
#!/usr/bin/env python3
"""Generate documentation with dynamic includes from generated files."""

import subprocess
import sys
from pathlib import Path

def include_generated_file(output_dir: Path, example_name: str) -> str:
    """Include the content of a generated file."""
    generated_file = output_dir / f"{example_name}.py"
    if generated_file.exists():
        with open(generated_file, 'r') as f:
            content = f.read()
        return f"```python\n{content}\n```"
    else:
        return f"```\n# File not found: {generated_file}\n# Run ./gen_doc.sh to generate\n```"

def update_doc_page(page_file: Path, example_name: str, output_dir: Path):
    """Update a documentation page with actual generated content."""
    if not page_file.exists():
        return False
        
    with open(page_file, 'r') as f:
        content = f.read()
    
    # Find the generated code section and replace it
    generated_code = include_generated_file(output_dir, example_name)
    
    # Replace the placeholder with actual code
    start_marker = "```python\n# See the actual generated file:"
    end_marker = "```"
    
    if start_marker in content:
        # Find and replace the section
        start_idx = content.find(start_marker)
        if start_idx != -1:
            # Find the end of this code block
            end_idx = content.find(end_marker, start_idx + len(start_marker))
            if end_idx != -1:
                end_idx += len(end_marker)
                # Replace with actual generated content
                new_content = content[:start_idx] + generated_code + content[end_idx:]
                
                with open(page_file, 'w') as f:
                    f.write(new_content)
                return True
    
    return False

def main():
    """Update all documentation pages with actual generated content."""
    print("🔄 Updating documentation with actual generated files...")
    
    # First, generate the examples
    print("1. Generating examples...")
    result = subprocess.run(["./gen_doc.sh"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Failed to generate examples: {result.stderr}")
        return False
    
    # Update documentation pages
    print("2. Updating documentation pages...")
    doc_dir = Path("doc")
    output_dir = doc_dir / "outputs"
    pages_dir = doc_dir / "pages"
    
    examples = [
        "smoothie_01_basic",
        "smoothie_02_nested", 
        "smoothie_03_compute",
        "smoothie_04_expand",
        "smoothie_05_flat"
    ]
    
    updated_count = 0
    for example in examples:
        page_file = pages_dir / f"{example.replace('smoothie_', '').replace('_', '-')}.md"
        if update_doc_page(page_file, example, output_dir):
            print(f"✅ Updated {page_file}")
            updated_count += 1
        else:
            print(f"⚠️  Could not update {page_file}")
    
    print(f"\n🎉 Updated {updated_count} documentation pages!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
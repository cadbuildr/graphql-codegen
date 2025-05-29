# GraphQL Codegen Documentation

**Progressive Examples: From Basic Types to Advanced Directives**

This documentation walks through GraphQL Codegen features with progressive examples using a smoothie recipe schema. Each example builds on the previous one, demonstrating core concepts step by step.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Generate examples:**
   ```bash
   ./gen_doc.sh
   ```

3. **Try it yourself:**
   ```bash
   poetry run python -m graphql_codegen.cli test/inputs/smoothies --stdout --flat
   ```

## 📚 Learning Path

| Example | Description |
|---------|-------------|
| [Basic Types](examples/01-basic-types.md) | Scalar types and simple objects |
| [Nested Objects](examples/02-nested-objects.md) | Parameter wrappers and object composition |
| [Compute Directive](examples/03-compute-directive.md) | Calculated fields with `@compute` |
| [Expand Directive](examples/04-expand-directive.md) | JSON template expansion with `@expand` |
| [Complete Schema](examples/05-complete-schema.md) | Full-featured smoothie schema |

## 🎯 Key Features

- **🔗 DRY Schema Management**: Single source schema with line extraction
- **📤 Flexible Output**: Generate packages or single files
- **🧮 Computed Fields**: Derive values with Python functions using `@compute`
- **🎨 Template Expansion**: JSON-based macro expansion with `@expand`
- **🔌 Runtime Flexibility**: Optional custom logic with registration functions

## 📖 Master Schema

All examples extract portions from this single source of truth:

```graphql
{% include_markdown "../test/inputs/smoothies/schema.graphql" %}
``` 
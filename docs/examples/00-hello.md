# 00 - Hello GraphQL Codegen

**Quick Start: Your First Generated Model**

## 🎯 Goal

Get GraphQL Codegen working in under 60 seconds with a minimal "hello world" example.

## 🚀 Try It Yourself

### 1. Create your schema file

Copy this content into `hello.graphql`:

```graphql
{% include_markdown "../../test/inputs/smoothies/schema.graphql" start="8" end="14" %}
```

### 2. Create your config file

Copy this content into `codegen.yaml`:

```yaml
{% include_markdown "../../test/inputs/smoothies/codegen.yaml" %}
```

### 3. Run the generator

```bash
poetry install
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

You'll see this output:

```python
{% include_markdown "../outputs/hello.py" %}
```

## 🔍 Key Concepts

- **Zero config**: Just point at a GraphQL schema file
- **Pydantic models**: Every GraphQL type becomes a typed Python class
- **Required fields**: GraphQL `!` becomes `Field(...)`
- **Flat output**: Single file with all models and helpers

---

[← Home](../index.md) | [Next: Basic Types →](01-basic-types.md) 
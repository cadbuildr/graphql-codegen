# 01 - Basic Types

**Foundation: Scalar Types and Simple Objects**

## 🎯 Goal

Learn how GraphQL scalar types and basic objects become Pydantic models with proper type annotations.

## 📋 Schema Input

Copy this content into `basic.graphql`:

```graphql
{% include_markdown "../../test/inputs/smoothies/schema.graphql" start="13" end="38" %}
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
{% include_markdown "../outputs/basic_types.py" %}
```

## 🔍 Key Concepts

- **Scalar mappings**: `String → str`, `Float → float`
- **Required fields**: GraphQL `!` becomes `Field(...)`
- **Forward references**: Type relationships use quoted strings
- **Model rebuilding**: Resolves circular references

## 💡 What You Get

- Type-safe Pydantic models
- Automatic validation
- IDE autocomplete support
- JSON serialization/deserialization

---

[← Scalars & Enums](01-scalars-enums.md) | [Next: Interfaces →](02-interfaces.md) 
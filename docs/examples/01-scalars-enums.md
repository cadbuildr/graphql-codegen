# 01 - Scalars & Enums

**Foundation: Type Mapping and Enumeration Values**

## 🎯 Goal

Learn how GraphQL scalars map to Python types and how enums become type-safe string enumerations.

## 📋 Schema Input

Copy this content into `scalars.graphql`:

```graphql
{% include_markdown "../../test/inputs/smoothies/schema.graphql" start="13" end="21" %}
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
{% include_markdown "../outputs/scalars_enums.py" %}
```

## 🔍 Key Concepts

- **Built-in scalars**: `String → str`, `Float → float`
- **Custom scalars**: `CaloriesPerGram → float` (via config mapping)
- **Enum generation**: GraphQL enums become Python `str, Enum` classes
- **Type safety**: Enum values are statically typed and validated

## 💡 Enum Benefits

- IDE autocomplete for enum values
- Runtime validation of enum assignments
- String serialization for JSON APIs
- Type checking with mypy/pylint

## 🔧 Config Mapping

To use custom scalars, add them to your `codegen.yaml`:

```yaml
{% include_markdown "../../test/inputs/smoothies/codegen.yaml" start="6" end="12" %}
```

---

[← Hello](00-hello.md) | [Next: Basic Types →](01-basic-types.md) 
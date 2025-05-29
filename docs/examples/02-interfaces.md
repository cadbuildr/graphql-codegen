# 02 - Interfaces

**Foundation: Shared Behavior with Interface Implementation**

## 🎯 Goal

Learn how GraphQL interfaces become base classes that enforce shared fields across implementing types.

## 📋 Schema Input

Copy this content into `interfaces.graphql`:

```graphql
{% include_markdown "../../test/inputs/smoothies/schema.graphql" start="13" end="50" %}
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
{% include_markdown "../outputs/interfaces.py" %}
```

## 🔍 Key Concepts

- **Interface definition**: `interface Ingredient` becomes a base class
- **Implementation**: `Fruit implements Ingredient` inherits from `Ingredient`
- **Field inheritance**: Implementing types get interface fields automatically
- **Multiple interfaces**: Types can implement multiple interfaces

## 💡 What Changed

Compared to basic types, we now have:
- `Ingredient` interface with shared fields (`name`, `calories_per_gram`)
- `Fruit` and `Addon` types that implement the interface
- Each implementation adds its own specific fields (`sweetness`, `protein`)
- Clean inheritance hierarchy avoiding duplication

---

[← Basic Types](01-basic-types.md) | [Next: Unions →](03-unions.md) 
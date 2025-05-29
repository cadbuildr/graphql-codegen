# 03 - Unions

**Advanced Types: Union Type Aliases**

## 🎯 Goal

Learn how GraphQL unions become Python type aliases that can hold multiple possible types.

## 📋 Schema Input

Copy this content into `unions.graphql`:

```graphql
{% include_markdown "../../test/inputs/smoothies/schema.graphql" start="13" end="56" %}
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
{% include_markdown "../outputs/unions.py" %}
```

## 🔍 Key Concepts

- **Union definition**: `union Blendable = Fruit | Addon` becomes type alias
- **Type alias**: `Blendable = Union["Fruit", "Addon"]` in Python
- **Runtime checking**: Use `isinstance()` to determine actual type
- **Forward references**: Union members use quoted strings

## 💡 What's New

The `union Blendable = Fruit | Addon` declaration creates:

```python
Blendable = Union["Fruit", "Addon"]
```

This means any field typed as `Blendable` can be either a `Fruit` or `Addon` instance.

## 🔍 Runtime Usage

```python
# Both are valid Blendable instances
banana = Fruit(name="Banana", calories_per_gram=FloatParameter(value=0.89), sweetness=FloatParameter(value=8.5))
protein = Addon(name="Protein Powder", calories_per_gram=FloatParameter(value=4.0), protein=FloatParameter(value=25.0))

# Check type at runtime
if isinstance(banana, Fruit):
    print(f"Sweetness: {banana.sweetness.value}")
elif isinstance(banana, Addon):
    print(f"Protein: {banana.protein.value}")
```

---

[← Interfaces](02-interfaces.md) | [Next: Compute Directive →](04-compute-directive.md) 
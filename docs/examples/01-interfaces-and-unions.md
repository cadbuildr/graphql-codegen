# 01 - Interfaces and Unions

**Foundation: Shared Behavior with Interface Implementation and Union Type Aliases**

## 🎯 Goal

In this follow up example we will create reusable interfaces and unions. The goal here is to be able to use interfaces with `implements` to create `Pydantic` models using python inheritance, and unions to create type aliases that can hold multiple possible types.

## 📋 Schema Input

Copy this content into `interfaces.graphql`:

```graphql
--8<-- "test/inputs/smoothies/schema.graphql:13:56"
```

## 🚀 Run It

```bash
graphql-codegen . --stdout --flat
```

## 🐍 Generated Python

```python
--8<-- "docs/outputs/interfaces_and_unions.py"
```

## 🔍 Key Concepts

### Interfaces
- **Interface definition**: `interface Ingredient` becomes a base class
- **Implementation**: `Fruit implements Ingredient` inherits from `Ingredient`
- **Field inheritance**: Implementing types get interface fields automatically
- **Multiple interfaces**: Types can implement multiple interfaces

### Unions
- **Union definition**: `union Blendable = Fruit | Addon` becomes type alias
- **Type alias**: `Blendable = Union["Fruit", "Addon"]` in Python
- **Runtime checking**: Use `isinstance()` to determine actual type
- **Forward references**: Union members use quoted strings

## 💡 What's Included

This example demonstrates:
- `Ingredient` interface with shared fields (`name`, `calories_per_gram`)
- `Fruit` and `Addon` types that implement the interface
- Each implementation adds its own specific fields (`sweetness`, `protein`)
- Clean inheritance hierarchy avoiding duplication
- `union Blendable = Fruit | Addon` creates `Blendable = Union["Fruit", "Addon"]`

## ! Note 
- In Graphql even if we use implement we have to include the fields again in the schema definition. This is something we might address in future versions of the codegen with a custom directive to stay DRY. The generated `Pydantic` class don't repeat the fields (because in Python Pydantic you should not do that) 

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

[← Hello](00-hello.md) | [Next: Compute Directive →](02-compute-directive.md) 
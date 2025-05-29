# 05 - @expand Directive

**Template Expansion: JSON Macros with Variable Substitution**

## 🎯 Goal

Learn how the `@expand` directive generates complex nested structures from JSON templates with variable substitution.

## 📋 Schema Input

Copy this content into `expand.graphql`:

```graphql
{% include_markdown "../../test/inputs/smoothies/schema.graphql" start="1" end="102" %}
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
{% include_markdown "../outputs/expand.py" %}
```

## 🔍 Key Concepts

- **@expand directive**: Generates complex object structures from JSON templates
- **Variable substitution**: `$size` in template gets replaced with field value
- **Expandable mixin**: Automatically added to types with expansion
- **Template storage**: JSON template stored in `json_schema_extra`

## 💡 Complete Feature Set

This complete example now demonstrates:

- ✅ **Custom scalars**: `CaloriesPerGram`
- ✅ **Enums**: `Size` with type-safe values
- ✅ **Interfaces**: `Ingredient` with implementations
- ✅ **Unions**: `Blendable = Fruit | Addon`
- ✅ **@compute directive**: Runtime calculated fields
- ✅ **@expand directive**: JSON template expansion
- ✅ **Mixins**: `Computable` and `Expandable` inheritance

## 🎨 How Expansion Works

The `@expand` directive on `BananaStrawberrySmoothie.result` contains a JSON template:

```graphql
result: Smoothie! @expand(into: """
{
  "name": "Banana-Strawberry",
  "size": "$size",
  "parts": [
    {
      "ingredient": {"name": "Banana", "calories_per_gram": {"value": 0.89}, "sweetness": {"value": 8.5}},
      "grams": {"value": 120}
    }
  ]
}
""")
```

## 🔄 Runtime Usage

```python
# Create instance with parameters
smoothie_spec = BananaStrawberrySmoothie(size=Size.LARGE)

# Expand creates the full Smoothie object
full_smoothie = smoothie_spec.expand()
print(full_smoothie.name)  # "Banana-Strawberry"
print(full_smoothie.size)  # Size.LARGE
print(len(full_smoothie.parts))  # 3 ingredients

# Access union types
for part in full_smoothie.parts:
    if isinstance(part.ingredient, Fruit):
        print(f"Fruit: {part.ingredient.name}, Sweetness: {part.ingredient.sweetness.value}")
    elif isinstance(part.ingredient, Addon):
        print(f"Addon: {part.ingredient.name}, Protein: {part.ingredient.protein.value}")
```

---

[← Compute Directive](04-compute-directive.md) | [Home](../index.md) 
# 04 - @expand Directive

**Template Expansion: JSON Macros with Variable Substitution**

## 🎯 Goal

Learn how the `@expand` directive generates complex nested structures from JSON templates with variable substitution.

The second key concept of our codegen is to provide our schema with expansion capabilities. This feature goal is to facilitate converting complex types into primitives. Imagine the following for our smoothie example. We have created a library to render smoothies. That library will read a JSON object that needs to match our `Smoothie` type previously defined. Now in our schema we also have a `BananaSmoothie`. During serialization to JSON we want an easy way to convert it to a `Smoothie`. That is where the expand comes in handy. The goal here is to provide a way to keep our schema in python while being able to give options of which `Primitives` we want to convert to at serialization ( potentially because our rendering application supports specific `Primitives`)   

## 📋 Schema Input

Copy this content into `expand.graphql`:

```graphql
--8<-- "test/inputs/smoothies/schema.graphql:1:133"
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
--8<-- "docs/outputs/expand.py:153:"
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
--8<-- "test/inputs/smoothies/schema.graphql:80:109"
```

## 🔄 Runtime Usage

```python
# Create instance with parameters
smoothie_spec = BananaStrawberrySmoothie(size=Size.LARGE)

# Expand creates the full Smoothie object
full_smoothie = smoothie_spec.expand()  #full_smoothie is of type Smoothie
print(full_smoothie.name)  # "Banana-Strawberry"
print(full_smoothie.size)  # Size.LARGE
print(len(full_smoothie.parts))  # 3 ingredients

```

---

[← Method Directive](03-method-directive.md) | [Next: Default Directive →](05-default-directive.md) 
# 03 - @method Directive

**Instance Methods: Generate Python Methods from Expressions**

## 🎯 Goal

Building on `@compute` fields, the `@method` directive generates actual Python instance methods instead of computed fields. This provides a more natural API for accessing derived data.

## 📋 Schema Input

Copy this content into `method.graphql`:

```graphql
--8<-- "test/inputs/smoothies/schema.graphql:1:86"
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
--8<-- "docs/outputs/method.py"
```

## 🔍 Key Concepts

- **@method directive**: Generates instance methods instead of data fields
- **Expression syntax**: Same mini-DSL as `@compute` directive
- **Method generation**: Creates actual `def method_name(self)` in Python classes
- **Runtime evaluation**: Methods call the same expression engine as computed fields

## 💡 What's New

The `Smoothie` type now has both a computed field and a method:

```python
class Smoothie(BaseModel, Computable):
    # Computed field (accessed via .compute())
    fruit_names: List[str] = Field(default=None, json_schema_extra={'compute': {'expr': 'parts[is Fruit].ingredient.name'}})
    
    # Generated method (accessed directly)
    def get_fruit_names(self) -> Optional[List[str]]:
        return _eval_expr(self, 'parts[is Fruit].ingredient.name')
```

## 🧮 Runtime Usage

```python
from your_module import BananaStrawberrySmoothie, Smoothie, Size

# Create and expand a smoothie
macro = BananaStrawberrySmoothie(size=Size.LARGE, result=Smoothie(name="dummy", size=Size.SMALL, parts=[]))
smoothie = macro.expand()

# Two ways to get the same data:
field_names = smoothie.compute("fruit_names")    # Via computed field
method_names = smoothie.get_fruit_names()        # Via generated method

print(field_names)   # ['Banana', 'Strawberry']
print(method_names)  # ['Banana', 'Strawberry']
assert field_names == method_names  # ✅ Same result
```

## 🔧 Method vs Compute Field

| Feature | @compute field | @method |
|---------|----------------|---------|
| Access pattern | `obj.compute("field_name")` | `obj.method_name()` |
| Type checking | Runtime only | Full IDE support |
| Serialization | Included in model | Not serialized |
| Use case | Data fields | Utility methods |

---

[← Compute Directive](02-compute-directive.md) | [Next: Expand Directive →](04-expand-directive.md) 
# 03 - @method Directive

**Instance Methods: Generate Python Methods from Expressions**

## 🎯 Goal

Building on `@compute` fields, the `@method` directive generates actual Python instance methods instead of computed fields. This provides a more natural API for accessing derived data.

## 📋 Schema Input

Copy this content into `method.graphql`:

```graphql
--8<-- "test/inputs/smoothies/schema.graphql:1:103"
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
--8<-- "docs/outputs/method.py:153:"
```

## 🔍 Key Concepts

- **@method directive**: Generates instance methods instead of data fields
- **@static_method directive**: Generates static factory methods on classes
- **Expression syntax**: Same mini-DSL as `@compute` directive
- **Method generation**: Creates actual `def method_name(self)` in Python classes
- **Static method generation**: Creates `@staticmethod def method_name(*args, **kwargs)`
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

And the `SmoothieFactory` demonstrates static methods:

```python
class SmoothieFactory(BaseModel, Computable):
    @staticmethod
    def empty_small(*_args, **_kw):
        return _eval_expr(globals(), "Smoothie(name='Empty', size=Size.SMALL, parts=[])")
    dummy: Optional[str] = Field(default=None)
```

## 🧮 Runtime Usage

```python
from your_module import BananaStrawberrySmoothie, Smoothie, Size, SmoothieFactory

# Instance methods: Create and expand a smoothie
macro = BananaStrawberrySmoothie(size=Size.LARGE, result=Smoothie(name="dummy", size=Size.SMALL, parts=[]))
smoothie = macro.expand()

# Two ways to get the same data:
field_names = smoothie.compute("fruit_names")    # Via computed field
method_names = smoothie.get_fruit_names()        # Via generated method

print(field_names)   # ['Banana', 'Strawberry']
print(method_names)  # ['Banana', 'Strawberry']
assert field_names == method_names  # ✅ Same result

# Static methods: Factory methods that don't need an instance
empty_smoothie = SmoothieFactory.empty_small()
print(empty_smoothie.name)  # 'Empty'
print(empty_smoothie.size)  # Size.SMALL
print(empty_smoothie.parts) # []
```

## 🔧 Method vs Compute Field vs Static Method

| Feature | @compute field | @method | @static_method |
|---------|----------------|---------|----------------|
| Access pattern | `obj.compute("field_name")` | `obj.method_name()` | `Class.method_name()` |
| Instance required | Yes | Yes | No |
| Type checking | Runtime only | Full IDE support | Full IDE support |
| Serialization | Included in model | Not serialized | Not applicable |
| Use case | Data fields | Utility methods | Factory methods |

---

[← Compute Directive](02-compute-directive.md) | [Next: Expand Directive →](04-expand-directive.md) 
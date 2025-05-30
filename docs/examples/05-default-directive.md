# 05 - @default Directive

**Field Defaults: Auto-Fill Fields with Expression Values**

## 🎯 Goal

The `@default` directive provides a way to automatically fill field values using expressions when no value is explicitly provided. This is useful for setting calculated defaults, constants, or derived values without requiring manual initialization.

## 📋 Schema Input

Copy this content into `default.graphql`:

```graphql
--8<-- "test/inputs/smoothies/schema.graphql:1:73"
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
--8<-- "docs/outputs/default.py:153:"
```

## 🔍 Key Concepts

- **@default directive**: Automatically fills field values when not provided
- **Expression evaluation**: Uses the same expression engine as `@compute`
- **Lazy evaluation**: Values are computed when needed, not at class definition time
- **Computable mixin**: Types with `@default` fields inherit from `Computable`
- **Pydantic integration**: Uses `default_factory` for seamless Pydantic integration

## 💡 What's New

The `ScalarHolder` type demonstrates field defaults:

```python
class ScalarHolder(BaseModel, Computable):
    value: float = Field(default_factory=lambda: _eval_expr(globals(), '3.141592'), json_schema_extra={'default': {'expr': '3.141592'}})
```

## 🧮 Runtime Usage

```python
from your_module import ScalarHolder

# Create instance without providing value
holder = ScalarHolder()  # No value parameter needed!

# The field is automatically filled with the default
print(holder.value)  # 3.141592

# You can still override the default if needed
explicit_holder = ScalarHolder(value=2.718)
print(explicit_holder.value)  # 2.718

# The default computation can be accessed via the compute method
computed_default = holder.compute("value")
print(computed_default)  # 3.141592
```

## 🔧 Default vs Compute vs Method

| Feature | @default | @compute | @method |
|---------|----------|----------|---------|
| When evaluated | At instantiation (if not provided) | On-demand via `.compute()` | On-demand via `.method_name()` |
| Field presence | Creates actual field with value | Creates field, but value computed separately | No field, only method |
| Override behavior | Can be overridden at construction | Always computed, ignores field value | N/A |
| Serialization | Included in model | Included if computed | Not serialized |
| Use case | Smart defaults | Derived data | Utility functions |

## 🎨 Expression Examples

The `@default` directive supports various expression types:

```graphql
type Examples {
  # Simple constants
  pi: Float! @default(expr: "3.141592")
  
  # String literals  
  greeting: String! @default(expr: "'Hello, World!'")
  
  # More complex expressions (when using with other objects)
  timestamp: String! @default(expr: "datetime.now().isoformat()")
}
```

## ⚠️ Important Notes

- Default expressions are evaluated in the global scope, not instance scope
- Simple constants (numbers, strings) are handled efficiently
- Complex expressions use Python's `eval()` for maximum flexibility
- Fields with `@default` make the type inherit from `Computable`

---

[← Expand Directive](04-expand-directive.md) | [Home](../index.md) 
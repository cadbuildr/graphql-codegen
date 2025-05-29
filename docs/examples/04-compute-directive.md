# 04 - @compute Directive

**Dynamic Fields: Runtime Calculation with Python Functions**

## 🎯 Goal

Learn how the `@compute` directive generates fields that calculate values at runtime using custom Python functions.

## 📋 Schema Input

Copy this content into `compute.graphql`:

```graphql
{% include_markdown "../../test/inputs/smoothies/schema.graphql" start="1" end="66" %}
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
{% include_markdown "../outputs/compute.py" %}
```

## 🔍 Key Concepts

- **@compute directive**: Marks fields for runtime calculation
- **Computable mixin**: Automatically added to types with computed fields
- **Function registration**: Use `@register_compute_fn` to provide implementations
- **Metadata**: Compute config stored in `json_schema_extra`

## 💡 What's New

The `IngredientAmount.calories` field now has:
```python
calories: "FloatParameter" = Field(..., json_schema_extra={"compute": {"fn": "calcCalories"}})
```

And the class inherits from `Computable`:
```python
class IngredientAmount(BaseModel, Computable):
```

## 🧮 Runtime Usage

```python
from your_module import IngredientAmount, register_compute_fn

@register_compute_fn("calcCalories")
def calc_calories(instance, field_name, meta):
    # Calculate: grams * calories_per_gram
    grams = instance.grams.value
    cal_per_gram = instance.ingredient.calories_per_gram.value
    return FloatParameter(value=grams * cal_per_gram)

# Usage
banana = Fruit(name="Banana", calories_per_gram=FloatParameter(value=0.89), sweetness=FloatParameter(value=8.5))
amount = IngredientAmount(
    ingredient=banana,
    grams=FloatParameter(value=120)
)
calories = amount.compute("calories")  # Calls your function
print(f"Calories: {calories.value}")  # 106.8
```

---

[← Unions](03-unions.md) | [Next: Expand Directive →](05-expand-directive.md) 
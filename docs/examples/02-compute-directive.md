# 02 - @compute Directive

**Dynamic Fields: Runtime Calculation with Python Functions**

## 🎯 Goal

So far we've used features that most codegen tools would provide. The `@compute` directive goes
beyond type definition and enable you to compute `derivated` fields by providing custom functions for them.


## 📋 Schema Input

Copy this content into `compute.graphql`:

```graphql
--8<-- "test/inputs/smoothies/schema.graphql:1:86"
```

## 🚀 Run It

```bash
poetry run python -m graphql_codegen.cli . --stdout --flat
```

## 🐍 Generated Python

```python
--8<-- "docs/outputs/compute.py"
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

[← Interfaces & Unions](01-interfaces-and-unions.md) | [Next: Method Directive →](03-method-directive.md) 
"""User-defined compute functions for smoothies package.

This file is completely user-managed and contains custom compute functions
referenced by @compute directives in the GraphQL schema.
"""

from smoothies.gen.auto import register_compute_fn


@register_compute_fn("calcCalories")
def calc_calories(instance, field_name: str, meta: dict):
    """Calculate calories for an IngredientAmount based on grams and calories_per_gram."""
    from smoothies.gen.models import FloatParameter

    if (
        not instance.ingredient
        or not instance.grams
        or not instance.ingredient.calories_per_gram
        or not hasattr(instance.grams, "value")
        or not hasattr(instance.ingredient.calories_per_gram, "value")
    ):
        # Handle cases where necessary data might be missing
        return FloatParameter(value=0.0)

    calories = instance.ingredient.calories_per_gram.value * instance.grams.value
    return FloatParameter(value=round(calories, 2))

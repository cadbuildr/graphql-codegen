"""Integration tests for the generated smoothies package."""

import pytest

# These imports assume that the 'smoothies' package (in test/outputs/smoothies)
# is discoverable by pytest, e.g., by running pytest from test/outputs/
# or by having test/outputs in PYTHONPATH.

from smoothies.gen.models import (
    BananaStrawberrySmoothie,
    IngredientAmount,
    Fruit,
    Size,
    Smoothie,  # Ensure Smoothie is imported if used by BananaStrawberrySmoothie
)
from smoothies.gen import auto as smoothies_auto

# Import compute functions to register them


def test_smoothies_package_structure():
    """Test that core components of the smoothies package are available."""
    assert hasattr(
        smoothies_auto, "Computable"
    ), "Computable mixin not found in auto.py"
    assert hasattr(
        smoothies_auto, "Expandable"
    ), "Expandable mixin not found in auto.py"
    # Check for a few key models
    # Import models directly for checking existence
    from smoothies.gen import models as smoothies_models_module

    assert "Smoothie" in dir(smoothies_models_module)
    assert "BananaStrawberrySmoothie" in dir(smoothies_models_module)


def test_smoothies_banana_strawberry_expand():
    """Test the @expand directive on BananaStrawberrySmoothie's result field."""

    # Provide a dummy Smoothie for the required 'result' field during instantiation.
    # Pydantic validates on __init__. The actual expansion happens when .expand() is called.
    dummy_smoothie_payload = Smoothie(name="dummy", size=Size.SMALL, parts=[])
    smoothie_macro = BananaStrawberrySmoothie(
        size=Size.LARGE, result=dummy_smoothie_payload
    )

    # Check that the BananaStrawberrySmoothie has the right setup
    assert "result" in BananaStrawberrySmoothie.model_fields
    result_field_info = BananaStrawberrySmoothie.model_fields["result"]
    assert result_field_info.json_schema_extra is not None
    assert "expand" in result_field_info.json_schema_extra
    assert "into" in result_field_info.json_schema_extra["expand"]

    # The Expandable.expand() method on the *type* BananaStrawberrySmoothie
    # has a fallback to look for a field named 'result' with @expand metadata.
    # _default_expand now builds proper Pydantic models instead of raw dicts.
    expanded_result = smoothie_macro.expand()

    # Check that we get a proper Smoothie instance
    assert isinstance(
        expanded_result, Smoothie
    ), "Expanded result should be a Smoothie instance"
    assert (
        expanded_result.name == "Banana-Strawberry"
    ), "Name should be set from template"
    assert (
        expanded_result.size == Size.LARGE
    ), "Size should be expanded from instance attribute"
    assert len(expanded_result.parts) == 3, "Should have 3 ingredient parts"

    # Check the ingredients are properly built
    part_names = [part.ingredient.name for part in expanded_result.parts]
    expected_names = ["Banana", "Strawberry", "Protein Powder"]
    assert (
        part_names == expected_names
    ), f"Expected ingredients {expected_names}, got {part_names}"

    # Check that parts are proper IngredientAmount instances
    for part in expanded_result.parts:
        assert isinstance(
            part, IngredientAmount
        ), "Each part should be an IngredientAmount instance"
        assert hasattr(part, "ingredient"), "Each part should have an ingredient"
        assert isinstance(part.grams, float), "Grams should be a float"
        assert isinstance(part.calories, float), "Calories should be a float"


def test_smoothies_ingredient_amount_compute():
    """Test the @compute directive on IngredientAmount.calories."""

    # The "calcCalories" function is already registered by importing smoothies.compute_functions
    # No need to re-register it here

    banana = Fruit(name="Banana", calories_per_gram=0.89, sweetness=8.5)
    banana_amount = IngredientAmount(
        ingredient=banana,
        grams=100.0,
        # 'calories' is computed, so initial value can be anything Pydantic allows (e.g. a default or None if Optional)
        # For a non-optional field, Pydantic expects a value or a default_factory.
        # Since it's float!, it must be provided. The @compute should override it.
        calories=-1.0,  # Dummy initial value
    )

    # Check that the IngredientAmount has the @compute setup for 'calories'
    assert "calories" in IngredientAmount.model_fields
    calories_field_info = IngredientAmount.model_fields["calories"]
    assert calories_field_info.json_schema_extra is not None
    assert "compute" in calories_field_info.json_schema_extra
    assert calories_field_info.json_schema_extra["compute"]["fn"] == "calcCalories"

    computed_calories = banana_amount.compute("calories")

    assert isinstance(computed_calories, float)
    assert computed_calories == 89.0

    strawberry = Fruit(name="Strawberry", calories_per_gram=0.32, sweetness=7.2)
    strawberry_amount = IngredientAmount(
        ingredient=strawberry,
        grams=150.0,
        calories=-1.0,  # Dummy initial value
    )
    computed_calories_strawberry = strawberry_amount.compute("calories")
    assert isinstance(computed_calories_strawberry, float)
    assert computed_calories_strawberry == 48.0

    # Test compute on a field without @compute (should fail as per current Computable.compute logic)
    with pytest.raises(ValueError, match="has no valid @compute metadata"):
        banana_amount.compute("grams")

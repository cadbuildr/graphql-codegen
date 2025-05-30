"""Tests for the @method directive functionality."""

from smoothies.gen.models import BananaStrawberrySmoothie, Smoothie, Size


def _build_smoothie():
    macro = BananaStrawberrySmoothie(
        size=Size.LARGE, result=Smoothie(name="dummy", size=Size.SMALL, parts=[])
    )
    return macro.expand()


def test_get_fruit_names_method():
    """Test that @method directive generates working instance methods."""
    smoothie = _build_smoothie()

    # Field version (already tested elsewhere)
    field_names = smoothie.compute("fruit_names")
    assert field_names == ["Banana", "Strawberry"]

    # Method version – NEW
    method_names = smoothie.get_fruit_names()
    assert method_names == ["Banana", "Strawberry"]

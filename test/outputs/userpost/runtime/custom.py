"""Custom runtime functions for userpost.

This is where you register your custom Python functions referenced by
@compute(fn="...") or @expand(into='{"fn": "..."}') directives in your GraphQL schema.

If you renamed 'package:' in codegen.yaml, change the import below.
"""

# Import helpers to register custom functions
from userpost.runtime import register_compute_fn, register_expand_fn


# Example usage:
#
# @register_compute_fn("myComputeFunction")
# def my_compute_function(instance, field_name: str, meta: dict):
#     """Compute function that returns a value for the field."""
#     return "computed_value"
#
# @register_expand_fn("myExpandFunction") 
# def my_expand_function(instance, meta: dict):
#     """Expand function that returns an expanded object or dict."""
#     return {"expanded": "data"} 
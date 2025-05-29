"""Runtime module for userpost.

This module provides easy access to registration functions for custom compute and expand functions.
"""

# Re-export registration functions from auto.py for convenience
from userpost.gen.auto import register_compute_fn, register_expand_fn

__all__ = ["register_compute_fn", "register_expand_fn"] 
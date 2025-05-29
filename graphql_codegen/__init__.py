"""GraphQL Codegen - Convert GraphQL SDL to typed Python with directive-driven behavior."""

__version__ = "0.1.0"

from .generator import generate_from_directory

__all__ = ["generate_from_directory"]

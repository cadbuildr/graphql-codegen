"""Main code generation orchestrator - DEPRECATED.

This module is kept for backward compatibility.
New code should use the generator package directly.
"""

from pathlib import Path
from typing import Optional

from .config import CodegenConfig
from .generator import generate_from_directory as _generate_from_directory
from .generator.types import GenerationResult


def generate_from_directory(
    schema_dir: Path,
    verbose: bool = False,
    override_config: Optional[CodegenConfig] = None,
) -> GenerationResult:
    """
    Main orchestrator function for code generation.

    DEPRECATED: Use graphql_codegen.generator.generate_from_directory instead.
    """
    return _generate_from_directory(schema_dir, verbose, override_config)

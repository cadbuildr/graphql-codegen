"""Generator package for GraphQL code generation."""

from pathlib import Path
from typing import Optional

from ..config import load_config, get_output_path, CodegenConfig
from ..parser import load_and_parse_schema_with_config
from .types import GenerationResult
from .type_collector import collect_types
from .outputs import (
    generate_flat_output,
    generate_package_output,
    generate_stdout_output,
)


def generate_from_directory(
    schema_dir: Path,
    verbose: bool = False,
    override_config: Optional[CodegenConfig] = None,
) -> GenerationResult:
    """
    Main orchestrator function for code generation.
    """
    try:
        # Load configuration
        if override_config:
            config = override_config
        else:
            config = load_config(schema_dir)

        if verbose:
            print(f"Using config: {config}")

        # Parse schema
        schema_info = load_and_parse_schema_with_config(schema_dir, config)

        if verbose:
            print(
                f"Parsed schema with {len(schema_info.types)} types and {len(schema_info.enums)} enums"
            )

        # Handle stdout output
        if config.output == "-":
            generate_stdout_output(config, schema_info, verbose)
            return GenerationResult(success=True)

        # Get output path
        output_path = get_output_path(schema_dir, config)

        # Collect types data
        (
            types_data,
            needs_computable_import,
            needs_expandable_import,
            imports_needed,
        ) = collect_types(schema_info, config)

        # Generate output based on mode
        if config.flat:
            generate_flat_output(
                output_path,
                config,
                types_data,
                schema_info,
                needs_computable_import,
                needs_expandable_import,
                imports_needed,
                verbose,
            )
        else:
            generate_package_output(
                output_path,
                config,
                types_data,
                schema_info,
                needs_computable_import,
                needs_expandable_import,
                imports_needed,
                verbose,
            )

        return GenerationResult(
            success=True,
            package_name=config.package_name,
            output_path=output_path,
        )

    except Exception as e:
        return GenerationResult(
            success=False,
            error=str(e),
        )

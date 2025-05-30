"""Output generation functions for different modes."""

from pathlib import Path
from typing import List, Set
from jinja2 import Environment, FileSystemLoader

from ..config import CodegenConfig
from ..parser import SchemaInfo
from .types import TypeInfo
from .utils import strip_hash_comments


def get_template_env() -> Environment:
    """Get the Jinja2 environment with templates loaded."""
    templates_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    # Add custom filters
    env.filters["repr"] = repr
    return env


def render_flat(
    types_data: List[TypeInfo],
    schema_info: SchemaInfo,
    needs_computable_import: bool,
    needs_expandable_import: bool,
    imports_needed: Set[str],
) -> str:
    """Render flat output to string."""
    env = get_template_env()
    template = env.get_template("flat.py.j2")

    return template.render(
        types=types_data,
        enums=schema_info.enums,
        needs_computable_import=needs_computable_import,
        needs_expandable_import=needs_expandable_import,
        additional_imports=list(imports_needed),
    )


def generate_flat_output(
    output_path: Path,
    config: CodegenConfig,
    types_data: List[TypeInfo],
    schema_info: SchemaInfo,
    needs_computable_import: bool,
    needs_expandable_import: bool,
    imports_needed: Set[str],
    verbose: bool,
):
    """Generate flat file output."""
    rendered = render_flat(
        types_data,
        schema_info,
        needs_computable_import,
        needs_expandable_import,
        imports_needed,
    )

    if verbose:
        print(f"Writing flat output to: {output_path}")

    output_path.write_text(strip_hash_comments(rendered))


def generate_package_output(
    output_path: Path,
    config: CodegenConfig,
    types_data: List[TypeInfo],
    schema_info: SchemaInfo,
    needs_computable_import: bool,
    needs_expandable_import: bool,
    imports_needed: Set[str],
    verbose: bool,
):
    """Generate package structure output."""
    from .package import create_package_structure, generate_package_files

    # Create package directory structure
    create_package_structure(output_path, config, verbose)

    # Generate package files
    generate_package_files(
        output_path,
        config,
        types_data,
        schema_info,
        needs_computable_import,
        needs_expandable_import,
        imports_needed,
        verbose,
    )


def generate_stdout_output(
    config: CodegenConfig, schema_info: SchemaInfo, verbose: bool = False
):
    """Generate output directly to stdout."""
    from .type_collector import collect_types

    (
        types_data,
        needs_computable_import,
        needs_expandable_import,
        imports_needed,
    ) = collect_types(schema_info, config, for_stdout=True)

    rendered = render_flat(
        types_data,
        schema_info,
        needs_computable_import,
        needs_expandable_import,
        imports_needed,
    )

    print(strip_hash_comments(rendered))

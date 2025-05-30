"""Package structure creation and management."""

from pathlib import Path
from typing import List, Set
from ..config import CodegenConfig
from ..parser import SchemaInfo
from .types import TypeInfo
from .outputs import get_template_env


def create_package_structure(
    output_path: Path, config: CodegenConfig, verbose: bool = False
):
    """Create the package directory structure."""
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "gen").mkdir(exist_ok=True)

    if verbose:
        print(f"Created package directory: {output_path}")


def generate_package_files(
    output_path: Path,
    config: CodegenConfig,
    types_data: List[TypeInfo],
    schema_info: SchemaInfo,
    needs_computable_import: bool,
    needs_expandable_import: bool,
    imports_needed: Set[str],
    verbose: bool = False,
):
    """Generate package files (auto.py, models.py, __init__.py)."""
    env = get_template_env()

    # Generate auto.py in gen/ subdirectory
    auto_template = env.get_template("auto.py.j2")
    auto_content = auto_template.render(package_name=config.package_name)
    auto_path = output_path / "gen" / "auto.py"
    auto_path.write_text(auto_content)

    if verbose:
        print(f"Generated: {auto_path}")

    # Generate models.py in gen/ subdirectory
    models_template = env.get_template("models.py.j2")
    models_content = models_template.render(
        types=types_data,
        enums=schema_info.enums,
        needs_computable_import=needs_computable_import,
        needs_expandable_import=needs_expandable_import,
        additional_imports=list(imports_needed),
    )
    models_path = output_path / "gen" / "models.py"
    models_path.write_text(models_content)

    if verbose:
        print(f"Generated: {models_path}")

    # Generate __init__.py in gen/ subdirectory
    init_content = f'"""Generated GraphQL types for {config.package_name}."""\n\nfrom .models import *\nfrom .auto import *\n'
    init_path = output_path / "gen" / "__init__.py"
    init_path.write_text(init_content)

    if verbose:
        print(f"Generated: {init_path}")

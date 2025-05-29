"""Configuration parsing for codegen.yaml files."""

import yaml
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator


class CodegenConfig(BaseModel):
    """Configuration model for codegen.yaml."""

    package: str = Field(..., description="Python package name")
    runtime_package: str = Field(..., description="Runtime package path")
    codegen_version: str = Field(..., description="Codegen version lock")
    scalars: Dict[str, str] = Field(
        default_factory=dict, description="Scalar type mappings"
    )
    templates: Optional[str] = Field(None, description="Custom templates directory")
    flat_output: bool = Field(
        False, description="Generate single file instead of package structure"
    )
    stdout: bool = Field(False, description="Output to stdout instead of files")
    schema_lines: Optional[str] = Field(
        None, description="Line ranges to include from schema (e.g., '1-10,15-20')"
    )
    base_schema: Optional[str] = Field(
        None, description="Path to base schema file to extract lines from"
    )

    @field_validator("package")
    @classmethod
    def validate_package_name(cls, v: str) -> str:
        """Ensure package name is a valid Python identifier."""
        if not v.isidentifier():
            raise ValueError(f"Package name '{v}' is not a valid Python identifier")
        return v

    @field_validator("codegen_version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Ensure codegen version is supported."""
        if v != "0.1":
            raise ValueError(f"Unsupported codegen version '{v}'. Expected '0.1'")
        return v


def load_config(schema_dir: Path) -> CodegenConfig:
    """Load and validate codegen.yaml from schema directory."""
    config_path = schema_dir / "codegen.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"codegen.yaml not found in {schema_dir}")

    try:
        with open(config_path, "r") as f:
            raw_config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {config_path}: {e}")

    try:
        return CodegenConfig(**raw_config)
    except Exception as e:
        raise ValueError(f"Invalid configuration in {config_path}: {e}")


def get_output_path(config: CodegenConfig, schema_dir: Path) -> Path:
    """Determine output path for generated package."""
    # Output goes to test/outputs/<package_name> for test cases
    # For real usage, this could be configurable
    if "test/inputs" in str(schema_dir):
        return schema_dir.parent.parent / "outputs" / config.package
    else:
        return schema_dir.parent / config.package

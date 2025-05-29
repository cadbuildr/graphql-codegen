"""Main code generation orchestrator."""

from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel
import json
import pprint
from jinja2 import Environment, FileSystemLoader

from .config import load_config, get_output_path, CodegenConfig
from .parser import load_and_parse_schema_with_config, SchemaInfo


# Helper function to strip hash comments from a string (typically JSON with comments)
def strip_hash_comments(text_with_comments: str) -> str:
    return "\n".join(
        line.split("#", 1)[0].rstrip()
        for line in text_with_comments.splitlines()
        if line.split("#", 1)[0].strip()
    )


class FieldInfo(BaseModel):
    """Information about a field for template rendering."""

    name: str
    python_type: str
    json_schema_extra: Optional[Dict[str, Any]] = None


class TypeInfo(BaseModel):
    """Information about a type for template rendering."""

    name: str
    base_classes: List[str]
    fields: List[FieldInfo]
    expansion_spec: Optional[str] = None
    kind: str = "object"  # "object", "interface", "union"
    union_types: List[str] = []  # For unions, the member types
    interfaces: List[str] = []  # For interfaces, the interface names


class GenerationResult(BaseModel):
    """Result of code generation process."""

    success: bool
    package_name: Optional[str] = None
    output_path: Optional[Path] = None
    error: Optional[str] = None


def build_field_meta(field, config: CodegenConfig) -> Tuple[str, Optional[Dict[str, Any]], bool, bool]:
    """
    Central helper to extract field metadata and determine requirements.
    Returns: (python_type, json_schema_extra, needs_compute, needs_expand)
    """
    python_type = get_python_type(field.type_name, field.is_list, field.is_required, config)
    
    meta = {}
    needs_compute = False
    needs_expand = False
    
    for directive in field.directives:
        if directive.name == "compute":
            meta["compute"] = {"fn": directive.args.get("fn")}
            needs_compute = True
        elif directive.name == "expand":
            into_value = directive.args.get("into", "{}")
            try:
                into_dict = json.loads(into_value)
                meta["expand"] = {"into": into_dict}
            except json.JSONDecodeError:
                meta["expand"] = {"into": into_value}
            needs_expand = True
    
    json_schema_extra = meta if meta else None
    return python_type, json_schema_extra, needs_compute, needs_expand


def collect_types(schema_info: SchemaInfo, config: CodegenConfig, for_stdout: bool = False) -> Tuple[List[TypeInfo], bool, bool, set]:
    """
    Central function to collect and process types data.
    Returns: (types_data, needs_computable_import, needs_expandable_import, imports_needed)
    """
    types_data = []
    needs_computable_import = False
    needs_expandable_import = False
    imports_needed = set()

    for type_info in schema_info.types:
        if type_info.name in [
            "Query",
            "Mutation", 
            "Subscription",
        ] or type_info.name.endswith("Input"):
            continue

        # Handle different type kinds
        if type_info.kind == "union":
            # For unions, create a type alias
            types_data.append(
                TypeInfo(
                    name=type_info.name,
                    base_classes=[],  # Unions are type aliases, not classes
                    fields=[],
                    kind="union",
                    union_types=type_info.union_types,
                )
            )
            continue

        # Analyze mixins needed
        type_has_compute_on_field = any(
            any(d.name == "compute" for d in f.directives) for f in type_info.fields
        )
        type_has_expand_on_type = any(d.name == "expand" for d in type_info.directives)
        type_has_expand_on_field = any(
            any(d.name == "expand" for d in f.directives) for f in type_info.fields
        )

        inherits_computable = type_has_compute_on_field
        inherits_expandable = type_has_expand_on_type or type_has_expand_on_field

        if inherits_computable:
            needs_computable_import = True
        if inherits_expandable:
            needs_expandable_import = True

        base_classes = []
        # For interfaces, only include BaseModel if no other interfaces are inherited
        if type_info.kind == "interface":
            if type_info.interfaces:
                # Interface inherits from other interfaces - don't add BaseModel
                base_classes.extend(type_info.interfaces)
            else:
                # Root interface - inherits from BaseModel
                base_classes.append("BaseModel")
        else:
            # For objects
            if type_info.interfaces:
                # If object implements interfaces, inherit from interfaces only
                # (interfaces already inherit from BaseModel)
                base_classes.extend(type_info.interfaces)
            else:
                # Object with no interfaces - inherit directly from BaseModel
                base_classes.append("BaseModel")
        
        if inherits_computable:
            base_classes.append("Computable")
        if inherits_expandable:
            base_classes.append("Expandable")

        # Process fields
        fields_data = []
        # Collect interface field names to avoid duplication
        interface_field_names = set()
        for interface_name in type_info.interfaces:
            interface_type = next((t for t in schema_info.types if t.name == interface_name), None)
            if interface_type:
                interface_field_names.update(f.name for f in interface_type.fields)

        for field in type_info.fields:
            # Skip fields that are already defined in interfaces
            if field.name in interface_field_names:
                continue

            python_type, json_schema_extra, field_needs_compute, field_needs_expand = build_field_meta(field, config)
            
            # Handle forward references for stdout mode
            if for_stdout:
                if field.type_name in [t.name for t in schema_info.types if t.name != type_info.name]:
                    python_type = python_type.replace(field.type_name, f'"{field.type_name}"')
                    
            fields_data.append(FieldInfo(
                name=field.name,
                python_type=python_type,
                json_schema_extra=json_schema_extra,
            ))

        # Handle type-level expansion
        expansion_spec = None
        for directive in type_info.directives:
            if directive.name == "expand":
                into_value = directive.args.get("into", "{}")
                try:
                    # Parse JSON to validate and then re-serialize cleanly
                    into_dict = json.loads(into_value)
                    expansion_spec = f"    __expansion__ = {json.dumps(into_dict, indent=4)}"
                except json.JSONDecodeError:
                    # Fallback: use raw value
                    expansion_spec = f"    __expansion__ = {repr(into_value)}"

        types_data.append(TypeInfo(
            name=type_info.name,
            base_classes=base_classes,
            fields=fields_data,
            expansion_spec=expansion_spec,
            kind=type_info.kind,
            interfaces=type_info.interfaces,
            union_types=type_info.union_types if type_info.kind == "union" else [],
        ))

    return types_data, needs_computable_import, needs_expandable_import, imports_needed


def get_template_env() -> Environment:
    """Get Jinja2 environment with templates."""
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    # Add custom filters
    env.filters["repr"] = repr
    return env


def generate_from_directory(
    schema_dir: Path, verbose: bool = False, override_config: Optional[CodegenConfig] = None
) -> GenerationResult:
    """Generate Python package from GraphQL schema directory."""
    try:
        if verbose:
            print(f"Loading configuration from {schema_dir}")

        config = override_config or load_config(schema_dir)

        if verbose:
            print(f"Configuration loaded: package={config.package}")

        if verbose:
            print(f"Parsing GraphQL schema")

        schema_info = load_and_parse_schema_with_config(schema_dir, config)

        if verbose:
            print(
                f"Found {len(schema_info.types)} types and {len(schema_info.scalars)} scalars"
            )

        if config.stdout:
            # Output to stdout instead of files
            generate_stdout_output(config, schema_info, verbose)
            return GenerationResult(success=True, package_name=config.package)
        else:
            output_path = get_output_path(config, schema_dir)

            if verbose:
                print(f"Output path: {output_path}")

            create_package_structure(output_path, config, verbose)
            generate_package_files(output_path, config, schema_info, verbose)

            return GenerationResult(
                success=True, package_name=config.package, output_path=output_path
            )

    except Exception as e:
        return GenerationResult(success=False, error=str(e))


def create_package_structure(
    output_path: Path, config: CodegenConfig, verbose: bool = False
):
    """Create the basic package directory structure."""
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "gen").mkdir(exist_ok=True)

    if verbose:
        print(f"Created directory structure at {output_path}")


def generate_package_files(
    output_path: Path,
    config: CodegenConfig,
    schema_info: SchemaInfo,
    verbose: bool = False,
):
    """Generate the package files using templates."""
    env = get_template_env()

    # Process types and gather template data
    types_data, needs_computable_import, needs_expandable_import, imports_needed = collect_types(schema_info, config, for_stdout=False)

    if config.flat_output:
        # Generate everything in a single file
        generate_flat_output(output_path, config, types_data, schema_info, needs_computable_import, needs_expandable_import, imports_needed, verbose)
    else:
        # Generate package structure
        generate_package_output(output_path, config, types_data, schema_info, needs_computable_import, needs_expandable_import, imports_needed, verbose)


def generate_flat_output(output_path: Path, config: CodegenConfig, types_data, schema_info, needs_computable_import, needs_expandable_import, imports_needed, verbose: bool):
    """Generate a single file output."""
    env = get_template_env()
    
    # Use the shared flat template
    template = env.get_template("flat.py.j2")
    content = template.render(
        types=types_data,
        needs_computable_import=needs_computable_import,
        needs_expandable_import=needs_expandable_import,
        enums=schema_info.enums,
        additional_imports=list(imports_needed),
    )
    
    output_file = output_path / f"{config.package}.py"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(content)
    
    if verbose:
        print(f"Generated flat file: {output_file}")


def generate_package_output(output_path: Path, config: CodegenConfig, types_data, schema_info, needs_computable_import, needs_expandable_import, imports_needed, verbose: bool):
    """Generate package structure output."""
    env = get_template_env()

    # Generate files using templates

    # 1. Package __init__.py
    package_init_template = env.get_template("package_init.py.j2")
    package_init_content = package_init_template.render(package_name=config.package)
    with open(output_path / "__init__.py", "w") as f:
        f.write(package_init_content)

    # 2. models.py
    models_template = env.get_template("models.py.j2")
    models_content = models_template.render(
        types=types_data,
        needs_computable_import=needs_computable_import,
        needs_expandable_import=needs_expandable_import,
        enums=schema_info.enums,
        additional_imports=list(imports_needed),
    )
    with open(output_path / "gen" / "models.py", "w") as f:
        f.write(models_content)

    # 3. auto.py
    auto_template = env.get_template("auto.py.j2")
    auto_content = auto_template.render(package_name=config.package)
    with open(output_path / "gen" / "auto.py", "w") as f:
        f.write(auto_content)

    if verbose:
        print(f"Generated package files in {output_path}")


def get_python_type(
    graphql_type: str, is_list: bool, is_required: bool, config: CodegenConfig
) -> str:
    """Convert GraphQL type to Python type annotation."""
    if graphql_type in config.scalars:
        python_type = config.scalars[graphql_type]
    else:
        python_type = graphql_type

    if is_list:
        python_type = f"List[{python_type}]"

    if not is_required:
        python_type = f"Optional[{python_type}]"

    return python_type


def generate_stdout_output(config: CodegenConfig, schema_info: SchemaInfo, verbose: bool = False):
    """Generate output to stdout instead of files."""
    import sys
    
    if config.flat_output:
        # Generate flat output to stdout
        env = get_template_env()
        
        # Process types (simplified version of the main processing logic)
        types_data, needs_computable_import, needs_expandable_import, imports_needed = collect_types(schema_info, config, for_stdout=True)
        
        # Use the shared flat template
        template = env.get_template("flat.py.j2")
        content = template.render(
            types=types_data,
            needs_computable_import=needs_computable_import,
            needs_expandable_import=needs_expandable_import,
            enums=schema_info.enums,
            additional_imports=list(imports_needed),
        )
        
        print(content)
        
    else:
        print("# Package structure output not supported for stdout mode", file=sys.stderr)
        print("# Use flat_output: true for stdout mode", file=sys.stderr)
        sys.exit(1)

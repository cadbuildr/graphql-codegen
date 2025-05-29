"""Main code generation orchestrator."""

from pathlib import Path
from typing import Optional, Dict, Any, List
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
    types_data = []
    needs_computable_import = False
    needs_expandable_import = False

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
            union_member_types = " | ".join([f'"{t}"' for t in type_info.union_types])
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
            # Skip fields that are inherited from interfaces
            if field.name in interface_field_names and type_info.interfaces:
                continue
                
            python_type = get_python_type(
                field.type_name, field.is_list, field.is_required, config
            )
            if field.type_name in [
                t.name for t in schema_info.types if t.name != type_info.name
            ]:
                python_type = python_type.replace(
                    field.type_name, f'"{field.type_name}"'
                )

            meta_for_json_schema_extra = {}

            # Handle @compute directive
            compute_directive = next(
                (d for d in field.directives if d.name == "compute"), None
            )
            if compute_directive:
                meta_for_json_schema_extra["compute"] = {
                    "fn": compute_directive.args.get("fn")
                }

            # Handle @expand directive on field
            expand_directive_field = next(
                (d for d in field.directives if d.name == "expand"), None
            )
            if expand_directive_field:
                into_json_str_with_comments = expand_directive_field.args.get(
                    "into", "{}"
                )
                into_json_str_stripped = strip_hash_comments(
                    into_json_str_with_comments
                )
                try:
                    into_dict = json.loads(into_json_str_stripped)
                    meta_for_json_schema_extra["expand"] = {"into": into_dict}
                except json.JSONDecodeError:
                    meta_for_json_schema_extra["expand"] = {
                        "into": into_json_str_stripped
                    }

            fields_data.append(
                FieldInfo(
                    name=field.name,
                    python_type=python_type,
                    json_schema_extra=meta_for_json_schema_extra
                    if meta_for_json_schema_extra
                    else None,
                )
            )

        # Handle @expand directive on type
        expansion_spec = None
        expand_directive_type = next(
            (d for d in type_info.directives if d.name == "expand"), None
        )
        if expand_directive_type:
            into_value = expand_directive_type.args.get("into", "{}")
            
            # Check if it's a simple string (function name) or JSON
            if into_value.strip().startswith("{"):
                # It's JSON, parse it
                into_json_str_stripped = strip_hash_comments(into_value)
                try:
                    expansion_dict = json.loads(into_json_str_stripped)
                    expansion_data_formatted = pprint.pformat(
                        expansion_dict, indent=1, width=80, sort_dicts=False
                    )
                    indented_expansion_data = "\n".join(
                        [f"        {line}" for line in expansion_data_formatted.split("\n")]
                    )
                    expansion_spec = f"    __expansion__: Dict[str, Any] = (\n{indented_expansion_data}\n    )\n"
                except json.JSONDecodeError:
                    expansion_spec = f"    # Failed to parse @expand into JSON: {into_value}\n"
            else:
                # It's a function name, create a simple expansion spec
                expansion_spec = f'    __expansion_fn__: str = "{into_value}"\n'

        types_data.append(
            TypeInfo(
                name=type_info.name,
                base_classes=base_classes,
                fields=fields_data,
                expansion_spec=expansion_spec,
                kind=type_info.kind,
                union_types=type_info.union_types if type_info.kind == "union" else [],
                interfaces=type_info.interfaces,
            )
        )

    # Determine required imports
    imports_needed = set()
    for scalar_name, python_type in config.scalars.items():
        if "datetime" in python_type:
            imports_needed.add("import datetime")
        if "typing" in python_type:
            imports_needed.add("import typing")

    if config.flat_output:
        # Generate everything in a single file
        generate_flat_output(output_path, config, types_data, schema_info, needs_computable_import, needs_expandable_import, imports_needed, verbose)
    else:
        # Generate package structure
        generate_package_output(output_path, config, types_data, schema_info, needs_computable_import, needs_expandable_import, imports_needed, verbose)


def generate_flat_output(output_path: Path, config: CodegenConfig, types_data, schema_info, needs_computable_import, needs_expandable_import, imports_needed, verbose: bool):
    """Generate a single file output."""
    env = get_template_env()
    
    # Create single file template
    flat_template_content = '''from __future__ import annotations
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field
from enum import Enum
{%- if additional_imports %}
{%- for import_line in additional_imports %}
{{ import_line }}
{%- endfor %}
{%- endif %}
import json

# Auto-generated helpers - inline
_COMPUTE: Dict[str, Any] = {}
_EXPAND_CUSTOM: Dict[str, Any] = {}

{% if needs_computable_import %}
class Computable:
    """Mixin for types with @compute fields."""
    def compute(self, field_name: str) -> Any:
        """Compute value for field with @compute directive."""
        if not hasattr(self.__class__, "model_fields"):
            raise TypeError(f"{self.__class__.__name__} is not a Pydantic model, cannot use Computable.")
        fld = self.__class__.model_fields.get(field_name)
        if not fld:
            raise ValueError(f"Field '{field_name}' not found in model {self.__class__.__name__}.")
        meta = fld.json_schema_extra or {}
        compute_meta = meta.get("compute")
        if not compute_meta or not isinstance(compute_meta, dict):
            raise ValueError(f"Field '{field_name}' in model {self.__class__.__name__} has no valid @compute metadata.")
        fn_name = compute_meta.get("fn")
        if not fn_name:
            raise ValueError(f"Compute metadata for '{field_name}' is missing 'fn'.")
        return _COMPUTE[fn_name](self, field_name, compute_meta)
{% endif %}

{% if needs_expandable_import %}
class Expandable:
    """Mixin for types with @expand directive."""
    def expand(self) -> Any:
        """Expand this node into primitive components."""
        # Simplified expand implementation for flat output
        return self
{% endif %}

# Registration functions
def register_compute_fn(name: str):
    def _wrap(fn):
        _COMPUTE[name] = fn
        return fn
    return _wrap

def register_expand_fn(name: str):
    def _wrap(fn):
        _EXPAND_CUSTOM[name] = fn
        return fn
    return _wrap

{%- for enum_info in enums %}

class {{ enum_info.name }}(str, Enum):
    """Generated from GraphQL enum {{ enum_info.name }}."""
{%- for value in enum_info.values %}
    {{ value }} = "{{ value }}"
{%- endfor %}
{%- endfor %}

{%- for type_info in types %}
{%- if type_info.kind != "union" %}

class {{ type_info.name }}({{ type_info.base_classes | join(", ") }}):
    """Generated from GraphQL {{ type_info.kind }} {{ type_info.name }}."""
{%- for field in type_info.fields %}
    {{ field.name }}: {{ field.python_type }} = Field({% if field.python_type.startswith("Optional[") %}default=None{% else %}...{% endif %}{% if field.json_schema_extra %}, json_schema_extra={{ field.json_schema_extra | repr }}{% endif %})
{%- endfor %}
{%- if type_info.expansion_spec %}
{{ type_info.expansion_spec }}
{%- endif %}
    model_config = {"protected_namespaces": ()}  # Pydantic v2 config
{%- endif %}
{%- endfor %}

# Union type aliases
{%- for type_info in types %}
{%- if type_info.kind == "union" %}
{{ type_info.name }} = Union[{% for union_type in type_info.union_types %}"{{ union_type }}"{% if not loop.last %}, {% endif %}{% endfor %}]
{%- endif %}
{%- endfor %}

# Rebuild models to resolve forward references and inheritance
{%- for type_info in types %}
{%- if type_info.kind != "union" %}
{{ type_info.name }}.model_rebuild()
{%- endif %}
{%- endfor %}
'''
    
    env.from_string(flat_template_content)
    template = env.from_string(flat_template_content)
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
        types_data = []
        needs_computable_import = False
        needs_expandable_import = False
        
        for type_info in schema_info.types:
            if type_info.name in ["Query", "Mutation", "Subscription"] or type_info.name.endswith("Input"):
                continue
                
            # Handle unions
            if type_info.kind == "union":
                types_data.append(TypeInfo(
                    name=type_info.name,
                    base_classes=[],
                    fields=[],
                    kind="union",
                    union_types=type_info.union_types,
                ))
                continue
                
            # Check for mixins
            type_has_compute = any(any(d.name == "compute" for d in f.directives) for f in type_info.fields)
            type_has_expand = any(d.name == "expand" for d in type_info.directives) or any(any(d.name == "expand" for d in f.directives) for f in type_info.fields)
            
            if type_has_compute:
                needs_computable_import = True
            if type_has_expand:
                needs_expandable_import = True
                
            base_classes = []
            if type_info.kind == "interface":
                if type_info.interfaces:
                    base_classes.extend(type_info.interfaces)
                else:
                    base_classes.append("BaseModel")
            else:
                if type_info.interfaces:
                    base_classes.extend(type_info.interfaces)
                else:
                    base_classes.append("BaseModel")
            
            if type_has_compute:
                base_classes.append("Computable")
            if type_has_expand:
                base_classes.append("Expandable")
                
            # Process fields (simplified)
            fields_data = []
            for field in type_info.fields:
                python_type = get_python_type(field.type_name, field.is_list, field.is_required, config)
                if field.type_name in [t.name for t in schema_info.types if t.name != type_info.name]:
                    python_type = python_type.replace(field.type_name, f'"{field.type_name}"')
                    
                meta = {}
                for directive in field.directives:
                    if directive.name == "compute":
                        meta["compute"] = {"fn": directive.args.get("fn")}
                    elif directive.name == "expand":
                        into_value = directive.args.get("into", "{}")
                        try:
                            into_dict = json.loads(into_value)
                            meta["expand"] = {"into": into_dict}
                        except json.JSONDecodeError:
                            meta["expand"] = {"into": into_value}
                            
                fields_data.append(FieldInfo(
                    name=field.name,
                    python_type=python_type,
                    json_schema_extra=meta if meta else None,
                ))
                
            types_data.append(TypeInfo(
                name=type_info.name,
                base_classes=base_classes,
                fields=fields_data,
                kind=type_info.kind,
                interfaces=type_info.interfaces,
                union_types=type_info.union_types if type_info.kind == "union" else [],
            ))
        
        # Generate flat template content (reuse from generate_flat_output)
        flat_template_content = '''from __future__ import annotations
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field
from enum import Enum
import json

# Auto-generated helpers - inline
_COMPUTE: Dict[str, Any] = {}
_EXPAND_CUSTOM: Dict[str, Any] = {}

{% if needs_computable_import %}
class Computable:
    """Mixin for types with @compute fields."""
    def compute(self, field_name: str) -> Any:
        if not hasattr(self.__class__, "model_fields"):
            raise TypeError(f"{self.__class__.__name__} is not a Pydantic model.")
        fld = self.__class__.model_fields.get(field_name)
        if not fld:
            raise ValueError(f"Field '{field_name}' not found.")
        meta = fld.json_schema_extra or {}
        compute_meta = meta.get("compute")
        if not compute_meta:
            raise ValueError(f"Field '{field_name}' has no @compute metadata.")
        fn_name = compute_meta.get("fn")
        if not fn_name:
            raise ValueError(f"Compute metadata missing 'fn'.")
        return _COMPUTE[fn_name](self, field_name, compute_meta)
{% endif %}

{% if needs_expandable_import %}
class Expandable:
    """Mixin for types with @expand directive."""
    def expand(self) -> Any:
        return self
{% endif %}

def register_compute_fn(name: str):
    def _wrap(fn):
        _COMPUTE[name] = fn
        return fn
    return _wrap

def register_expand_fn(name: str):
    def _wrap(fn):
        _EXPAND_CUSTOM[name] = fn
        return fn
    return _wrap

{%- for enum_info in enums %}

class {{ enum_info.name }}(str, Enum):
{%- for value in enum_info.values %}
    {{ value }} = "{{ value }}"
{%- endfor %}
{%- endfor %}

{%- for type_info in types %}
{%- if type_info.kind != "union" %}

class {{ type_info.name }}({{ type_info.base_classes | join(", ") }}):
{%- for field in type_info.fields %}
    {{ field.name }}: {{ field.python_type }} = Field({% if field.python_type.startswith("Optional[") %}default=None{% else %}...{% endif %}{% if field.json_schema_extra %}, json_schema_extra={{ field.json_schema_extra | repr }}{% endif %})
{%- endfor %}
    model_config = {"protected_namespaces": ()}
{%- endif %}
{%- endfor %}

{%- for type_info in types %}
{%- if type_info.kind == "union" %}
{{ type_info.name }} = Union[{% for union_type in type_info.union_types %}"{{ union_type }}"{% if not loop.last %}, {% endif %}{% endfor %}]
{%- endif %}
{%- endfor %}

{%- for type_info in types %}
{%- if type_info.kind != "union" %}
{{ type_info.name }}.model_rebuild()
{%- endif %}
{%- endfor %}
'''
        
        template = env.from_string(flat_template_content)
        content = template.render(
            types=types_data,
            needs_computable_import=needs_computable_import,
            needs_expandable_import=needs_expandable_import,
            enums=schema_info.enums,
        )
        
        print(content)
        
    else:
        print("# Package structure output not supported for stdout mode", file=sys.stderr)
        print("# Use flat_output: true for stdout mode", file=sys.stderr)
        sys.exit(1)

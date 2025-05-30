"""Type collection and processing logic."""

from typing import List, Tuple, Set
from ..config import CodegenConfig
from ..parser import SchemaInfo
from .types import TypeInfo, FieldInfo, MethodInfo
from .utils import build_field_meta


def collect_types(
    schema_info: SchemaInfo, config: CodegenConfig, for_stdout: bool = False
) -> Tuple[List[TypeInfo], bool, bool, Set[str]]:
    """
    Central function to collect and process types data.
    Returns: (types_data, needs_computable_import, needs_expandable_import, imports_needed)
    """
    types_data = []
    needs_computable_import = False
    needs_expandable_import = False
    imports_needed: Set[str] = set()

    # Analyze scalar mappings to determine required imports
    for scalar_type, python_type in config.scalars.items():
        if "datetime" in python_type:
            imports_needed.add("import datetime")
        elif "typing." in python_type:
            imports_needed.add("import typing")

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
        type_has_method_directive = any(
            any(d.name == "method" for d in f.directives) for f in type_info.fields
        )
        # NEW: Check for @default and @static_method directives
        type_has_default_on_field = any(
            any(d.name == "default" for d in f.directives) for f in type_info.fields
        )
        type_has_static_method = any(
            d.name == "static_method" for d in type_info.directives
        )

        inherits_computable = (
            type_has_compute_on_field
            or type_has_default_on_field
            or type_has_static_method
        )
        inherits_expandable = type_has_expand_on_type or type_has_expand_on_field

        if inherits_computable:
            needs_computable_import = True
        if inherits_expandable:
            needs_expandable_import = True
        # Methods that use expressions also need _eval_expr import
        if type_has_method_directive:
            needs_computable_import = True

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

        # Collect interface field names to avoid duplication
        interface_field_names: Set[str] = set()
        for interface_name in type_info.interfaces:
            interface_type = next(
                (t for t in schema_info.types if t.name == interface_name), None
            )
            if interface_type:
                interface_field_names.update(f.name for f in interface_type.fields)

        # Process fields and methods
        fields_data = []
        methods_data = []

        for field in type_info.fields:
            # Skip fields that are already defined in interfaces
            if field.name in interface_field_names:
                continue

            # Check for @method directive
            meth_dir = next((d for d in field.directives if d.name == "method"), None)
            if meth_dir:
                from .utils import get_python_type

                methods_data.append(
                    MethodInfo(
                        name=field.name,
                        return_type=get_python_type(
                            field.type_name, field.is_list, False, config
                        ),
                        expr=meth_dir.args.get("expr"),
                        fn=meth_dir.args.get("fn"),
                    )
                )
                continue  # do NOT emit as Pydantic field

            # Process regular fields
            python_type, json_schema_extra, _, _ = build_field_meta(field, config)

            # Handle forward references for stdout mode
            if for_stdout:
                if field.type_name in [
                    t.name for t in schema_info.types if t.name != type_info.name
                ]:
                    python_type = python_type.replace(
                        field.type_name, f'"{field.type_name}"'
                    )

            fields_data.append(
                FieldInfo(
                    name=field.name,
                    python_type=python_type,
                    json_schema_extra=json_schema_extra,
                )
            )

        # Process static methods (from @static_method directives on types)
        static_methods_data = []
        for directive in type_info.directives:
            if directive.name == "static_method":
                name = directive.args.get("name")
                expr = directive.args.get("expr")
                if name and expr:
                    static_methods_data.append(
                        MethodInfo(
                            name=name,
                            return_type="Any",  # Static methods can return anything
                            expr=expr,
                        )
                    )

        # Handle type-level expansion
        expansion_spec = None
        for directive in type_info.directives:
            if directive.name == "expand":
                into_value = directive.args.get("into", "{}")
                from .utils import parse_into

                into_dict = parse_into(into_value)
                if isinstance(into_dict, dict):
                    import json

                    # Parse JSON to validate and then re-serialize cleanly
                    expansion_spec = (
                        f"    __expansion__ = {json.dumps(into_dict, indent=4)}"
                    )
                else:
                    # Fallback: use raw value
                    expansion_spec = f"    __expansion__ = {repr(into_dict)}"

        types_data.append(
            TypeInfo(
                name=type_info.name,
                base_classes=base_classes,
                fields=fields_data,
                methods=methods_data,
                static_methods=static_methods_data,
                expansion_spec=expansion_spec,
                kind=type_info.kind,
                interfaces=type_info.interfaces,
                union_types=type_info.union_types if type_info.kind == "union" else [],
            )
        )

    return types_data, needs_computable_import, needs_expandable_import, imports_needed

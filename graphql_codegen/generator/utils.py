"""Utility functions for code generation."""

import json
from typing import Dict, Any, Tuple, Optional
from ..config import CodegenConfig


def strip_hash_comments(text_with_comments: str) -> str:
    """Remove lines starting with # from generated output."""
    lines = text_with_comments.split("\n")
    return "\n".join(line for line in lines if not line.strip().startswith("#"))


def parse_into(value: str) -> dict:
    """Parse 'into' JSON value from directive args, with fallback handling."""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


def get_python_type(
    graphql_type: str, is_list: bool, is_required: bool, config: CodegenConfig
) -> str:
    """Convert GraphQL type to Python type string."""
    # Handle scalar types first
    if graphql_type in config.scalars:
        python_type = config.scalars[graphql_type]
    else:
        # Default mapping for standard types
        python_type = {
            "String": "str",
            "Int": "int",
            "Float": "float",
            "Boolean": "bool",
            "ID": "str",
        }.get(graphql_type, graphql_type)

    # Handle lists
    if is_list:
        python_type = f"List[{python_type}]"

    # Handle optionals
    if not is_required:
        python_type = f"Optional[{python_type}]"

    return python_type


def build_field_meta(
    field, config: CodegenConfig
) -> Tuple[str, Optional[Dict[str, Any]], bool, bool]:
    """
    Central helper to extract field metadata and determine requirements.
    Returns: (python_type, json_schema_extra, needs_compute, needs_expand)
    """
    python_type = get_python_type(
        field.type_name, field.is_list, field.is_required, config
    )

    meta = {}
    needs_compute = False
    needs_expand = False

    for directive in field.directives:
        if directive.name == "compute":
            # minimal support: either fn **or** expr
            if "expr" in directive.args:
                meta["compute"] = {"expr": directive.args["expr"]}
            else:
                meta["compute"] = {"fn": directive.args.get("fn")}
            needs_compute = True
        elif directive.name == "expand":
            into_value = directive.args.get("into", "{}")
            into_dict = parse_into(into_value)
            meta["expand"] = {"into": into_dict}
            needs_expand = True
        elif directive.name == "default":
            # NEW: honour @default(expr:"…")
            expr = directive.args.get("expr")
            if expr:
                meta["default"] = {"expr": expr}

    json_schema_extra = meta if meta else None
    return python_type, json_schema_extra, needs_compute, needs_expand

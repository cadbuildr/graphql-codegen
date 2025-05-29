"""GraphQL schema parsing with directive extraction."""

from pathlib import Path
from typing import Dict, List, Any
from pydantic import BaseModel
from graphql import (
    build_schema,
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLInterfaceType,
    GraphQLUnionType,
    GraphQLEnumType,
    GraphQLDirective,
)
from graphql.type.definition import (
    GraphQLType,
    GraphQLScalarType,
    GraphQLList,
    GraphQLNonNull,
)


class DirectiveInfo(BaseModel):
    """Information about a directive applied to a field or type."""

    name: str
    args: Dict[str, Any]


class FieldInfo(BaseModel):
    """Information about a GraphQL field."""

    name: str
    type_name: str
    is_list: bool = False
    is_required: bool = False
    directives: List[DirectiveInfo] = []


class TypeInfo(BaseModel):
    """Information about a GraphQL type."""

    name: str
    fields: List[FieldInfo] = []
    directives: List[DirectiveInfo] = []
    kind: str = "object"  # "object", "interface", "union"
    interfaces: List[str] = []  # For object types that implement interfaces
    union_types: List[str] = []  # For union types


class EnumInfo(BaseModel):
    """Information about a GraphQL enum."""

    name: str
    values: List[str] = []


class SchemaInfo(BaseModel):
    """Parsed GraphQL schema information."""

    types: List[TypeInfo] = []
    scalars: List[str] = []
    enums: List[EnumInfo] = []


def parse_schema_file(schema_path: Path) -> GraphQLSchema:
    """Parse GraphQL schema from file."""
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "r") as f:
        schema_text = f.read()

    try:
        return build_schema(schema_text)
    except Exception as e:
        raise ValueError(f"Failed to parse GraphQL schema: {e}")


def extract_type_name(graphql_type: GraphQLType) -> tuple[str, bool, bool]:
    """Extract type name, list flag, and required flag from GraphQL type."""
    is_required = False
    is_list = False

    # Unwrap NonNull
    if isinstance(graphql_type, GraphQLNonNull):
        is_required = True
        graphql_type = graphql_type.of_type

    # Unwrap List
    if isinstance(graphql_type, GraphQLList):
        is_list = True
        graphql_type = graphql_type.of_type

        # Handle NonNull inside List
        if isinstance(graphql_type, GraphQLNonNull):
            graphql_type = graphql_type.of_type

    # Get name from GraphQL type - check if it has name attribute
    name = getattr(graphql_type, "name", str(graphql_type))
    return name, is_list, is_required


def extract_directive_info(directives: List[GraphQLDirective]) -> List[DirectiveInfo]:
    """Extract directive information from GraphQL directives."""
    directive_infos = []

    for directive in directives:
        args = {}
        # Check if directive has arguments attribute
        if hasattr(directive, "arguments") and directive.arguments:
            for arg_name, arg_value in directive.arguments.items():
                # Handle different argument types
                if hasattr(arg_value, "value"):
                    args[arg_name] = arg_value.value
                else:
                    args[arg_name] = str(arg_value)

        directive_infos.append(DirectiveInfo(name=directive.name, args=args))

    return directive_infos


def parse_schema_info(schema: GraphQLSchema) -> SchemaInfo:
    """Extract structured information from GraphQL schema."""
    types = []
    scalars = []
    enums = []

    for type_name, graphql_type in schema.type_map.items():
        # Skip built-in types
        if type_name.startswith("__"):
            continue

        if isinstance(graphql_type, GraphQLScalarType):
            scalars.append(type_name)

        elif isinstance(graphql_type, GraphQLEnumType):
            enum_values = []
            if hasattr(graphql_type, "values"):
                enum_values = list(graphql_type.values.keys())
            enums.append(EnumInfo(name=type_name, values=enum_values))

        elif isinstance(graphql_type, GraphQLObjectType):
            fields = []

            for field_name, field in graphql_type.fields.items():
                field_type_name, is_list, is_required = extract_type_name(field.type)

                # Extract directives from field AST node if available
                field_directives = []
                if (
                    hasattr(field, "ast_node")
                    and field.ast_node
                    and field.ast_node.directives
                ):
                    for directive_node in field.ast_node.directives:
                        args = {}
                        if directive_node.arguments:
                            for arg in directive_node.arguments:
                                # Handle string values
                                if hasattr(arg.value, "value"):
                                    args[arg.name.value] = arg.value.value
                                else:
                                    args[arg.name.value] = str(arg.value)
                        field_directives.append(
                            DirectiveInfo(name=directive_node.name.value, args=args)
                        )

                fields.append(
                    FieldInfo(
                        name=field_name,
                        type_name=field_type_name,
                        is_list=is_list,
                        is_required=is_required,
                        directives=field_directives,
                    )
                )

            # Extract type-level directives
            type_directives = []
            if (
                hasattr(graphql_type, "ast_node")
                and graphql_type.ast_node
                and graphql_type.ast_node.directives
            ):
                for directive_node in graphql_type.ast_node.directives:
                    args = {}
                    if directive_node.arguments:
                        for arg in directive_node.arguments:
                            if hasattr(arg.value, "value"):
                                args[arg.name.value] = arg.value.value
                            else:
                                args[arg.name.value] = str(arg.value)
                    type_directives.append(
                        DirectiveInfo(name=directive_node.name.value, args=args)
                    )

            # Extract interfaces that this object implements
            interfaces = []
            if hasattr(graphql_type, "interfaces"):
                interfaces = [iface.name for iface in graphql_type.interfaces]

            types.append(
                TypeInfo(
                    name=type_name,
                    fields=fields,
                    directives=type_directives,
                    kind="object",
                    interfaces=interfaces,
                )
            )

        elif isinstance(graphql_type, GraphQLInterfaceType):
            fields = []

            for field_name, field in graphql_type.fields.items():
                field_type_name, is_list, is_required = extract_type_name(field.type)

                # Extract directives from field AST node if available
                field_directives = []
                if (
                    hasattr(field, "ast_node")
                    and field.ast_node
                    and field.ast_node.directives
                ):
                    for directive_node in field.ast_node.directives:
                        args = {}
                        if directive_node.arguments:
                            for arg in directive_node.arguments:
                                if hasattr(arg.value, "value"):
                                    args[arg.name.value] = arg.value.value
                                else:
                                    args[arg.name.value] = str(arg.value)
                        field_directives.append(
                            DirectiveInfo(name=directive_node.name.value, args=args)
                        )

                fields.append(
                    FieldInfo(
                        name=field_name,
                        type_name=field_type_name,
                        is_list=is_list,
                        is_required=is_required,
                        directives=field_directives,
                    )
                )

            # Extract type-level directives
            type_directives = []
            if (
                hasattr(graphql_type, "ast_node")
                and graphql_type.ast_node
                and graphql_type.ast_node.directives
            ):
                for directive_node in graphql_type.ast_node.directives:
                    args = {}
                    if directive_node.arguments:
                        for arg in directive_node.arguments:
                            if hasattr(arg.value, "value"):
                                args[arg.name.value] = arg.value.value
                            else:
                                args[arg.name.value] = str(arg.value)
                    type_directives.append(
                        DirectiveInfo(name=directive_node.name.value, args=args)
                    )

            # Extract interfaces that this interface implements
            interfaces = []
            if hasattr(graphql_type, "interfaces"):
                interfaces = [iface.name for iface in graphql_type.interfaces]

            types.append(
                TypeInfo(
                    name=type_name,
                    fields=fields,
                    directives=type_directives,
                    kind="interface",
                    interfaces=interfaces,
                )
            )

        elif isinstance(graphql_type, GraphQLUnionType):
            # For unions, extract the member types
            union_types = []
            if hasattr(graphql_type, "types"):
                union_types = [member.name for member in graphql_type.types]

            # Extract type-level directives
            type_directives = []
            if (
                hasattr(graphql_type, "ast_node")
                and graphql_type.ast_node
                and graphql_type.ast_node.directives
            ):
                for directive_node in graphql_type.ast_node.directives:
                    args = {}
                    if directive_node.arguments:
                        for arg in directive_node.arguments:
                            if hasattr(arg.value, "value"):
                                args[arg.name.value] = arg.value.value
                            else:
                                args[arg.name.value] = str(arg.value)
                    type_directives.append(
                        DirectiveInfo(name=directive_node.name.value, args=args)
                    )

            types.append(
                TypeInfo(
                    name=type_name,
                    fields=[],  # Unions don't have fields
                    directives=type_directives,
                    kind="union",
                    union_types=union_types,
                )
            )

    return SchemaInfo(types=types, scalars=scalars, enums=enums)


def load_and_parse_schema(schema_dir: Path) -> SchemaInfo:
    """Load schema file and parse into structured information."""
    schema_path = schema_dir / "schema.graphql"
    schema = parse_schema_file(schema_path)
    return parse_schema_info(schema)


def load_and_parse_schema_with_config(schema_dir: Path, config) -> SchemaInfo:
    """Load schema with potential line extraction based on config."""
    if config.base_schema and config.schema_lines:
        # Extract lines from base schema
        base_schema_path = Path(config.base_schema)
        if not base_schema_path.is_absolute():
            # Make path relative to current working directory, not schema_dir
            base_schema_path = Path.cwd() / base_schema_path
        schema_content = extract_schema_lines(base_schema_path, config.schema_lines)
        schema = build_schema(schema_content)
    else:
        # Use regular schema file
        schema_path = schema_dir / "schema.graphql"
        schema = parse_schema_file(schema_path)

    return parse_schema_info(schema)


def extract_schema_lines(schema_path: Path, line_ranges: str) -> str:
    """Extract specific lines from a schema file based on line ranges.

    Args:
        schema_path: Path to the schema file
        line_ranges: String like "1-10,15-20,25" specifying which lines to include

    Returns:
        Extracted schema content as string
    """
    with open(schema_path, "r") as f:
        lines = f.readlines()

    selected_lines = []
    ranges = line_ranges.split(",")

    for range_spec in ranges:
        range_spec = range_spec.strip()
        if "-" in range_spec:
            start, end = map(int, range_spec.split("-"))
            # Convert to 0-based indexing
            selected_lines.extend(lines[start - 1 : end])
        else:
            # Single line
            line_num = int(range_spec)
            selected_lines.append(lines[line_num - 1])

    return "".join(selected_lines)

"""Type definitions and data models for code generation."""

from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class FieldInfo(BaseModel):
    """Information about a field for template rendering."""

    name: str
    python_type: str
    json_schema_extra: Optional[Dict[str, Any]] = None


class MethodInfo(BaseModel):
    """Information about a method for template rendering."""

    name: str
    return_type: str
    expr: Optional[str] = None
    fn: Optional[str] = None


class TypeInfo(BaseModel):
    """Information about a type for template rendering."""

    name: str
    base_classes: List[str]
    fields: List[FieldInfo]
    methods: List[MethodInfo] = []
    static_methods: List[MethodInfo] = []  # NEW: for @static_method directive
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

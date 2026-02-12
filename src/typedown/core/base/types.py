from typing import TypeVar, Generic, Annotated
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

T = TypeVar("T")

class ReferenceMeta:
    """
    Metadata for Ref type to store the target type(s).
    Supports both single type (str) and polymorphic types (tuple of str).
    """
    def __init__(self, target_type):
        if isinstance(target_type, tuple):
            self.target_types = target_type
            self.target_type = target_type[0] if target_type else None  # Primary type for backwards compatibility
        elif isinstance(target_type, str):
            self.target_types = (target_type,)
            self.target_type = target_type
        else:
            raise TypeError(f"ReferenceMeta target_type must be str or tuple, got {type(target_type)}")

    def __repr__(self):
        if len(self.target_types) > 1:
            return f"ReferenceMeta(targets={self.target_types})"
        return f"ReferenceMeta(target={self.target_type})"
    
    def matches(self, class_name: str) -> bool:
        """Check if a class name matches any of the allowed target types (for polymorphic support)."""
        return class_name in self.target_types

class _RefType(str):
    """
    Runtime representation of a Reference.
    It functions exactly like a string at runtime for Pydantic.
    """
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler):
        # Validate as a string
        return core_schema.str_schema()

class Ref:
    """
    Ref type factory.
    Usage: field: Ref["User"]
    """
    def __class_getitem__(cls, target_type):
        # We use Annotated to attach metadata for the compiler
        # Support both single type and multiple types (polymorphic reference)
        if isinstance(target_type, tuple):
            # Polymorphic reference: Ref["User", "Admin"]
            return Annotated[str, ReferenceMeta(target_type)]
        elif isinstance(target_type, str):
            # Single type reference: Ref["User"]
            return Annotated[str, ReferenceMeta(target_type)]
        else:
            raise TypeError(f"Ref type argument must be a string or tuple of strings, got {type(target_type)}")



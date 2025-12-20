from typing import TypeVar, Generic, Annotated
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

T = TypeVar("T")

class ReferenceMeta:
    """Metadata for Ref type to store the target type string."""
    def __init__(self, target_type: str):
        self.target_type = target_type

    def __repr__(self):
        return f"ReferenceMeta(target={self.target_type})"

class _RefType(str):
    """
    Runtime representation of a Reference.
    It functions exactly like a string at runtime for Pydantic.
    """
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler):
        # Validate as a string
        return core_schema.str_schema()

def Ref(target_type: str) -> type:
    """
    Factory to create a Ref type.
    Usage: field: Ref["User"]
    """
    # We use Annotated to attach metadata for the compiler
    return Annotated[str, ReferenceMeta(target_type)]

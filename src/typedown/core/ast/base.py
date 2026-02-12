from typing import Optional, Protocol, runtime_checkable
from pydantic import BaseModel

class SourceLocation(BaseModel):
    """Describes the location of an element in the source file."""
    file_path: str
    line_start: int
    line_end: int
    col_start: int = 0
    col_end: int = 0

@runtime_checkable
class HashableNode(Protocol):
    @property
    def content_hash(self) -> str:
        ...

class Node(BaseModel):
    id: Optional[str] = None
    location: Optional[SourceLocation] = None

    @property
    def content_hash(self) -> str:
        """Returns the SHA-256 hash of the node's content."""
        raise NotImplementedError("Subclasses must implement content_hash if they are hashable.")

from typing import Optional, Protocol, runtime_checkable
from pydantic import BaseModel
import hashlib

class SourceLocation(BaseModel):
    """描述一个元素在源文件中的位置"""
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
        """返回节点内容的 SHA-256 哈希值"""
        raise NotImplementedError("Subclasses must implement content_hash if they are hashable.")

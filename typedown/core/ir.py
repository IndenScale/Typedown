from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field

# --- Base Nodes ---

class SourceLocation(BaseModel):
    file_path: str
    line_start: int
    line_end: int

class Node(BaseModel):
    id: Optional[str] = None
    location: Optional[SourceLocation] = None

# --- Semantic Nodes ---

class ModelDef(Node):
    """
    Represents a `model` block (Python/Pydantic code).
    """
    code: str

class EntityDef(Node):
    """
    Represents an `entity:Type` block.
    """
    id: str
    type_name: str
    data: Dict[str, Any]

class SpecDef(Node):
    """
    Represents a `spec` block (Python/Pytest code).
    """
    name: str # extracted from function name or block info
    code: str
    data: Dict[str, Any] = Field(default_factory=dict) # Metadata for the spec

class Reference(Node):
    """
    Represents [[Target]] inline reference.
    """
    target: str

class ConfigDef(Node):
    """
    Represents a `config:python` block (Arbitrary Python code for context injection).
    """
    code: str

class Document(Node):
    """
    Represents a parsed file.
    """
    path: Path
    configs: List[ConfigDef] = Field(default_factory=list)
    models: List[ModelDef] = Field(default_factory=list)
    entities: List[EntityDef] = Field(default_factory=list)
    specs: List[SpecDef] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    headers: List[Dict[str, Any]] = Field(default_factory=list) # [{'title': str, 'level': int, 'line': int}]
    raw_content: str = ""

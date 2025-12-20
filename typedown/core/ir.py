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

class ImportStmt(Node):
    """
    Represents an import from `config:python` or `import:` block (future).
    e.g. `from @lib.math import MathConfig`
    """
    source: str # "@lib.math"
    names: List[str] # ["MathConfig"]
    alias: Optional[str] = None

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

class Document(Node):
    """
    Represents a parsed file.
    """
    path: Path
    imports: List[ImportStmt] = Field(default_factory=list)
    models: List[ModelDef] = Field(default_factory=list)
    entities: List[EntityDef] = Field(default_factory=list)
    specs: List[SpecDef] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    raw_content: str = ""

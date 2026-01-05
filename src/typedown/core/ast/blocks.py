from typing import Dict, Optional, Any, Union, List
from pydantic import Field
import hashlib
import json
from .base import Node, SourceLocation
from ..base.identifiers import Identifier, AnyIdentifier
from pydantic import model_validator

class Reference(Node):  # Inherit from Node to get location? No, Reference in document.py was BaseModel.
    # But blocks.py Node has id/location.
    # original Reference had target, location, identifier...
    # Let's keep it as BaseModel from original but it's better if it's consistent.
    # Let's stick to original definition for safety.
    """
    AST 节点：表示 Typedown 文本中的 [[query]] 引用
    """
    target: str         # 原始查询字符串
    # location is in Node if we inherit, but let's redefine to match original exact structure first, 
    # OR better: make it inherit Node since Node has location.
    # Original Reference: target, location, identifier, resolved_entity_id, resolved_value
    location: SourceLocation
    
    identifier: Optional[AnyIdentifier] = None
    resolved_entity_id: Optional[str] = None
    resolved_value: Optional[Any] = None

    @model_validator(mode='after')
    def parse_identifier_if_needed(self):
        if self.identifier is None:
            base_id = self.target.split('.')[0] if '.' in self.target else self.target
            self.identifier = Identifier.parse(base_id)
        return self

class EntityRef(Node):
    """描述对其他 Entity 的引用关系 (former / derived_from)"""
    target_query: str

class ModelBlock(Node):
    """
    AST Node: Represents a `model` block (Python/Pydantic code).
    Syntax: ```model:ModelID
    """
    code: str

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.code.encode("utf-8")).hexdigest()

class EntityBlock(Node):
    """
    AST 节点：表示 Typedown 中的一个 entity 代码块。
    ```entity:Type
    ...
    ```
    """
    # 基础元数据 (id is inherited from Node)
    class_name: str # e.g., "User", "models.rpg.Character"
    
    # 原始数据 (YAML/JSON 解析后)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    # 解析后的完整数据 (Desugared/Merged)
    resolved_data: Dict[str, Any] = Field(default_factory=dict)
    
    # L2: Slug (Logical ID) - Explicitly defined in body as `id: ...`
    slug: Optional[str] = None

    # L3: UUID - Explicitly defined in body as `uuid: ...`
    uuid: Optional[str] = None

    # Evolution Semantics
    former_ids: List[str] = Field(default_factory=list)  # from `former`
    derived_from_id: Optional[str] = None  # from `derived_from`
    
    # Internal Analysis
    references: List[Reference] = Field(default_factory=list)

    @property
    def data(self) -> Dict[str, Any]:
        """Legacy alias for resolved_data."""
        return self.resolved_data

    @property
    def content_hash(self) -> str:
        # Use raw_data for hashing as resolved_data depends on external factors
        # Sort keys to ensure deterministic hash
        content = json.dumps(self.raw_data, sort_keys=True, ensure_ascii=False)
        # Optimization from TODOS: class_name + Handle/ID + Canonical YAML
        canonical = f"{self.class_name}:{self.id}:{content}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

class SpecBlock(Node):
    """
    AST Node: Represents a `spec` block (Python/Pytest code).
    """
    name: str
    code: str
    target: Optional[str] = None
    description: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    severity: Union[str, Dict[str, str]] = "warning"
    
    data: Dict[str, Any] = Field(default_factory=dict)
    
    # Internal Analysis
    references: List[Reference] = Field(default_factory=list)

    @property
    def content_hash(self) -> str:
        # Spec hash depends on name, code, target and params
        params_str = json.dumps(self.params, sort_keys=True, ensure_ascii=False)
        canonical = f"{self.name}:{self.target}:{params_str}:{self.code}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

class ConfigBlock(Node):
    """
    AST Node: Represents a `config` block.
    """
    code: str

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.code.encode("utf-8")).hexdigest()

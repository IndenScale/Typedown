from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field

class SourceLocation(BaseModel):
    """描述一个元素在源文件中的位置"""
    file_path: str
    line_start: int
    line_end: int
    col_start: int = 0
    col_end: int = 0

class EntityRef(BaseModel):
    """描述对其他 Entity 的引用关系 (former / derived_from)"""
    target_query: str
    location: Optional[SourceLocation] = None

class EntityBlock(BaseModel):
    """
    AST 节点：表示 Markdown 中的一个 entity 代码块。
    ```entity:Type
    ...
    ```
    """
    # 基础元数据
    id: str  # 必须全局唯一
    class_name: str # e.g., "User", "models.rpg.Character"
    
    # 原始数据 (YAML/JSON 解析后)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    # 解析后的完整数据 (Desugared/Merged)
    resolved_data: Dict[str, Any] = Field(default_factory=dict)
    
    # 关系 (尚未解析为具体对象，仅存储引用字符串)
    former_ref: Optional[EntityRef] = None
    derived_from_ref: Optional[EntityRef] = None
    
    # 定位信息
    location: SourceLocation

class SpecBlock(BaseModel):
    """
    AST Node: Represents a `spec:Rule` block in Markdown.
    """
    id: str
    description: Optional[str] = None
    target: str # Selector string, e.g. "entity:Monster"
    check: str  # Python function path, e.g. "specs.combat.check_min_hp"
    params: Dict[str, Any] = Field(default_factory=dict)
    severity: Union[str, Dict[str, str]] = "warning" # "error" or map {"default": "warning", "release": "error"}
    
    location: SourceLocation

class Reference(BaseModel):
    """
    AST 节点：表示 Markdown 文本中的 [[query]] 引用
    """
    raw_text: str       # "[[User.name]]"
    query_string: str   # "User.name"
    location: SourceLocation
    
    # 解析状态 (Compiler pass 填充)
    resolved_entity_id: Optional[str] = None
    resolved_value: Optional[Any] = None # 如果是属性引用，存储解析后的值

class Document(BaseModel):
    """
    AST 节点：表示一个 Markdown 文件
    """
    path: Path
    
    # 文件内容的哈希值，用于增量解析
    content_hash: str
    
    # 配置上下文 (从 config.td 继承合并后的结果)
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # 提取出的结构化节点
    entities: List[EntityBlock] = Field(default_factory=list)
    specs: List[SpecBlock] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    
    # 提取出的可执行 Python 脚本
    python_scripts: List[str] = Field(default_factory=list)
    model_scripts: List[str] = Field(default_factory=list) # model blocks with pre-injected imports
    
    # 原始 Markdown 内容 (用于后续回填/物化)
    raw_content: str

class Project(BaseModel):
    """
    AST 根节点：表示整个 Typedown 项目
    """
    root_dir: Path
    documents: Dict[str, Document] = Field(default_factory=dict) # path -> Document
    
    # 全局符号表 (Symbol Table)
    # entity_id -> EntityBlock
    symbol_table: Dict[str, EntityBlock] = Field(default_factory=dict)
    
    # 规则表 (Spec Table)
    # spec_id -> SpecBlock
    spec_table: Dict[str, SpecBlock] = Field(default_factory=dict) # <--- Added
    
    # 依赖图 (用于拓扑排序)
    # entity_id -> List[dependency_entity_ids]
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict)

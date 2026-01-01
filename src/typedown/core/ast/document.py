from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseModel, Field
from .base import SourceLocation
from .blocks import EntityBlock, ModelBlock, ConfigBlock, SpecBlock, Reference
from ..base.identifiers import Identifier, AnyIdentifier

import hashlib

class Document(BaseModel):
    """
    AST 节点：表示一个 Typedown 文件
    """
    path: Path
    
    # Front Matter 元数据
    tags: List[str] = Field(default_factory=list)
    scripts: Dict[str, str] = Field(default_factory=dict)
    
    # 配置上下文 (从 config.td 继承合并后的结果)
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # 提取出的结构化节点
    configs: List[ConfigBlock] = Field(default_factory=list)
    models: List[ModelBlock] = Field(default_factory=list)
    entities: List[EntityBlock] = Field(default_factory=list)
    specs: List[SpecBlock] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    
    # 辅助信息
    headers: List[Dict[str, Any]] = Field(default_factory=list)
    
    # 原始 Typedown 内容 (用于后续回填/物化)
    raw_content: str = ""

    @property
    def content_hash(self) -> str:
        """
        聚合所有 Block 的哈希值，生成文档级别的 Merkle 哈希。
        """
        # 收集所有块的哈希
        block_hashes = []
        for block in self.configs:
            block_hashes.append(block.content_hash)
        for block in self.models:
            block_hashes.append(block.content_hash)
        for block in self.entities:
            block_hashes.append(block.content_hash)
        for block in self.specs:
            block_hashes.append(block.content_hash)
        
        # 排序以确保确定性
        block_hashes.sort()
        combined = "".join(block_hashes)
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

class Resource(BaseModel):
    """
    AST 节点：表示外部资源文件 (非 Typedown 文档)
    用于支持 [[assets/image.png]] 形式的引用访问。
    """
    id: str             # 资源的逻辑 ID (通常是相对于 Project Root 的路径, 如 "data/table.csv")
    path: Path          # 文件绝对路径
    content: bytes      # 文件字节流内容
    content_hash: str   # 内容哈希

class Project(BaseModel):
    """
    AST 根节点：表示整个 Typedown 项目
    """
    root_dir: Path
    documents: Dict[str, Document] = Field(default_factory=dict) # path -> Document
    resources: Dict[str, Resource] = Field(default_factory=dict) # path(id) -> Resource
    
    # 项目级别脚本 (从 typedown.yaml 加载)
    scripts: Dict[str, str] = Field(default_factory=dict)
    
    # 全局符号表 (Symbol Table)
    # entity_id -> EntityBlock or Resource
    symbol_table: Dict[str, Any] = Field(default_factory=dict)
    
    # 规则表 (Spec Table)
    # spec_id -> SpecBlock
    spec_table: Dict[str, SpecBlock] = Field(default_factory=dict)
    
    # 依赖图 (用于拓扑排序)
    # entity_id -> List[dependency_entity_ids]
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict)

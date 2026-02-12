from typing import Dict, List, Any
from pathlib import Path
from pydantic import BaseModel, Field
from .blocks import EntityBlock, ModelBlock, ConfigBlock, SpecBlock, Reference

import hashlib

class Document(BaseModel):
    """
    AST Node: Represents a Typedown file.
    """
    path: Path
    
    # Front Matter metadata
    tags: List[str] = Field(default_factory=list)
    
    # Configuration context (inherited and merged from config.td)
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Extracted structured nodes
    configs: List[ConfigBlock] = Field(default_factory=list)
    models: List[ModelBlock] = Field(default_factory=list)
    entities: List[EntityBlock] = Field(default_factory=list)
    specs: List[SpecBlock] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    
    # Auxiliary information
    headers: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Raw Typedown content (for later backfill/materialization)
    raw_content: str = ""

    @property
    def content_hash(self) -> str:
        """
        Aggregates hash values of all blocks to generate a document-level Merkle hash.
        """
        # Collect hashes from all blocks
        block_hashes = []
        for block in self.configs:
            block_hashes.append(block.content_hash)
        for block in self.models:
            block_hashes.append(block.content_hash)
        for block in self.entities:
            block_hashes.append(block.content_hash)
        for block in self.specs:
            block_hashes.append(block.content_hash)
        
        # Sort to ensure deterministic ordering
        block_hashes.sort()
        combined = "".join(block_hashes)
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

class Resource(BaseModel):
    """
    AST Node: Represents an external resource file (non-Typedown document).
    Used to support references like [[assets/image.png]].
    """
    id: str             # Logical ID of the resource (usually relative to Project Root, e.g., "data/table.csv")
    path: Path          # Absolute file path
    content: bytes      # Raw file content
    content_hash: str   # Content hash

class Project(BaseModel):
    """
    AST Root Node: Represents the entire Typedown project.
    """
    root_dir: Path
    documents: Dict[str, Document] = Field(default_factory=dict)  # path -> Document
    resources: Dict[str, Resource] = Field(default_factory=dict)  # path(id) -> Resource
    
    # Global Symbol Table
    # entity_id -> EntityBlock or Resource
    symbol_table: Dict[str, Any] = Field(default_factory=dict)
    
    # Spec Table
    # spec_id -> SpecBlock
    spec_table: Dict[str, SpecBlock] = Field(default_factory=dict)
    
    # Dependency Graph (for topological sorting)
    # entity_id -> List[dependency_entity_ids]
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict)

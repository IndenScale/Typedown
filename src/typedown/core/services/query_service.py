"""
QueryService: Query interface for the symbol table.

Responsibilities:
- GraphQL-like query execution
- Entity lookup by type
- Entity lookup by ID
"""

from pathlib import Path
from typing import Any, List, Optional, Dict, TYPE_CHECKING
from rich.console import Console

from typedown.core.ast import EntityBlock
from typedown.core.base.utils import AttributeWrapper
from typedown.core.base.symbol_table import SymbolTable
from typedown.core.analysis.query import QueryEngine

if TYPE_CHECKING:
    from typedown.core.compiler import Compiler


class QueryService:
    """
    Service for querying the compiled symbol table.
    
    Provides:
    - GraphQL-like query interface
    - Entity type filtering
    - Entity ID lookup
    """
    
    def __init__(
        self,
        project_root: Path,
        symbol_table: SymbolTable,
        console: Optional[Console] = None
    ):
        self.project_root = project_root
        self.symbol_table = symbol_table
        self.console = console
    
    def query(
        self,
        query_string: str,
        context_path: Optional[Path] = None
    ) -> Any:
        """
        GraphQL-like query interface for the symbol table.
        
        Example:
            query("User.profile.email")
            query("projects.*.name")
        
        Args:
            query_string: Query string
            context_path: Optional context path for relative queries
            
        Returns:
            Query results (List[Any])
        """
        ctx = context_path or self.project_root
        
        engine = QueryEngine(self.symbol_table, root_dir=self.project_root)
        return engine.resolve_query(query_string, context_path=ctx)
    
    def get_entities_by_type(self, type_name: str) -> List[Any]:
        """
        Get all entities matching a specific type.
        
        Args:
            type_name: Entity type name to filter by
            
        Returns:
            List of entities wrapped in AttributeWrapper
        """
        results = []
        for node in self.symbol_table.values():
            if isinstance(node, EntityBlock) and node.class_name == type_name:
                results.append(AttributeWrapper(node.resolved_data))
        return results
    
    def get_entity(self, entity_id: str) -> Optional[Any]:
        """
        Get a single entity by its ID.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Entity wrapped in AttributeWrapper, or None if not found
        """
        entity = self.symbol_table.get(entity_id)
        if entity:
            return AttributeWrapper(entity.resolved_data)
        return None
    
    def get_entity_raw(self, entity_id: str) -> Optional[EntityBlock]:
        """
        Get the raw EntityBlock by ID (for internal use).
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            EntityBlock or None if not found
        """
        entity = self.symbol_table.get(entity_id)
        if isinstance(entity, EntityBlock):
            return entity
        return None
    
    def list_entity_types(self) -> List[str]:
        """
        Get a list of all entity types in the symbol table.
        
        Returns:
            List of unique type names
        """
        types = set()
        for node in self.symbol_table.values():
            if isinstance(node, EntityBlock):
                types.add(node.class_name)
        return sorted(list(types))
    
    def list_entities(self) -> Dict[str, str]:
        """
        Get a mapping of entity IDs to their types.
        
        Returns:
            Dictionary of entity_id -> type_name
        """
        entities = {}
        for node in self.symbol_table.values():
            if isinstance(node, EntityBlock):
                entities[node.id] = node.class_name
        return entities

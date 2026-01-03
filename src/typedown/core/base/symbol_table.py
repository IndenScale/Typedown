from pathlib import Path
from typing import Dict, Optional, List, Any, Union
import hashlib

from typedown.core.base.identifiers import Identifier, Handle, Slug, Hash, UUID

# Use Any for Node to avoid circular imports, or import strictly if possible.
# Ideally this should be imported from typedown.core.base assuming Node is there.
# For now we handle the dependency carefully.

class SymbolTable:
    """
    A Path-Aware Symbol Table supporting Typedown's Triple Resolution strategy.
    
    Structure:
    1. Global Index: Flat map of Logical IDs (globally unique).
    2. Scoped Index: Map of Directory Path -> { Handle Name -> Node }.
    3. Hash Index: Map of Content Hash (sha256:...) -> Node.
    
    This allows O(Depth) resolution for Handles (lexical scoping) and O(1) for Logical IDs and Hashes.
    """
    
    def __init__(self):
        # Global Registry: "infra/db-prod" -> Node
        self._global_index: Dict[str, Any] = {}
        
        # Scoped Registry: Path("/app/src") -> { "db": Node }
        self._scoped_index: Dict[Path, Dict[str, Any]] = {}

        # Hash Registry: "sha256:..." -> Node (L0 Cache)
        self._hash_index: Dict[str, Any] = {}

    def add(self, node: Any, scope_path: Path):
        """
        Register a node into the symbol table.
        
        Args:
            node: The AST Node (EntityBlock, ModelBlock, etc.)
            scope_path: The file path where this node is defined. 
                        The scope is associated with the file's PARENT directory.
        """
        # 1. Register by Hash (L0)
        if hasattr(node, "content_hash"):
             # For property access, we might need to handle NotImplementedError
             try:
                 h = node.content_hash
                 if h:
                     self._hash_index[f"sha256:{h}"] = node
             except (NotImplementedError, AttributeError):
                 pass

        if not hasattr(node, "id") or not node.id:
            return

        # 2. Register in Global Index (L1/L2)
        self._global_index[node.id] = node
        
        # 3. Register Explicit L2 (Slug) & L3 (UUID) identifiers from AST
        # These are always global.
        if hasattr(node, "slug") and node.slug:
            self._global_index[node.slug] = node
            
        if hasattr(node, "uuid") and node.uuid:
            self._global_index[node.uuid] = node
            
        if hasattr(node, "former_ids") and node.former_ids:
            for former in node.former_ids:
                 # Register alias pointing to the *current* node (new state)
                 self._global_index[former] = node
            
        # ALWAYS register as a handle in the local scope.
        if scope_path.suffix and not scope_path.is_dir():
            scope_dir = scope_path.parent
        else:
            scope_dir = scope_path
        
        scope_dir = scope_dir.resolve()
        
        if scope_dir not in self._scoped_index:
            self._scoped_index[scope_dir] = {}
        
        self._scoped_index[scope_dir][node.id] = node

    def resolve(self, query: str, context_path: Optional[Path] = None) -> Optional[Any]:
        """
        Execute Triple Resolution using Identifier System.
        Delegates to specific resolution methods based on Identifier type.
        """
        identifier = Identifier.parse(query)
        
        if isinstance(identifier, Hash):
            return self.resolve_hash(identifier.hash_value)
        elif isinstance(identifier, Handle):
            return self.resolve_handle(identifier.name, context_path)
        elif isinstance(identifier, Slug):
            return self.resolve_slug(identifier.path)
        elif isinstance(identifier, UUID):
            return self.resolve_uuid(identifier.uuid_value)
        return None

    def resolve_hash(self, hash_value: str) -> Optional[Any]:
        """L0: Resolve by content hash."""
        # Check standard sha256 prefix key
        key = f"sha256:{hash_value}"
        if key in self._hash_index:
            return self._hash_index[key]
        return None

    def resolve_handle(self, name: str, context_path: Optional[Path] = None) -> Optional[Any]:
        """L1: Resolve local handle by walking up the scope chain."""
        if not context_path:
            # Fallback to global index if no context provided (legacy behavior support)
            return self._global_index.get(name)

        if context_path.suffix and not context_path.is_dir():
            current_dir = context_path.parent
        else:
            current_dir = context_path
        
        current_dir = current_dir.resolve()
        
        # Scoped Lookup: Current Dir -> Parents
        search_paths = [current_dir] + list(current_dir.parents)
        
        for scope in search_paths:
            if scope in self._scoped_index:
                if name in self._scoped_index[scope]:
                    return self._scoped_index[scope][name]
        
        # Fallback to global index (handles can refer to slugs if unique)
        return self._global_index.get(name)

    def resolve_slug(self, slug_path: str) -> Optional[Any]:
        """L2: Resolve by global logical path (Slug ID)."""
        return self._global_index.get(slug_path)

    def resolve_uuid(self, uuid_value: str) -> Optional[Any]:
        """L3: Resolve by global UUID."""
        # UUIDs are stored in the global index
        return self._global_index.get(uuid_value)

    # --- Dict Compatibility Layer ---
    
    def __contains__(self, key: str) -> bool:
        # Default behavior for dict-like usage: check hash, then global
        if key.startswith("sha256:"):
            return key in self._hash_index
        return key in self._global_index

    def __getitem__(self, key: str) -> Any:
        res = self.resolve(key)
        if res is None:
            raise KeyError(key)
        return res

    def get(self, key: str, default=None) -> Any:
        res = self.resolve(key)
        return res if res is not None else default

    def values(self):
        """Returns all unique nodes across all indexes."""
        # Use dict to track unique nodes by id (since nodes are not hashable)
        seen = {}
        
        # Add global nodes
        for node_id, node in self._global_index.items():
            seen[id(node)] = node  # Use Python object id for uniqueness
        
        # Add scoped nodes
        for scope_dict in self._scoped_index.values():
            for node in scope_dict.values():
                seen[id(node)] = node
        
        return list(seen.values())

    def items(self):
        """Returns all global items. (Scoped items are omitted as they lack unique global keys)"""
        return self._global_index.items()

    def keys(self):
        """Returns all global keys."""
        return self._global_index.keys()

    def __iter__(self):
        return iter(self._global_index)

    def get_all_globals(self) -> Dict[str, Any]:
        return self._global_index
        
    def get_scope_handles(self, path: Path) -> Dict[str, Any]:
        """Debug helper to see what's visible in a specific exact directory."""
        return self._scoped_index.get(path, {})

    def clear(self):
        self._global_index.clear()
        self._scoped_index.clear()
        self._hash_index.clear()

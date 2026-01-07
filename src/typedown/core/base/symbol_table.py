from pathlib import Path
from typing import Dict, Optional, List, Any, Union
import hashlib
import json
import tempfile
import os

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

        # Type Index: "User" -> [Node, Node]
        self._type_index: Dict[str, List[Any]] = {}
        
        # DuckDB Connection Cache
        self._db_conn = None

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
            
        # ALWAYS register as a handle in the local scope.
        # If scope_path is a file, we register in that file's PARENT directory scope.
        # This implements Directory-Level scoping (config.td + sibling visibility).
        
        # Determine scope target (Directory)
        # We assume it's a file if it has a suffix or if it's a known file on disk.
        if scope_path.suffix or (scope_path.exists() and not scope_path.is_dir()):
            scope_target = scope_path.parent.resolve()
        else:
            scope_target = scope_path.resolve()
        
        if scope_target not in self._scoped_index:
            self._scoped_index[scope_target] = {}
        
        self._scoped_index[scope_target][node.id] = node

        # 4. Register Type Index (Optimization for SQL/Collections)
        if hasattr(node, "class_name") and node.class_name:
            if node.class_name not in self._type_index:
                self._type_index[node.class_name] = []
            self._type_index[node.class_name].append(node)

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

        # Ensure we are working with an absolute, normalized path
        # Note: .resolve() can be flaky on non-existent paths on some systems, 
        # but .absolute() + .normalize() (via resolve) is standard for CWD-relative.
        current_path = context_path.resolve()
        
        # If the context is a file, the local scope IS its parent directory.
        # We start searching from the parent directory to find sibling files or config.td exports.
        if current_path.suffix or (current_path.exists() and not current_path.is_dir()):
            start_dir = current_path.parent
        else:
            start_dir = current_path
            
        # Scoped Lookup: Start Dir -> Parents
        # list(start_dir.parents) returns [parent, grandparent, ..., root]
        search_paths = [start_dir] + list(start_dir.parents)
        
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

    def get_by_type(self, type_name: str) -> List[Any]:
        return self._type_index.get(type_name, [])

    def get_duckdb_connection(self):
        """
        Returns a DB connection (DuckDB preferred, SQLite fallback) with all types registered as tables.
        Lazily initialized.
        """
        if self._db_conn:
            return self._db_conn

        # 1. Try DuckDB
        try:
            import duckdb
            self._db_conn = duckdb.connect(":memory:")
            self._populate_duckdb(self._db_conn)
            return self._db_conn
        except ImportError:
            pass

        # 2. Fallback to SQLite
        try:
            import sqlite3
            self._db_conn = sqlite3.connect(":memory:")
            # Enable dictionary cursor for compatibility
            self._db_conn.row_factory = sqlite3.Row
            self._populate_sqlite(self._db_conn)
            return self._db_conn
        except ImportError:
            raise ImportError("DuckDB or SQLite is required for SQL features.")

    def _populate_duckdb(self, conn):
        for type_name, nodes in self._type_index.items():
            # Flatten to list of dicts
            data = []
            for node in nodes:
                row = getattr(node, "resolved_data", None) or getattr(node, "raw_data", {})
                row_copy = row.copy() if row else {}
                if hasattr(node, "id"):
                    row_copy["_id"] = node.id
                    if "id" not in row_copy:
                        row_copy["id"] = node.id
                data.append(row_copy)
            
            if not data:
                continue

            # Table name cleanup: "models.User" -> "User"
            table_name = type_name.split(".")[-1]
            
            # Use JSON file for robust schema inference
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp:
                json.dump(data, tmp, default=str)
                tmp_path = tmp.name
            
            try:
                conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_json_auto('{tmp_path}')")
            except Exception:
                # Ignore table creation errors (e.g. invalid data)
                pass
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    def _populate_sqlite(self, conn):
        for type_name, nodes in self._type_index.items():
            data = []
            keys = set()
            
            for node in nodes:
                row = getattr(node, "resolved_data", None) or getattr(node, "raw_data", {})
                row_copy = row.copy() if row else {}
                if hasattr(node, "id"):
                    row_copy["_id"] = node.id
                    # Helper: Expose as 'id' if not conflicting with payload
                    if "id" not in row_copy:
                        row_copy["id"] = node.id
                
                # Flatten complex types for SQLite
                for k, v in row_copy.items():
                    if isinstance(v, (dict, list)):
                        row_copy[k] = json.dumps(v)
                    keys.add(k)
                
                data.append(row_copy)
            
            if not data:
                continue

            table_name = type_name.split(".")[-1]
            
            # Create Table
            # SQLite needs explicit schema usually, but we can infer dynamic columns
            # For simplicity, we create TEXT columns for everything if inference is hard
            # Or we can just use the keys found
            
            # Sanitize keys
            safe_keys = [k for k in keys if k.isidentifier()]
            if not safe_keys:
                continue
                
            cols_def = ", ".join([f"{k} TEXT" for k in safe_keys]) # Default to TEXT for simplicity
            
            # Improved Inference: Check first non-null value for type?
            # For now, strict typing in SQLite is loose, so TEXT/NUMERIC is fine.
            # But let's try to be a bit better:
            
            cols_defs = []
            for k in safe_keys:
                # Check first value
                sample = next((d.get(k) for d in data if d.get(k) is not None), None)
                if isinstance(sample, int):
                    col_type = "INTEGER"
                elif isinstance(sample, float):
                    col_type = "REAL"
                else:
                    col_type = "TEXT"
                cols_defs.append(f"{k} {col_type}")
            
            create_stmt = f"CREATE TABLE {table_name} ({', '.join(cols_defs)})"
            conn.execute(create_stmt)
            
            # Insert Data
            placeholders = ", ".join(["?" for _ in safe_keys])
            insert_stmt = f"INSERT INTO {table_name} ({', '.join(safe_keys)}) VALUES ({placeholders})"
            
            rows_to_insert = []
            for row in data:
                vals = [row.get(k) for k in safe_keys]
                rows_to_insert.append(vals)
                
            conn.executemany(insert_stmt, rows_to_insert)

    def get_scope_handles(self, path: Path) -> Dict[str, Any]:
        """Debug helper to see what's visible in a specific exact directory."""
        return self._scoped_index.get(path, {})

    def clear(self):
        self._global_index.clear()
        self._scoped_index.clear()
        self._hash_index.clear()

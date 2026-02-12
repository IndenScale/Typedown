import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from rich.console import Console

try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

from typedown.core.ast import EntityBlock
from typedown.core.base.errors import ReferenceError, QueryError
from typedown.core.base.identifiers import Identifier, Handle, Hash, UUID

console = Console()
REF_PATTERN = re.compile(r'\[\[(.*?)\]\]')


class QueryEngine:
    """
    QueryEngine with instance-based design.
    
    Provides query execution against symbol tables with support for:
    - SQL execution (via DuckDB/SQLite)
    - Data evaluation with reference resolution
    - String interpolation with [[reference]] syntax
    - Symbol path resolution with property access
    
    Usage:
        engine = QueryEngine(symbol_table, root_dir)
        result = engine.resolve_query("User.alice")
        data = engine.evaluate_data(raw_data)
    """
    
    def __init__(
        self,
        symbol_table: Any,
        root_dir: Optional[Path] = None,
        resources: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize QueryEngine with dependencies.
        
        Args:
            symbol_table: The SymbolTable or dict for lookups
            root_dir: Project root directory for asset resolution
            resources: Resource map for asset lookups
        """
        self.symbol_table = symbol_table
        self.root_dir = root_dir
        self.resources = resources or {}
        self._cache: Dict[str, Any] = {}
    
    def execute_sql(self, query: str, parameters: Dict[str, Any] = {}) -> List[Any]:
        """
        Execute SQL query against the symbol table's database connection.
        
        Args:
            query: SQL query string
            parameters: Query parameters for binding
            
        Returns:
            List of result rows as dictionaries
            
        Raises:
            QueryError: If execution fails or no connection available
        """
        # We assume symbol_table has get_duckdb_connection
        if not hasattr(self.symbol_table, "get_duckdb_connection"):
             raise QueryError("SymbolTable does not support SQL execution.")
        
        try:
            con = self.symbol_table.get_duckdb_connection()
            
            # Check if it's DuckDB or SQLite
            is_sqlite = False
            try:
                import sqlite3
                if isinstance(con, sqlite3.Connection):
                    is_sqlite = True
            except ImportError:
                pass

            if is_sqlite:
                cursor = con.cursor()
                cursor.execute(query, parameters)
                # sqlite3.Row factory handles dict-like access
                rows = cursor.fetchall()
                # Convert to pure dicts and auto-parse JSON strings
                results = []
                for row in rows:
                    row_dict = dict(row)
                    for key, value in row_dict.items():
                        if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                            try:
                                row_dict[key] = json.loads(value)
                            except json.JSONDecodeError:
                                pass  # Keep original string if not valid JSON
                    results.append(row_dict)
                return results
            else:
                # DuckDB
                con.execute(query, parameters)
                
                if not con.description:
                    return []
                
                columns = [desc[0] for desc in con.description]
                rows = con.fetchall()
                
                results = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    # Auto-parse JSON strings returned by DuckDB
                    for key, value in row_dict.items():
                        if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                            try:
                                row_dict[key] = json.loads(value)
                            except json.JSONDecodeError:
                                pass  # Keep original string if not valid JSON
                    results.append(row_dict)
                
                return results
            
        except Exception as e:
            raise QueryError(f"SQL Execution failed: {e}")

    def evaluate_data(self, data: Any, context_path: Optional[Path] = None) -> Any:
        """
        Recursively traverse `data` and replace string references [[query]] 
        with their resolved values from the symbol table.
        
        Args:
            data: Data structure to evaluate (dict, list, str, or primitive)
            context_path: File path where the data originates (for context resolution)
            
        Returns:
            Evaluated data with references resolved
        """
        if isinstance(data, dict):
            return {k: self.evaluate_data(v, context_path=context_path) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.evaluate_data(v, context_path=context_path) for v in data]
        elif isinstance(data, str):
            return self.resolve_string(data, context_path=context_path)
        else:
            return data

    def resolve_string(self, text: str, context_path: Optional[Path] = None) -> Any:
        """
        Resolve references within a string.
        
        Supports:
        - Exact reference: "[[query]]" -> resolved value
        - Interpolation: "Hello [[name]]!" -> "Hello Alice!"
        
        Args:
            text: String potentially containing references
            context_path: Context path for resolution
            
        Returns:
            Resolved value (or original string if no references)
            
        Raises:
            ReferenceError: If exact reference not found
        """
        # Check if the whole string is a reference
        match = REF_PATTERN.fullmatch(text)
        if match:
            query = match.group(1)
            results = self.resolve_query(query, context_path=context_path)
            if not results:
                 raise ReferenceError(f"Reference not found: '{query}'")
            return results[0]
            
        # Mixed content support: "Level [[level]]"
        if REF_PATTERN.search(text):
            def replacer(m):
                try:
                    results = self.resolve_query(m.group(1), context_path=context_path)
                    val = results[0] if results else None
                    return str(val) if val is not None else m.group(0)
                except (QueryError, ReferenceError):
                    return m.group(0)
            
            return REF_PATTERN.sub(replacer, text)
            
        return text

    def resolve_query(
        self, 
        query: str, 
        scope: Optional[Path] = None,
        context_path: Optional[Path] = None
    ) -> List[Any]:
        """
        Executes a query against the symbol table and resources.
        
        Args:
            query: The query string (e.g., "User.alice", "assets/image.png", "sha256:...").
            scope: Optional directory limit for resolution.
            context_path: The file path where the query originates (for Triple Resolution).

        Returns:
            List of matching blocks/objects. If ambiguous, returns multiple.
        """
        results = []

        # 1. Try Standard Symbol Resolution (Exact Match ID or Property Access)
        try:
            val = self._resolve_symbol_path(query, context_path=context_path)
            if val is not None:
                # Check Scope
                # Assuming val is an EntityBlock or similar Node with location
                if scope and hasattr(val, 'location') and val.location:
                   if self._is_in_scope(val.location.file_path, scope):
                       results.append(val)
                else:
                    # If it's a scalar (no location) or no scope provided, include it
                    results.append(val)
        except (ReferenceError, QueryError):
            pass

        # 2. Try Resource/Asset Resolution (Path based)
        # Treat query as a relative path
        # Normalize path separators
        target_path_str = query.replace("\\", "/")
        
        # Check explicit resources (pre-loaded)
        if target_path_str in self.resources:
            res = self.resources[target_path_str]
             # Check Scope
            if scope:
                 # Resource ID is relative path, so check if it starts with scope relative to root?
                 # Or check absolute path
                 if self._is_in_scope(str(res.path), scope):
                     results.append(res)
            else:
                results.append(res)
        
        # 3. Dynamic File Match
        if self.root_dir and not results:
             # Try resolving as file path relative to project root
             candidate_path = self.root_dir / target_path_str
             if candidate_path.is_file():
                 # Create a transient Resource-like object
                 # This avoids eager scanning
                 from collections import namedtuple
                 # Minimal compatible interface with what Linker/Compiler might produce
                 TransientResource = namedtuple("TransientResource", ["path", "id"])
                 res = TransientResource(path=candidate_path, id=target_path_str)
                 
                 # Check Scope
                 if scope:
                      if self._is_in_scope(str(candidate_path), scope):
                          results.append(res)
                 else:
                      results.append(res)

        return results

    def _is_in_scope(self, file_path: str, scope: Path) -> bool:
        """Check if file_path is within the scope directory."""
        try:
            p = Path(file_path).resolve()
            s = scope.resolve()
            return p.is_relative_to(s)
        except ValueError:
            return False

    def _resolve_symbol_path(self, query: str, context_path: Optional[Path] = None) -> Any:
        """
        Resolve symbol path using Identifier separation.
        Steps:
        1. Identify Root Identifier (Handle/Slug/Hash/UUID).
        2. Resolve Root Object.
        3. Traverse Property Path (if any).
        """
        # Split into Root and Property Path
        # We need to be careful: "users/alice.name" -> Root: "users/alice", Prop: "name"
        # "alice.name" -> Root: "alice", Prop: "name"
        # "sha256:... .meta" -> Root: "sha256:...", Prop: "meta"
        
        # Heuristic: 
        # If it contains "sha256:", the colon is part of ID. Properties follow after space? No, usually not property access on hash.
        # But let's support "ID.property".
        
        # NOTE: Slug IDs can contain slashes, but NOT dots (usually).
        # Handles generally don't contain dots.
        # So splitting by first dot is a reasonable default, BUT:
        # What if ID is "v1.2/config"? (Slug with dot).
        # Our Identifier parser is context-free.
        
        # Strategy:
        # Try to parse the WHOLE string as identifier first?
        # If "User.name" is parsed as Handle("User.name"), we fail to find it, then what?
        # This is the "Dot ambiguity" problem.
        # Simplest approach: Assume "." starts property path unless part of known pattern.
        
        # Heuristic: 
        # If it contains "sha256:", the colon is part of ID. Properties follow after space? No, usually not property access on hash.
        # But let's support "ID.property".
        
        # NOTE: Slug IDs can contain slashes, but NOT dots (usually).
        # Handles generally don't contain dots.
        # So splitting by first dot is a reasonable default.
        
        if "." in query:
            parts = query.split(".")
            root_query = parts[0]
            property_path = parts[1:]
        else:
            root_query = query
            property_path = []

        # 1. Parse Root Identifier
        identifier = Identifier.parse(root_query)
        
        # 2. Resolve Root Object
        current_data = self._resolve_by_identifier(identifier, context_path)

        # 3. Traverse Properties
        if not property_path:
            return current_data
            
        return self._traverse_property_path(current_data, property_path, query)

    def _resolve_by_identifier(self, identifier: Identifier, context_path: Optional[Path] = None) -> Any:
        """Dispatch resolution based on Identifier type."""
        # Use SymbolTable's specific methods if available (Preferred)
        if hasattr(self.symbol_table, "resolve_handle"):
            if isinstance(identifier, Hash):
                val = self.symbol_table.resolve_hash(identifier.hash_value)
                if val is None: raise ReferenceError(f"Hash not found: {identifier}")
                return val
            elif isinstance(identifier, Handle):
                val = self.symbol_table.resolve_handle(identifier.name, context_path)
                if val is None: raise ReferenceError(f"L1 Match failed: Handle '{identifier}' not found in current context.")
                return val
            elif isinstance(identifier, UUID):
                val = self.symbol_table.resolve_uuid(identifier.uuid_value)
                if val is None: raise ReferenceError(f"UUID not found: {identifier}")
                return val

        # Fallback to generic resolve or dict lookup (Legacy/Testing)
        if hasattr(self.symbol_table, "resolve"):
             val = self.symbol_table.resolve(str(identifier), context_path)
             if val is None: raise ReferenceError(f"Identifier not found: {identifier}")
             return val
             
        # Dict fallback
        key = str(identifier)
        if key not in self.symbol_table:
             raise ReferenceError(f"Identifier {identifier} not found in symbol table.")
        return self.symbol_table[key]
    
    

    def _traverse_property_path(self, current_data: Any, property_path: List[str], original_query: str) -> Any:
        """
        遍历属性访问路径，支持：
        - 属性访问：User.name
        - 数组索引：items[0]
        - 通配符：User.*（返回整个对象）
        """
        # Unwrap Variable Handles at the start
        if hasattr(current_data, "type") and getattr(current_data, "type") == "variable" and hasattr(current_data, "value"):
            current_data = current_data.value
        
        # Regex for "name" or "name[index]"
        PART_PATTERN = re.compile(r"^(\w+)(?:\[(\d+)\])?$")

        for i, part in enumerate(property_path):
            # Final '*' logic: Return current data (serialized)
            if part == "*":
                if i == len(property_path) - 1:  # It IS the last part
                    resolved_data = getattr(current_data, "resolved_data", None)
                    raw_data = getattr(current_data, "raw_data", None)
                    
                    if resolved_data:
                         return resolved_data
                    if raw_data:
                         return raw_data
                    return current_data
                else:
                    raise QueryError(f"Invalid query: '*' must be the final segment in '{original_query}'")

            # Parse name and index
            match = PART_PATTERN.match(part)
            if not match:
                raise QueryError(f"Invalid path segment: '{part}' in '{original_query}'")
            
            name, index = match.groups()
            
            # Resolve Name
            found = False
            # Check .data transparency for Nodes at first step or subsequent
            if i == 0:
                 resolved_data = getattr(current_data, "resolved_data", None)
                 raw_data = getattr(current_data, "raw_data", None)
                 
                 if isinstance(resolved_data, dict) and name in resolved_data:
                      current_data = resolved_data[name]
                      found = True
                 elif isinstance(raw_data, dict) and name in raw_data:
                      current_data = raw_data[name]
                      found = True
            
            if not found:
                if isinstance(current_data, dict) and name in current_data:
                    current_data = current_data[name]
                    found = True
                elif hasattr(current_data, name):
                    current_data = getattr(current_data, name)
                    found = True
            
            if not found:
                 raise QueryError(f"Segment '{name}' not found in '{original_query}'")

            # Resolve Index if present
            if index is not None:
                idx = int(index)
                if isinstance(current_data, list):
                    if idx < len(current_data):
                        current_data = current_data[idx]
                    else:
                        raise QueryError(f"Index {idx} out of range in segment '{part}'")
                else:
                    raise QueryError(f"Segment '{name}' is not a list, cannot index in '{original_query}'")

        return current_data
    
    def clear_cache(self) -> None:
        """Clear internal cache."""
        self._cache.clear()

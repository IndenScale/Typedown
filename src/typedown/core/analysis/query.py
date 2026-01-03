import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from rich.console import Console
from typedown.core.ast import EntityBlock
from typedown.core.base.errors import ReferenceError, QueryError
from typedown.core.base.identifiers import Identifier, Handle, Slug, Hash, UUID

console = Console()
REF_PATTERN = re.compile(r'\[\[(.*?)\]\]')

class QueryError(Exception):
    pass

class QueryEngine:
    @staticmethod
    def evaluate_data(data: Any, symbol_table: Any, context_path: Optional[Path] = None) -> Any:
        """
        Recursively traverse `data` and replace string references [[query]] 
        with their resolved values from the symbol table.
        """
        if isinstance(data, dict):
            return {k: QueryEngine.evaluate_data(v, symbol_table, context_path=context_path) for k, v in data.items()}
        elif isinstance(data, list):
            return [QueryEngine.evaluate_data(v, symbol_table, context_path=context_path) for v in data]
        elif isinstance(data, str):
            return QueryEngine.resolve_string(data, symbol_table, context_path=context_path)
        else:
            return data

    @staticmethod
    def resolve_string(text: str, symbol_table: Any, context_path: Optional[Path] = None) -> Any:
        # Check if the whole string is a reference
        match = REF_PATTERN.fullmatch(text)
        if match:
            query = match.group(1)
            results = QueryEngine.resolve_query(query, symbol_table, context_path=context_path)
            if not results:
                 raise ReferenceError(f"Reference not found: '{query}'")
            return results[0]
            
        # Mixed content support: "Level [[level]]"
        if REF_PATTERN.search(text):
            def replacer(m):
                try:
                    results = QueryEngine.resolve_query(m.group(1), symbol_table, context_path=context_path)
                    val = results[0] if results else None
                    return str(val) if val is not None else m.group(0)
                except (QueryError, ReferenceError):
                    return m.group(0)
            
            return REF_PATTERN.sub(replacer, text)
            
        return text

    @staticmethod
    def resolve_query(query: str, symbol_table: Any, resources: Dict[str, Any] = {}, root_dir: Optional[Path] = None, scope: Optional[Path] = None, context_path: Optional[Path] = None) -> List[Any]:
        """
        Executes a query against the symbol table and resources.
        
        Args:
            query: The query string (e.g., "User.alice", "assets/image.png", "sha256:...").
            symbol_table: The SymbolTable object or dictionary.
            resources: The global resources map (id -> Resource).
            root_dir: The project root directory (needed for asset resolution).
            scope: Optional directory limit for resolution.
            context_path: The file path where the query originates (for Triple Resolution).

        Returns:
            List of matching blocks/objects. If ambiguous, returns multiple.
        """
        results = []

        # 1. Try Standard Symbol Resolution (Exact Match ID or Property Access)
        try:
            val = QueryEngine._resolve_symbol_path(query, symbol_table, context_path=context_path)
            if val is not None:
                # Check Scope
                # Assuming val is an EntityBlock or similar Node with location
                if scope and hasattr(val, 'location') and val.location:
                   if QueryEngine._is_in_scope(val.location.file_path, scope):
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
        if target_path_str in resources:
            res = resources[target_path_str]
             # Check Scope
            if scope:
                 # Resource ID is relative path, so check if it starts with scope relative to root?
                 # Or check absolute path
                 if QueryEngine._is_in_scope(str(res.path), scope):
                     results.append(res)
            else:
                results.append(res)
        
        # 3. Dynamic File Match
        if root_dir and not results:
             # Try resolving as file path relative to project root
             candidate_path = root_dir / target_path_str
             if candidate_path.is_file():
                 # Create a transient Resource-like object
                 # This avoids eager scanning
                 from collections import namedtuple
                 # Minimal compatible interface with what Linker/Compiler might produce
                 TransientResource = namedtuple("TransientResource", ["path", "id"])
                 res = TransientResource(path=candidate_path, id=target_path_str)
                 
                 # Check Scope
                 if scope:
                      if QueryEngine._is_in_scope(str(candidate_path), scope):
                          results.append(res)
                 else:
                      results.append(res)

        return results

    @staticmethod
    def _is_in_scope(file_path: str, scope: Path) -> bool:
        try:
            p = Path(file_path).resolve()
            s = scope.resolve()
            return p.is_relative_to(s)
        except ValueError:
            return False

    @staticmethod
    def _resolve_symbol_path(query: str, symbol_table: Any, context_path: Optional[Path] = None) -> Any:
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
        current_data = QueryEngine._resolve_by_identifier(identifier, symbol_table, context_path)

        # 3. Traverse Properties
        if not property_path:
            return current_data
            
        return QueryEngine._traverse_property_path(current_data, property_path, query)

    @staticmethod
    def _resolve_by_identifier(identifier: Identifier, symbol_table: Any, context_path: Optional[Path] = None) -> Any:
        """Dispatch resolution based on Identifier type."""
        # Use SymbolTable's specific methods if available (Preferred)
        if hasattr(symbol_table, "resolve_handle"):
            if isinstance(identifier, Hash):
                val = symbol_table.resolve_hash(identifier.hash_value)
                if val is None: raise ReferenceError(f"Hash not found: {identifier}")
                return val
            elif isinstance(identifier, Handle):
                val = symbol_table.resolve_handle(identifier.name, context_path)
                if val is None: raise ReferenceError(f"L2 Fuzzy Match failed: Handle '{identifier}' not found in current context.")
                return val
            elif isinstance(identifier, Slug):
                val = symbol_table.resolve_slug(identifier.path)
                if val is None: raise ReferenceError(f"L1 Exact Match failed: System ID '{identifier}' not found in global index.")
                return val
            elif isinstance(identifier, UUID):
                val = symbol_table.resolve_uuid(identifier.uuid_value)
                if val is None: raise ReferenceError(f"UUID not found: {identifier}")
                return val

        # Fallback to generic resolve or dict lookup (Legacy/Testing)
        if hasattr(symbol_table, "resolve"):
             val = symbol_table.resolve(str(identifier), context_path)
             if val is None: raise ReferenceError(f"Identifier not found: {identifier}")
             return val
             
        # Dict fallback
        key = str(identifier)
        if key not in symbol_table:
             raise ReferenceError(f"Identifier {identifier} not found in symbol table.")
        return symbol_table[key]
    
    

    @staticmethod
    def _traverse_property_path(current_data: Any, property_path: List[str], original_query: str) -> Any:
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
                    if hasattr(current_data, "resolved_data") and current_data.resolved_data:
                         return current_data.resolved_data
                    if hasattr(current_data, "raw_data"):
                         return current_data.raw_data
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
                 if hasattr(current_data, "resolved_data") and isinstance(current_data.resolved_data, dict) and name in current_data.resolved_data:
                      current_data = current_data.resolved_data[name]
                      found = True
                 elif hasattr(current_data, "raw_data") and isinstance(current_data.raw_data, dict) and name in current_data.raw_data:
                      current_data = current_data.raw_data[name]
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


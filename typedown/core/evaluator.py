import re
from typing import Any, Dict, List, Optional
from rich.console import Console
from typedown.core.ast import EntityBlock

console = Console()
REF_PATTERN = re.compile(r'\[\[(.*?)\]\]')

class EvaluationError(Exception):
    pass

class Evaluator:
    @staticmethod
    def evaluate_data(data: Any, symbol_table: Dict[str, Any]) -> Any:
        """
        Recursively traverse `data` and replace string references [[query]] 
        with their resolved values from the symbol table.
        """
        if isinstance(data, dict):
            return {k: Evaluator.evaluate_data(v, symbol_table) for k, v in data.items()}
        elif isinstance(data, list):
            return [Evaluator.evaluate_data(v, symbol_table) for v in data]
        elif isinstance(data, str):
            return Evaluator.resolve_string(data, symbol_table)
        else:
            return data

    @staticmethod
    def resolve_string(text: str, symbol_table: Dict[str, Any]) -> Any:
        # Check if the whole string is a reference
        # We only support direct replacement if the string is EXACTLY [[...]]
        # If it's "Hello [[User]]", we might support interpolation later, 
        # but for now let's focus on direct value injection or string interpolation.
        
        # Strategy:
        # 1. Exact match "[[query]]" -> returns the object (Dict, List, Int, etc.)
        # 2. Partial match "Hello [[query]]" -> returns a string with substitution.
        
        match = REF_PATTERN.fullmatch(text)
        if match:
            query = match.group(1)
            return Evaluator.resolve_query(query, symbol_table)
            
        # Mixed content support: "Level [[level]]"
        # We use re.sub with a callback
        if REF_PATTERN.search(text):
            def replacer(m):
                try:
                    val = Evaluator.resolve_query(m.group(1), symbol_table)
                    return str(val)
                except EvaluationError:
                    return m.group(0) # Keep as is if failed? Or raise?
            
            return REF_PATTERN.sub(replacer, text)
            
        return text

    @staticmethod
    def resolve_query(query: str, symbol_table: Dict[str, Any]) -> Any:
        # 1. Single segment: ID string
        if "." not in query:
            if query not in symbol_table:
                raise EvaluationError(f"Reference to unknown ID: '{query}'")
            return query

        parts = query.split(".")
        root_id = parts[0]
        if root_id not in symbol_table:
            raise EvaluationError(f"Reference to unknown ID: '{root_id}'")

        current_data = symbol_table[root_id]
        
        # Regex for "name" or "name[index]"
        PART_PATTERN = re.compile(r"^(\w+)(?:\[(\d+)\])?$")

        for i, part in enumerate(parts[1:]):
            # Final '*' logic: Return current data (serialized)
            if part == "*":
                if i == len(parts) - 2: # It IS the last part
                    if hasattr(current_data, "data"):
                        return getattr(current_data, "data")
                    return current_data
                else:
                    raise EvaluationError(f"Invalid query: '*' must be the final segment in '{query}'")

            # Parse name and index
            match = PART_PATTERN.match(part)
            if not match:
                raise EvaluationError(f"Invalid path segment: '{part}' in '{query}'")
            
            name, index = match.groups()
            
            # Resolve Name
            found = False
            # Check .data transparency for Nodes at first step or subsequent
            if i == 0 and hasattr(current_data, "data") and isinstance(getattr(current_data, "data"), dict):
                if name in getattr(current_data, "data"):
                    current_data = getattr(current_data, "data")[name]
                    found = True
            
            if not found:
                if isinstance(current_data, dict) and name in current_data:
                    current_data = current_data[name]
                    found = True
                elif hasattr(current_data, name):
                    current_data = getattr(current_data, name)
                    found = True
            
            if not found:
                 raise EvaluationError(f"Segment '{name}' not found in '{query}'")

            # Resolve Index if present
            if index is not None:
                idx = int(index)
                if isinstance(current_data, list):
                    if idx < len(current_data):
                        current_data = current_data[idx]
                    else:
                        raise EvaluationError(f"Index {idx} out of range in segment '{part}'")
                else:
                    raise EvaluationError(f"Segment '{name}' is not a list, cannot index in '{query}'")

        return current_data

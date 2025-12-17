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
    def evaluate_data(data: Any, symbol_table: Dict[str, EntityBlock]) -> Any:
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
    def resolve_string(text: str, symbol_table: Dict[str, EntityBlock]) -> Any:
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
                val = Evaluator.resolve_query(m.group(1), symbol_table)
                return str(val) # Force string conversion for interpolation
            
            return REF_PATTERN.sub(replacer, text)
            
        return text

    @staticmethod
    def resolve_query(query: str, symbol_table: Dict[str, EntityBlock]) -> Any:
        """
        Resolve 'EntityID.attr.subattr' to a value.
        """
        parts = query.split('.')
        entity_id = parts[0]
        
        if entity_id not in symbol_table:
            # Fallback for now: return original string or raise?
            # Raising is better to catch errors.
            raise EvaluationError(f"Reference to unknown Entity ID: '{entity_id}'")
            
        entity = symbol_table[entity_id]
        
        # Determine the root data to look into.
        # It must be the resolved_data.
        # BUT: Dependency order guarantees parents are processed.
        # But if 'EntityID' refers to a sibling or unrelated entity?
        # If they are not in dependency chain, they might NOT be resolved yet if they come later in topological sort.
        # However, if I reference something, surely I depend on it?
        # Ah, the current Dependency Graph ONLY tracks `former/derived_from`.
        # It does NOT track `[[references]]` in the body.
        
        # CRITICAL ARCHITECTURAL ISSUE:
        # Implicit dependencies via `[[ ]]` are not in the DAG. 
        # So we might reference an entity that hasn't been materialized yet.
        
        # Logic:
        # Check if entity.resolved_data is populated.
        # If not, we have a problem.
        # For now, let's check `resolved_data`.
        
        current_data = entity.resolved_data
        if not current_data:
             # If referenced entity is not resolved, we can't get attributes.
             # This means we need to update the Resolver to include body references in the DAG.
             # But for P0, let's assume the user manually ordered things correctly or valid references are mostly upstream.
             # Or, maybe we can access `raw_data` if `resolved_data` is missing? 
             # No, `raw_data` is incomplete (missing parent data).
             
             # Let's check if the referenced entity IS the current entity (self-reference).
             pass

        # Traverse attributes
        for part in parts[1:]:
            if isinstance(current_data, dict) and part in current_data:
                current_data = current_data[part]
            else:
                raise EvaluationError(f"Attribute '{part}' not found in '{query}' (stopped at '{current_data}')")
                
        return current_data

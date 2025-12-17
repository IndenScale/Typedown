from typing import Any, Dict, List
import copy

class Merger:
    """
    Handles merging of Entity data (Parent + Child).
    """
    
    @staticmethod
    def merge(parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        Strategy:
        - Scalar: Child overwrites Parent.
        - List: Child overwrites Parent (No append).
        - Dict: Recursive merge.
        """
        # Start with a deep copy of parent to avoid mutating it
        result = copy.deepcopy(parent)
        
        for key, child_value in child.items():
            if key in result:
                parent_value = result[key]
                
                # Recursive Merge for Dicts
                if isinstance(parent_value, dict) and isinstance(child_value, dict):
                    result[key] = Merger.merge(parent_value, child_value)
                else:
                    # For Scalars and Lists: Overwrite
                    result[key] = child_value
            else:
                # New key in child
                result[key] = child_value
                
        return result

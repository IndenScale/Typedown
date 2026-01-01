from typing import Any, List, Dict

class Desugarer:
    """
    Handles Typedown-specific YAML desugaring.
    Converts YAML artifacts like [['ref']] back to "[[ref]]" and flattens nested lists.
    """
    
    @staticmethod
    def desugar(data: Any) -> Any:
        """
        Recursively desugar data.
        """
        if isinstance(data, dict):
            return {k: Desugarer.desugar(v) for k, v in data.items()}
        elif isinstance(data, list):
            # 1. Check for the specific pattern [['target']]
            if len(data) == 1 and isinstance(data[0], list) and len(data[0]) == 1 and isinstance(data[0][0], str):
                # Potential legacy double-bracket YAML artifact
                # Convert back to Typedown query string
                return f"[[{data[0][0]}]]"
            
            # 2. Check for single bracket string wrap: ['target'] -> "[[target]]" ?
            # Actually, standard YAML for [[target]] is [['target']].
            # For [target], it's ['target'].
            # Typedown spec says [[ ]] is the reference.
            
            # 3. Flatenning: If we have a list of lists that were intended as refs:
            # [ [[a]], [[b]] ] -> [['a'], ['b']] after YAML parse.
            # We want to flatten this to ["[[a]]", "[[b]]"]
            
            processed_list = []
            for item in data:
                desugared_item = Desugarer.desugar(item)
                # If the item was a list that got desugared into a string starting with [[, 
                # or if it's just a regular list, we decide whether to flatten.
                # The rule is: Typedown prohibits nested lists in Entity Body.
                # So if we see a list, we might want to flatten it IF it contains references.
                processed_list.append(desugared_item)
            
            return processed_list
        else:
            return data

    @staticmethod
    def flatten_refs(data: Any) -> Any:
        # Placeholder for more complex flattening logic if needed
        return Desugarer.desugar(data)

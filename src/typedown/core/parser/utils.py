from typing import Tuple, Dict, Optional, List

class InfoStringParser:
    @staticmethod
    def parse(info_str: str) -> Tuple[str, Optional[str], Dict[str, str]]:
        """
        Parses a Typedown code block info string.
        Format: type:arg key=value "quoted key"="quoted value"
        
        Returns:
            (block_type, block_arg, meta_dict)
        """
        if not info_str:
            return "", None, {}

        # Basic split, respecting quotes would be better but simple split is current baseline
        # TODO: strict tokenizer if needed
        parts = info_str.split()
        if not parts:
            return "", None, {}

        header = parts[0]
        meta_parts = parts[1:]
        
        block_type = header
        block_arg = None
        
        if ':' in header:
            block_type, block_arg = header.split(':', 1)
            
        meta = {}
        for p in meta_parts:
            if '=' in p:
                k, v = p.split('=', 1)
                meta[k] = v.strip('"\'')
            # Handle strict arg parsing if arg wasn't in colon syntax
            elif not block_arg and '=' not in p:
                # e.g. ```entity User``` -> type=entity, arg=User
                # But this depends on caller logic. 
                # For this parser, we just return parts.
                pass
                
        return block_type, block_arg, meta

    @staticmethod
    def parse_strict(info_str: str) -> Tuple[str, Optional[str]]:
        """
        Strict parsing for: ```type:arg
        Returns (type, arg) or (None, None) if invalid.
        """
        if not info_str:
            return None, None
            
        parts = info_str.split()
        if not parts:
            return None, None
            
        header = parts[0]
        if ':' not in header:
            return None, None
            
        return header.split(':', 1)

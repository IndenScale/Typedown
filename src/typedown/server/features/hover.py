from lsprotocol.types import (
    TEXT_DOCUMENT_HOVER,
    HoverParams,
    Hover,
)
from typedown.server.application import server, TypedownLanguageServer
from pathlib import Path
import re

@server.feature(TEXT_DOCUMENT_HOVER)
def hover(ls: TypedownLanguageServer, params: HoverParams):
    if not ls.compiler: return None
    
    # We need to read the document line to find what is under cursor
    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    if params.position.line >= len(lines): return None
    line = lines[params.position.line]
    col = params.position.character
    
    # 1. Check for [[ID]]
    for match in re.finditer(r'\[\[(.*?)\]\]', line):
        if match.start() <= col <= match.end():
            ref_id = match.group(1).strip()
            if ref_id in ls.compiler.symbol_table:
                entity = ls.compiler.symbol_table[ref_id]
                
                # Basic Info
                sys_id = getattr(entity, 'id', 'Unknown')
                type_name = getattr(entity, 'class_name', 'Unknown')
                md = f"**Handle**: `{ref_id}`\n**System ID**: `{sys_id}`\n**Type**: `{type_name}`\n\n"
                
                # Fetch Content Preview if possible
                loc = getattr(entity, 'location', None)
                if loc and loc.file_path:
                    try:
                        p = Path(entity.location.file_path)
                        if p.exists():
                            # We want to read lines around the definition
                            # Mistune location is 1-based
                            start = entity.location.line_start
                            end = entity.location.line_end
                            
                            # Read file content safely
                            content_lines = p.read_text(encoding="utf-8").splitlines()
                            
                            # Extract snippet (up to 8 lines)
                            snippet_lines = content_lines[start:min(end, start + 8)]
                            snippet = "\n".join(snippet_lines)
                            
                            md += f"```yaml\n{snippet}\n```"
                            if end - start > 8:
                                md += "\n*(...)*"
                    except Exception:
                        pass

                return Hover(contents=md)
    
    # 2. Check for Entity Block Header: ```entity Type: ID
    match = re.match(r'^(\s*)```entity\s+([\w\.\-]+)(?:\s*:\s*([\w\.\-]+))?', line)
    if match:
        # Check if cursor is on Type name (Group 2)
        type_start = match.start(2)
        type_end = match.end(2)
        if type_start <= col <= type_end:
            type_name = match.group(2)            
            # Lookup in compiler's model registry
            if hasattr(ls.compiler, 'model_registry') and type_name in ls.compiler.model_registry:
                model_cls = ls.compiler.model_registry[type_name]
                
                md = f"**Type**: `{type_name}`\n\n"
                md += f"**Python**: `{model_cls.__name__}`\n\n"
                
                if model_cls.__doc__:
                    md += f"{model_cls.__doc__}\n\n"
                
                md += "**Fields**:\n"
                for name, field in model_cls.model_fields.items():
                    req = " (Required)" if field.is_required() else ""
                    md += f"- `{name}`{req}\n"
                
                return Hover(contents=md)
            else:
                 return Hover(contents=f"**Type**: `{type_name}` (Not Found in Registry)")

    return None

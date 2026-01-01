from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    CompletionParams,
)
from typedown.server.application import server, TypedownLanguageServer
from pathlib import Path
import re

@server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=["["]))
def completions(ls: TypedownLanguageServer, params: CompletionParams):
    if not ls.compiler: return []
    
    # Read context to determine if we are in a wiki link
    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    if params.position.line >= len(lines): return []
    
    line = lines[params.position.line]
    col = params.position.character
    prefix = line[:col]
    
    items = []
    
    # CASE 1: [[class:
    class_match = re.search(r'\[\[class:([\w\.\-_]*)$', prefix)
    if class_match:
        # Show all known Models
        if hasattr(ls.compiler, 'model_registry'):
            for model_name, model_cls in ls.compiler.model_registry.items():
                items.append(CompletionItem(
                    label=model_name,
                    kind=CompletionItemKind.Class,
                    detail="Model",
                    documentation=model_cls.__doc__ or f"Pydantic Model {model_name}",
                    insert_text=f"{model_name}]]",
                    sort_text=f"00_{model_name}"
                ))
        return CompletionList(is_incomplete=False, items=items)

    # CASE 2: [[entity:
    entity_match = re.search(r'\[\[entity:([\w\.\-_]*)$', prefix)
    if entity_match:
        # Show all known Entities
        for entity_id, entity in ls.compiler.symbol_table.items():
            items.append(CompletionItem(
                label=entity_id,
                kind=CompletionItemKind.Class,
                detail=entity.class_name or "Entity",
                documentation=f"Defined in {Path(entity.location.file_path).name}",
                insert_text=f"{entity_id}]]",
                sort_text=f"00_{entity_id}"
            ))
        return CompletionList(is_incomplete=False, items=items)

    # CASE 3: [[header:
    header_match = re.search(r'\[\[header:([\w\.\-_ ]*)$', prefix)
    if header_match:
        # Show all known Headers from all docs
        for doc_path, doc in ls.compiler.documents.items():
            for hdr in doc.headers:
                title = hdr.get('title', 'Untitled')
                level = hdr.get('level', 1)
                # Format: Title (File.md)
                items.append(CompletionItem(
                    label=title,
                    kind=CompletionItemKind.Reference, # Use Reference icon for headers
                    detail=f"H{level} in {doc_path.name}",
                    insert_text=f"{title}]]",
                    sort_text=f"00_{title}"
                ))
        return CompletionList(is_incomplete=False, items=items)

    # CASE 4: Generic [[
    match = re.search(r'\[\[([^:\]]*)$', prefix)
    
    if match:
        # 1. Snippets
        for snip in ["entity:", "class:", "header:"]:
            items.append(CompletionItem(
                label=snip,
                kind=CompletionItemKind.Keyword,
                detail=f"Scope to {snip[:-1]}",
                insert_text=snip,
                sort_text=f"00_{snip}_snippet", 
                command={'title': 'Trigger Completion', 'command': 'editor.action.triggerSuggest'}
            ))

        # 2. Entities (Icon: Class/Struct)
        for entity_id, entity in ls.compiler.symbol_table.items():
            items.append(CompletionItem(
                label=entity_id,
                kind=CompletionItemKind.Struct, # Distinct from Class
                detail=entity.class_name or "Entity",
                documentation=f"Defined in {Path(entity.location.file_path).name}",
                insert_text=f"{entity_id}]]",
                sort_text=f"10_{entity_id}"
            ))
            
        # 3. Files (Icon: File)
        for doc_path in ls.compiler.documents.keys():
            path_name = doc_path.name
            items.append(CompletionItem(
                label=path_name,
                kind=CompletionItemKind.File,
                detail="File",
                insert_text=f"{path_name}]]",
                sort_text=f"20_{path_name}"
            ))

        return CompletionList(is_incomplete=False, items=items)
        
    return []

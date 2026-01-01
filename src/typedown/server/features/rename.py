from lsprotocol.types import (
    TEXT_DOCUMENT_RENAME,
    RenameParams,
    TextEdit,
    WorkspaceEdit,
    Range,
    Position,
)
from typedown.server.application import server, TypedownLanguageServer
from typing import Dict, List
import re

@server.feature(TEXT_DOCUMENT_RENAME)
def rename(ls: TypedownLanguageServer, params: RenameParams):
    if not ls.compiler or not ls.compiler.dependency_graph: return None

    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    if params.position.line >= len(lines): return None
    line = lines[params.position.line]
    col = params.position.character
    
    # Identify target ID
    target_id = None
    
    # 1. From Wiki Link [[ID]]
    for match in re.finditer(r'\[\[(.*?)\]\]', line):
        if match.start() <= col <= match.end():
            target_id = match.group(1).strip()
            break
            
    # 2. From Word
    if not target_id:
         start = col
         while start > 0 and (line[start-1].isalnum() or line[start-1] in "._-"):
            start -= 1
         end = col
         while end < len(line) and (line[end].isalnum() or line[end] in "._-"):
            end += 1
         candidate = line[start:end]
         if candidate in ls.compiler.symbol_table:
             target_id = candidate

    if not target_id:
        return None
        
    changes: Dict[str, List[TextEdit]] = {}
    
    # Strategy: Scan ALL documents for [[TargetID]] and update them.
    for doc_path, doc_obj in ls.compiler.documents.items():
        uri = doc_path.as_uri()
        doc_edits = []
        
        try:
            content = doc_obj.raw_content 
            if not content: continue
            
            pattern = f"[[{target_id}]]"
            
            # Iterate all matches
            for match in re.finditer(re.escape(pattern), content):
                start_idx = match.start()
                
                # The ID starts after "[[" (2 chars)
                id_start_idx = start_idx + 2
                
                # Convert absolute index to Line/Col
                pre_content = content[:id_start_idx]
                line_num = pre_content.count('\n')
                last_newline = pre_content.rfind('\n')
                if last_newline == -1:
                    col_num = len(pre_content)
                else:
                    col_num = len(pre_content) - (last_newline + 1)
                
                doc_edits.append(TextEdit(
                    range=Range(
                        start=Position(line=line_num, character=col_num),
                        end=Position(line=line_num, character=col_num + len(target_id))
                    ),
                    new_text=params.new_name
                ))
            
        except Exception:
            continue

        if doc_edits:
            if uri not in changes: changes[uri] = []
            changes[uri].extend(doc_edits)

    return WorkspaceEdit(changes=changes)

from lsprotocol.types import (
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_REFERENCES,
    DefinitionParams,
    ReferenceParams,
    Location,
    LocationLink,
    Range,
    Position,
)
from typedown.server.application import server, TypedownLanguageServer
from pathlib import Path
import re
import inspect
from typedown.server.managers.diagnostics import uri_to_path

@server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: TypedownLanguageServer, params: DefinitionParams):
    with ls.lock:
        return _definition_impl(ls, params)

def _definition_impl(ls: TypedownLanguageServer, params: DefinitionParams):
    if not ls.compiler: 
        ls.show_message_log("Definition Request: Compiler not initialized.")
        return None

    uri = params.text_document.uri
    file_path = uri_to_path(uri)
    
    ls.show_message_log(f"Definition Request for: {file_path} at line {params.position.line}, col {params.position.character}")
    
    if file_path not in ls.compiler.documents:
        ls.show_message_log(f"Definition Request: File not found in compiler documents: {file_path}")
        return None
        
    doc = ls.compiler.documents[file_path]
    line = params.position.line
    col = params.position.character
    
    # 1. Check if on a Reference [[...]]
    target_ref = _find_reference_at_position(doc, line, col)
    if target_ref:
        ls.show_message_log(f"Definition Request: Found Reference '{target_ref.target}'")
        if target_ref.identifier:
            ref_id = str(target_ref.identifier)
            if ref_id in ls.compiler.symbol_table:
                 target_obj = ls.compiler.symbol_table[ref_id]
                 if hasattr(target_obj, 'location') and target_obj.location:
                     target_uri = Path(target_obj.location.file_path).as_uri()
                     # LSP Range is 0-indexed, AST is 1-indexed
                     # Go to Definition usually jumps to the start of the block
                     target_line = max(0, target_obj.location.line_start - 1)
                     ls.show_message_log(f"Definition Request: Jump to Entity '{ref_id}' at {target_uri}:{target_line}")
                     
                     # Refine Range: target_range is full block, target_selection_range is just the header
                     full_range = Range(
                        start=Position(line=target_line, character=0),
                        end=Position(line=max(0, target_obj.location.line_end), character=0)
                     )
                     selection_range = Range(
                        start=Position(line=target_line, character=0),
                        end=Position(line=target_line, character=100) # Select first line roughly
                     )
                     
                     return [LocationLink(
                        origin_selection_range=Range(
                            start=Position(line=line, character=target_ref.location.col_start),
                            end=Position(line=line, character=target_ref.location.col_end)
                        ),
                        target_uri=target_uri,
                        target_range=full_range,
                        target_selection_range=selection_range
                     )]
            else:
                ls.show_message_log(f"Definition Request: Symbol '{ref_id}' not found in Symbol Table.")
    else:
        ls.show_message_log("Definition Request: No Reference found at cursor.")

    # 2. Check if on Entity Header (Type or Handle)
    source_lines = doc.raw_content.splitlines()
    if line < len(source_lines):
        line_text = source_lines[line]
        # Regex for: ```entity Type: Handle
        match = re.match(r'^(\s*)```entity\s+([\w\.\-]+)(?:\s*:\s*([\w\.\-]+))?', line_text)
        
        if match:
            # Check col against Type (Group 2)
            type_start = match.start(2)
            type_end = match.end(2)
            
            if type_start <= col <= type_end:
                 # Go to Model Definition
                 type_name = match.group(2)
                 ls.show_message_log(f"Definition Request: Clicked on Type '{type_name}'")
                 if type_name in ls.compiler.symbol_table:
                      target_obj = ls.compiler.symbol_table[type_name]
                      if hasattr(target_obj, 'location') and target_obj.location:
                           target_uri = Path(target_obj.location.file_path).as_uri()
                           target_line = max(0, target_obj.location.line_start - 1)
                           ls.show_message_log(f"Definition Request: Jump to Model Block '{type_name}' at {target_uri}:{target_line}")
                           
                           full_range = Range(
                              start=Position(line=target_line, character=0),
                              end=Position(line=max(0, target_obj.location.line_end), character=0)
                           )
                           selection_range = Range(
                              start=Position(line=target_line, character=0),
                              end=Position(line=target_line, character=len(type_name) + 12) # ~ ```model:ID
                           )
                           
                           return [LocationLink(
                              origin_selection_range=Range(
                                  start=Position(line=line, character=type_start),
                                  end=Position(line=line, character=type_end)
                              ),
                              target_uri=target_uri,
                              target_range=full_range,
                              target_selection_range=selection_range
                           )]

                 if hasattr(ls.compiler, 'model_registry') and type_name in ls.compiler.model_registry:
                      model_cls = ls.compiler.model_registry[type_name]
                      try:
                        src_file = inspect.getsourcefile(model_cls)
                        if src_file:
                            src_lines, start_line = inspect.getsourcelines(model_cls)
                            target_range = Range(
                                start=Position(line=max(0, start_line - 1), character=0),
                                end=Position(line=max(0, start_line + len(src_lines)), character=0)
                            )
                            ls.show_message_log(f"Definition Request: Jump to Model '{type_name}' in python source.")
                            # Return LocationLink to enforce full string selection
                            return [LocationLink(
                                origin_selection_range=Range(
                                    start=Position(line=line, character=type_start),
                                    end=Position(line=line, character=type_end)
                                ),
                                target_uri=Path(src_file).as_uri(),
                                target_range=target_range,
                                target_selection_range=target_range
                            )]
                      except Exception as e:
                        ls.show_message_log(f"Definition Request: Error resolving model source: {e}")
                        pass

            # Check col against Handle (Group 3)
            # [Refactor] Self-Jump logic removed.
            # Clicking on the definition itself should do nothing (return None),
            # allowing the cursor to stay in place instead of risking a jump to stale AST locations.
            if match.group(3):
                handle_start = match.start(3)
                handle_end = match.end(3)
                if handle_start <= col <= handle_end:
                     target_id = match.group(3)
                     ls.show_message_log(f"Definition Request: Clicked on Handle '{target_id}' (Declaration). Returning None to keep cursor in place.")
                     return None
                     
    return None
                             
    return None

def _find_reference_at_position(doc, line: int, col: int):
    """Find the specific AST Reference node at the given position."""
    # Search all blocks that might contain references
    # references are stored in doc.references
    
    # AST is 1-indexed, LSP is 0-indexed
    candidates = [ref for ref in doc.references if ref.location.line_start == line + 1] 
    
    for ref in candidates:
        if ref.location.col_start <= col <= ref.location.col_end:
            return ref
    return None

@server.feature(TEXT_DOCUMENT_REFERENCES)
def references(ls: TypedownLanguageServer, params: ReferenceParams):
    if not ls.compiler or not ls.compiler.dependency_graph: return None

    uri = params.text_document.uri
    file_path = uri_to_path(uri)
    
    if file_path not in ls.compiler.documents:
        return None
    doc = ls.compiler.documents[file_path]
    line = params.position.line
    col = params.position.character

    target_id = None

    # 1. Check if on a Reference (Go to Definition -> Find References of THAT definition)
    # E.g. clicking on [[alice]] -> find all refs to alice
    target_ref = _find_reference_at_position(doc, line, col)
    if target_ref and target_ref.identifier:
        target_id = str(target_ref.identifier)

    # 2. Check if on Entity Header Handle (Find references TO this entity)
    # Re-use Regex check
    if not target_id:
        source_lines = doc.raw_content.splitlines()
        if line < len(source_lines):
            line_text = source_lines[line]
            match = re.match(r'^(\s*)```entity\s+([\w\.\-]+)(?:\s*:\s*([\w\.\-]+))?', line_text)
            if match and match.group(3):
                # Check if on Handle
                handle_start = match.start(3)
                handle_end = match.end(3)
                if handle_start <= col <= handle_end:
                    target_id = match.group(3)

    if target_id and target_id in ls.compiler.dependency_graph.reverse_adj:
        locations = []
        referencing_ids = ls.compiler.dependency_graph.reverse_adj[target_id]
        
        for ref_id in referencing_ids:
            if ref_id in ls.compiler.symbol_table:
                entity = ls.compiler.symbol_table[ref_id]
                if entity.location:
                    locations.append(Location(
                        uri=Path(entity.location.file_path).as_uri(),
                        range=Range(
                            start=Position(line=max(0, entity.location.line_start-1), character=0),
                            end=Position(line=max(0, entity.location.line_end), character=0)
                        )
                    ))
        return locations
        
    return []

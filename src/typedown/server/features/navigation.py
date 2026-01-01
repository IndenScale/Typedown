from lsprotocol.types import (
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_REFERENCES,
    DefinitionParams,
    ReferenceParams,
    Location,
    Range,
    Position,
)
from typedown.server.application import server, TypedownLanguageServer
from pathlib import Path
import re
import inspect

@server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: TypedownLanguageServer, params: DefinitionParams):
    if not ls.compiler: return None

    uri = params.text_document.uri
    file_path = Path(uri.replace("file://", "")) # Basic URI parse, improved later via uri_to_path
    
    # Use Compiler's AST state
    # We assume ls.compiler.documents is keyed by Path
    if file_path not in ls.compiler.documents:
        return None
        
    doc = ls.compiler.documents[file_path]
    line = params.position.line
    col = params.position.character
    
    # 1. Search in Entity Blocks for References
    for entity in doc.entities:
        # Check if cursor is inside this entity block
        # We need precise location mapping. 
        # entity.location usually spans the whole block.
        # But entity.references have their own locations.
        
        # Optimization: Check if cursor is roughly in block range first
        if not (entity.location.line_start <= line <= entity.location.line_end):
            continue
            
        for ref in entity.references:
            # Check if cursor is on this reference
            # Reference location: line_start, line_end, etc.
            # Assuming Reference location logic is accurate
            if ref.location and ref.location.line_start == line: # TODO: Multi-line refs?
                # AST doesn't strictly give column range currently for Refs?
                # We might need to assume or check text text.
                # If we lack columns, we fall back to regex on that line just to confirm bounds?
                # Or we trust the parser populated columns? 
                # Our current Parser mock didn't populate columns. 
                # Let's rely on "Reference contains target string".
                
                # Fallback / Refinement:
                # If we know the line and the target string, we can find the col range.
                ref_text = f"[[{ref.target}]]"
                # This is heuristic if multiple same refs on one line.
                # Ideally Parser gives col_start/col_end.
                # Let's assume for this iteration we assume it matches if on line.
                pass
                
        # Actually... without column info in AST `references` list from our current `TypedownParser`, 
        # we still need to match text to be precise about WHICH reference on the line.
        # BUT, the request is to "Refactor ... to use AST".
        # So let's implement the lookup using AST + Text Search for column refinement.
    
    # Re-implemented Logic:
    
    # 1. Check references inside blocks
    target_ref = _find_reference_at_position(doc, line, col)
    if target_ref and target_ref.identifier:
        # Resolve Identifier
        # We can use reference.identifier (Identifier Object)
        ref_id = str(target_ref.identifier)
        
        # Look up in symbol table
        if ref_id in ls.compiler.symbol_table:
             target_obj = ls.compiler.symbol_table[ref_id]
             if hasattr(target_obj, 'location') and target_obj.location:
                 return Location(
                    uri=Path(target_obj.location.file_path).as_uri(),
                    range=Range(
                        start=Position(line=max(0, target_obj.location.line_start-1), character=0),
                        end=Position(line=max(0, target_obj.location.line_end), character=0)
                    )
                )

    # 2. Check for Entity Type Definition (Go to Model)
    # Check if we are on the "Type" part of an entity declaration
    for entity in doc.entities:
        if entity.location.line_start == line:
             # Header line: ```entity:Type ID
             # Heuristic check on type name
             if entity.class_name:
                 # If cursor is within the type name range...
                 # We assume type name is present in the line text.
                 # Let's simple check if we are in the header line for now.
                 if hasattr(ls.compiler, 'model_registry') and entity.class_name in ls.compiler.model_registry:
                      model_cls = ls.compiler.model_registry[entity.class_name]
                      try:
                        src_file = inspect.getsourcefile(model_cls)
                        if src_file:
                            src_lines, start_line = inspect.getsourcelines(model_cls)
                            return Location(
                                uri=Path(src_file).as_uri(),
                                range=Range(
                                    start=Position(line=max(0, start_line - 1), character=0),
                                    end=Position(line=max(0, start_line + len(src_lines)), character=0)
                                )
                            )
                      except Exception:
                        pass
    return None

def _find_reference_at_position(doc, line: int, col: int):
    """Find the specific AST Reference node at the given position."""
    # Search all blocks that might contain references
    all_blocks = doc.entities + doc.specs # + doc.models (if they have refs?)
    
    # Also doc.references (global/top-level refs if any)
    # Actually doc.references contains ALL references found by parser in scanning.
    # So we can just iterate doc.references!
    
    candidates = [ref for ref in doc.references if ref.location.line_start == line]
    
    # Disambiguate by column if possible
    # Since our Parser currently sets line_start but maybe not col_start, 
    # we might need to peek at the raw content or rely on `target`.
    # Let's assume we find the one where the column matches `[[target]]` pattern in the line source.
    
    # We need the source line to check columns
    source_lines = doc.raw_content.splitlines()
    if line >= len(source_lines): return None
    text_line = source_lines[line]
    
    for ref in candidates:
        # Find all occurrences of [[target]] on this line
        needle = f"[[{ref.target}]]"
        # This is a bit weak if multiple same refs. 
        # But better than pure regex since we know it IS a reference.
        for match in re.finditer(re.escape(needle), text_line):
            if match.start() <= col <= match.end():
                return ref
    return None

@server.feature(TEXT_DOCUMENT_REFERENCES)
def references(ls: TypedownLanguageServer, params: ReferenceParams):
    if not ls.compiler or not ls.compiler.dependency_graph: return None

    uri = params.text_document.uri
    file_path = Path(uri.replace("file://", ""))
    
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

    # 2. Check if on an Entity Definition (Find references TO this entity)
    # E.g. clicking on `id: alice` -> find references to alice
    if not target_id:
        for entity in doc.entities:
            # Check if cursor is in the header or ID field?
            # Simplification: If cursor is inside the block, and we are NOT on a reference...
            # Are we defining the entity?
            # If we are on the line defining the ID?
            
            # Let's Assume if cursor is ANYWHERE in the block and not on a ref, we contextually refer to the entity itself?
            # Or strict: only on ID definition.
            
            # Strict approach: Check if cursor is on `id: ...` line.
            # But we don't have per-field location mapping yet.
            
            if entity.location.line_start <= line <= entity.location.line_end:
                # If we are here, and _find_reference_at_position failed, we might be defining the entity.
                # Let's assume yes.
                target_id = entity.id
                break

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

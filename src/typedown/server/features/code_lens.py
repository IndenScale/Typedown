from typing import List, Optional
from lsprotocol.types import (
    TEXT_DOCUMENT_CODE_LENS,
    CODE_LENS_RESOLVE,
    CodeLens,
    CodeLensParams,
    Command,
    Range,
    Position,
)
from typedown.server.application import server, TypedownLanguageServer
from typedown.server.managers.diagnostics import uri_to_path
from pathlib import Path

# Command constants
CMD_RUN_SPEC = "typedown.runSpec"
CMD_VIEW_FORMER = "typedown.viewFormer"

@server.feature(TEXT_DOCUMENT_CODE_LENS)
def code_lens(ls: TypedownLanguageServer, params: CodeLensParams) -> List[CodeLens]:
    if not ls.compiler:
        return []

    uri = params.text_document.uri
    path = uri_to_path(uri)
    
    if path not in ls.compiler.documents:
        return []
    
    doc = ls.compiler.documents[path]
    lenses = []
    
    # 1. Code Lens for Spec Blocks
    for spec in doc.specs:
        if spec.location:
            # Place at the start line of the block
            lenses.append(CodeLens(
                range=Range(
                    start=Position(line=max(0, spec.location.line_start - 1), character=0),
                    end=Position(line=max(0, spec.location.line_start - 1), character=0),
                ),
                command=Command(
                    title="▶ Run Spec",
                    command=CMD_RUN_SPEC,
                    arguments=[str(path), spec.id]
                )
            ))
            
    # 2. Code Lens for Entity Blocks (Former/Evolution)
    for entity in doc.entities:
        if entity.former_ids and entity.location:
            lenses.append(CodeLens(
                range=Range(
                    start=Position(line=max(0, entity.location.line_start - 1), character=0),
                    end=Position(line=max(0, entity.location.line_start - 1), character=0),
                ),
                command=Command(
                    title="📜 View Evolution",
                    command=CMD_VIEW_FORMER,
                    arguments=[str(path), entity.id]
                )
            ))
            
    return lenses

@server.command(CMD_RUN_SPEC)
def run_spec_command(ls: TypedownLanguageServer, *args):
    """Callback for Run Spec lens."""
    if not ls.compiler or len(args) < 2:
        return
        
    file_path_str, spec_id = args[0], args[1]
    ls.show_message(f"Running spec '{spec_id}'...", 3) # Info message
    
    # compile() now triggers Stage 3.5 (Specs) automatically
    with ls.lock:
        success = ls.compiler.compile()
    
    if success:
        ls.show_message(f"Spec '{spec_id}' (and all other L3 checks) passed! ✓", 3)
    else:
        # The specific failure will be shown as a diagnostic in the editor
        ls.show_message(f"Validation failed. ✗ Check errors in '{spec_id}'.", 1)

@server.command(CMD_VIEW_FORMER)
def view_former_command(ls: TypedownLanguageServer, *args):
    if not ls.compiler or len(args) < 2:
        return
        
    file_path_str, entity_id = args[0], args[1]
    # TODO: Implement a ghost text or peek view for evolution history
    ls.show_message(f"Evolution history for '{entity_id}' (P0 implemented former field)", 3)

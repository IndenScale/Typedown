from typing import List, Optional
from lsprotocol.types import (
    TEXT_DOCUMENT_CODE_LENS,
    CODE_LENS_RESOLVE,
    CodeLens,
    CodeLensParams,
    Command,
    Range,
    Position,
    ShowMessageParams,
    MessageType,
)
from typedown.server.application import server, TypedownLanguageServer
from typedown.server.managers.diagnostics import uri_to_path
from pathlib import Path

from pydantic import BaseModel

from typing import Any

# Pydantic models used for serialization construction only
class SpecCommandArgs(BaseModel):
    file_path: str
    spec_id: str

class EntityCommandArgs(BaseModel):
    file_path: str
    entity_id: str

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
                    arguments=[SpecCommandArgs(file_path=str(path), spec_id=spec.id).model_dump()]
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
                    arguments=[EntityCommandArgs(file_path=str(path), entity_id=entity.id).model_dump()]
                )
            ))
            
    return lenses

@server.command(CMD_RUN_SPEC)
def run_spec_command(ls: TypedownLanguageServer, *args):
    """Callback for Run Spec lens."""
    if not ls.compiler or not args:
        return

    # Unpack arguments manually (Robust against pygls version diffs)
    # expected args: [{'file_path': '...', 'spec_id': '...'}]
    try:
        if isinstance(args[0], list):
             data = args[0][0] # sometimes flattened
        else:
             data = args[0]
        
        # Determine if it's a dict (new style) or tuple (legacy fallback)
        if isinstance(data, dict):
             file_path_str = data.get("file_path")
             spec_id = data.get("spec_id")
        else:
             # Fallback just in case
             file_path_str = data[0]
             spec_id = data[1]
             
    except (IndexError, KeyError, TypeError):
        return

    if not file_path_str or not spec_id:
        return

    # compile() now triggers Stage 3.5 (Specs) automatically
    with ls.lock:
        # 1. Ensure L1/L2 state is fresh
        # ls.compiler.compile() -> REMOVED: This forces disk scan and overwrites in-memory dirty buffers!
        # Rely on did_change -> update_document -> _recompile_in_memory instead.
        
        # 2. Run L4 Specs explicitly
        success = ls.compiler.verify_specs(spec_filter=spec_id)
        
        # 3. Publish ALL diagnostics (L1+L2+L4)
        # This is critical: if we don't publish, the red squiggles won't show up.
        # import moved to top-level to avoid circular dependency if possible, 
        # but here we access via imported module
        from typedown.server.managers.diagnostics import publish_diagnostics
        publish_diagnostics(ls, ls.compiler)
    
    if success:
        ls.window_show_message(ShowMessageParams(
            type=MessageType.Info, 
            message=f"Spec passed."
        ))
    else:
        # The specific failure will be shown as a diagnostic in the editor
        # Get failure count if possible or just generic message
        # TypedownError does not have source_id by default. 
        # SpecExecutor messages are formatted 'Spec 'X' failed...'
        failure_count = sum(1 for d in ls.compiler.diagnostics if f"Spec '{spec_id}'" in d.message and d.severity == "error")
        msg = f"Spec failed with {failure_count} errors. See editor for details." if failure_count > 0 else "Spec failed."
        
        ls.window_show_message(ShowMessageParams(
            type=MessageType.Error, 
            message=msg
        ))

@server.command(CMD_VIEW_FORMER)
def view_former_command(ls: TypedownLanguageServer, *args):
    if not ls.compiler or not args:
        return
    
    try:
        if isinstance(args[0], list):
             data = args[0][0]
        else:
             data = args[0]
             
        if isinstance(data, dict):
             file_path_str = data.get("file_path")
             entity_id = data.get("entity_id")
        else:
             file_path_str = data[0]
             entity_id = data[1]
    except (IndexError, KeyError, TypeError):
        return
    # TODO: Implement a ghost text or peek view for evolution history
    ls.window_show_message(ShowMessageParams(
        type=MessageType.Info,
        message=f"Evolution history for '{entity_id}' (P0 implemented former field)"
    ))

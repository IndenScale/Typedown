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
CMD_TRIGGER_VALIDATION = "typedown.triggerValidation"
CMD_RECOMPILE = "typedown.recompile"

@server.feature(TEXT_DOCUMENT_CODE_LENS)
def code_lens(ls: TypedownLanguageServer, params: CodeLensParams) -> List[CodeLens]:
    if not ls.is_ready: return []
    if not ls.compiler:
        return []

    uri = params.text_document.uri
    path = uri_to_path(uri)
    
    ls.show_message_log(f"CodeLens Request for: {path}")
    
    if path not in ls.compiler.documents:
        ls.show_message_log(f"CodeLens: File not found in documents: {path}")
        return []
    
    doc = ls.compiler.documents[path]
    lenses = []
    
    # 1. Code Lens for Spec Blocks
    for spec in doc.specs:
        if spec.location:
            ls.show_message_log(f"CodeLens: Found Spec '{spec.id}'")
            # Place at the start line of the block
            lenses.append(CodeLens(
                range=Range(
                    start=Position(line=max(0, spec.location.line_start - 1), character=0),
                    end=Position(line=max(0, spec.location.line_start - 1), character=0),
                ),
                command=Command(
                    title="▶ Run Spec",
                    command=CMD_RUN_SPEC,
                    arguments=[SpecCommandArgs(file_path=str(path), spec_id=spec.id or "").model_dump()]
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
                    arguments=[EntityCommandArgs(file_path=str(path), entity_id=entity.id or "").model_dump()]
                )
            ))
            
    return lenses

@server.command(CMD_RUN_SPEC)
def run_spec_command(ls: TypedownLanguageServer, *args):
    """Callback for Run Spec lens."""
    if not ls.is_ready: return
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
        
        # Prepare capturing console to show output to user
        from io import StringIO
        from rich.console import Console
        
        output_buffer = StringIO()
        capturing_console = Console(file=output_buffer, force_terminal=False, width=120)
        
        # 2. Run L4 Specs explicitly
        success = ls.compiler.verify_specs(spec_filter=spec_id, console=capturing_console)
        
        # Capture output and send to client log
        run_output = output_buffer.getvalue()
        if run_output:
             # Use Info type to ensure it shows up clearly
             ls.show_message_log(f"--- Spec Execution Output ({spec_id}) ---\n{run_output}", MessageType.Info)
        
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
    if not ls.is_ready: return
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

@server.command(CMD_TRIGGER_VALIDATION)
def trigger_validation_command(ls: TypedownLanguageServer, *args):
    if not ls.is_ready: return
    if not ls.compiler:
        return
    
    # "Soft" Validation: Recompile in-memory documents only.
    # Used during editing to avoid overwriting unsaved changes with disk content.
    with ls.lock:
        try:
            ls.compiler._recompile_in_memory()
            
            # DEBUG: Log in-memory documents
            ls.compiler.console.print(f"[bold yellow]DEBUG: Memory Documents:[/bold yellow]")
            for path in ls.compiler.documents.keys():
                 ls.compiler.console.print(f" - {path}")

            # Run L4 Specs
            ls.compiler.verify_specs()
            
        except Exception as e:
            ls.compiler.console.print(f"[bold red]Validation Error:[/bold red] {e}")

        # Publish ALL diagnostics
        from typedown.server.managers.diagnostics import publish_diagnostics
        publish_diagnostics(ls, ls.compiler)


@server.command(CMD_RECOMPILE)
def recompile_command(ls: TypedownLanguageServer, *args):
    if not ls.is_ready: return
    if not ls.compiler:
        return

    # "Hard" Reset: Scan disk for new files.
    # Used when switching demos/projects to discover new file structure.
    # WARNING: This discards any in-memory unsaved changes (didOpen overlays).
    with ls.lock:
        ls.compiler.console.print(f"[bold blue]COMMAND: Recompile (Disk Scan)[/bold blue]")
        success = ls.compiler.compile()
        
        ls.compiler.console.print(f"[bold yellow]DEBUG: Scanned Documents:[/bold yellow]")
        for path in ls.compiler.documents.keys():
             ls.compiler.console.print(f" - {path}")

        if success:
            ls.compiler.verify_specs()
        
        from typedown.server.managers.diagnostics import publish_diagnostics
        publish_diagnostics(ls, ls.compiler)

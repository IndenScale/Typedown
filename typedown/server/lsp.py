import re
from pathlib import Path
from urllib.parse import urlparse, unquote, unquote_plus
from typing import Optional, List, Dict
import os
import sys

from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DEFINITION,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    DidSaveTextDocumentParams,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    DefinitionParams,
    Location,
    Diagnostic,
    DiagnosticSeverity,
    Range,
    Position,
)

from typedown.core.workspace import Workspace
from typedown.core.errors import TypedownError

class TypedownLanguageServer(LanguageServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workspace_instance: Optional[Workspace] = None

server = TypedownLanguageServer("typedown-server", "0.1.0")

def uri_to_path(uri: str) -> Path:
    parsed = urlparse(uri)
    # unquote helps with %20 spaces etc
    path_str = unquote(parsed.path)
    # On Windows, urlparse might leave a leading slash for C:/...
    if os.name == 'nt' and path_str.startswith('/'):
        path_str = path_str[1:]
    return Path(path_str).resolve()

def to_lsp_diagnostic(error: TypedownError) -> Diagnostic:
    # Default range (entire file if unknown)
    start_line = 0
    start_col = 0
    end_line = 0
    end_col = 0
    
    if error.location:
        # Pydantic/Validator line numbers are usually 1-indexed
        # LSP uses 0-indexed
        start_line = max(0, error.location.line_start - 1)
        end_line = max(0, error.location.line_end - 1)
        
        # Columns
        start_col = max(0, error.location.col_start - 1)
        if error.location.col_end:
            end_col = max(0, error.location.col_end - 1)
        else:
            # If no end column, try to make it visible
            end_col = 1000 
        
    return Diagnostic(
        range=Range(
            start=Position(line=start_line, character=start_col),
            end=Position(line=end_line, character=end_col),
        ),
        message=error.message,
        severity=DiagnosticSeverity.Error if error.severity == "error" else DiagnosticSeverity.Warning,
        source="typedown"
    )

def validate(ls: TypedownLanguageServer, uri: str):
    if not ls.workspace_instance:
        return

    try:
        # 1. Update the document in workspace with current content from LSP
        # We rely on pygls managing the document text via `ls.workspace.get_document(uri)`
        doc = ls.workspace.get_document(uri)
        path = uri_to_path(uri)
        content = doc.source
        
        # ls.show_message_log(f"Validating {path}...")
        
        # Update/Reindex this specific file using the in-memory content
        ls.workspace_instance.reindex_file(path, content=content)
        
        # 2. Run full validation
        # TODO: Optimize to only validate affected files
        errors = ls.workspace_instance.validate_project()
        
        # 3. Group errors by file
        file_diagnostics: Dict[str, List[Diagnostic]] = {}
        
        for e in errors:
            if not e.location: continue
            p = str(Path(e.location.file_path).resolve())
            if p not in file_diagnostics:
                file_diagnostics[p] = []
            file_diagnostics[p].append(to_lsp_diagnostic(e))
            
        # 4. Publish
        # Publish for current file (to ensure clearing)
        current_path_str = str(path)
        if current_path_str not in file_diagnostics:
            file_diagnostics[current_path_str] = []
            
        for file_path_str, diagnostics in file_diagnostics.items():
            # Convert path to URI
            file_uri = Path(file_path_str).as_uri()
            # ls.show_message_log(f"Publishing {len(diagnostics)} diagnostics for {file_uri}")
            ls.publish_diagnostics(file_uri, diagnostics)
            
    except Exception as e:
        ls.show_message_log(f"Validation Error: {e}")
        import traceback
        traceback.print_exc()

@server.feature("initialize")
def initialize(ls: TypedownLanguageServer, params):
    ls.show_message_log("Typedown LSP Server Initializing...")
    
    root_uri = params.root_uri or params.root_path
    if root_uri:
        if not root_uri.startswith('file://') and not root_uri.startswith('/'):
             root_path = Path(root_uri).resolve()
        else:
             root_path = uri_to_path(root_uri)
             
        ls.show_message_log(f"Loading workspace from: {root_path}")
        
        try:
            ls.workspace_instance = Workspace(root=root_path)
            # Initial load
            ls.workspace_instance.load(root_path)
            ls.show_message_log("Initial load complete.")
        except Exception as e:
            ls.show_message_log(f"Failed to initialize workspace: {e}")

@server.feature("shutdown")
def shutdown(ls: TypedownLanguageServer, params):
    ls.show_message_log("Typedown LSP Server Shutting down...")

@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: TypedownLanguageServer, params: DidOpenTextDocumentParams):
    ls.show_message_log(f"Document opened: {params.text_document.uri}")
    validate(ls, params.text_document.uri)

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: TypedownLanguageServer, params: DidChangeTextDocumentParams):
    validate(ls, params.text_document.uri)

@server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls: TypedownLanguageServer, params: DidSaveTextDocumentParams):
    ls.show_message_log(f"Document saved: {params.text_document.uri}")

@server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=["[", " ", "\"", ":"]))
def completions(ls: TypedownLanguageServer, params: CompletionParams):
    if not ls.workspace_instance:
        return []

    doc = ls.workspace.get_document(params.text_document.uri)
    lines = doc.source.splitlines()
    if params.position.line >= len(lines):
        return []
    
    line_content = lines[params.position.line]
    col = params.position.character
    
    # 1. Trigger for Reference: [[
    # Check if we are inside [[...]]
    # Simple check: Look backwards from cursor for [[
    prefix = line_content[:col]
    
    is_ref_trigger = False
    
    # Check for direct [[
    if prefix.endswith("[["):
        is_ref_trigger = True
    else:
        # Check if we are inside, e.g. [[Use|
        last_open = prefix.rfind("[[")
        last_close = prefix.rfind("]]")
        if last_open != -1:
            if last_close == -1 or last_close < last_open:
                # We are likely inside a reference
                is_ref_trigger = True
    
    # Check for 'former: "..."' or 'derived_from: "..."'
    # This is rough, but effective
    # Check if we are inside quotes?
    # For MVP, let's just dump ALL IDs if we think we might be in a place referencing an ID.
    
    if is_ref_trigger:
        items = []
        for entity_id, entity in ls.workspace_instance.project.symbol_table.items():
            kind = CompletionItemKind.Class
            detail = f"{entity.class_name}"
            
            item = CompletionItem(
                label=entity_id,
                kind=kind,
                detail=detail,
                documentation=f"Defined in {Path(entity.location.file_path).name}"
            )
            items.append(item)
        return CompletionList(is_incomplete=False, items=items)

    return []

@server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: TypedownLanguageServer, params: DefinitionParams):
    if not ls.workspace_instance:
        return None

    doc = ls.workspace.get_document(params.text_document.uri)
    lines = doc.source.splitlines()
    if params.position.line >= len(lines):
        return None
    
    line_content = lines[params.position.line]
    col = params.position.character
    
    # Find word at cursor or reference structure
    # Try to find [[ID]] matches
    target_id = None
    
    # 1. Search for [[ID]]
    for match in re.finditer(r'\[\[(.*?)\]\]', line_content):
        # Allow clicking anywhere inside [[...]] including brackets
        start = match.start()
        end = match.end()
        if start <= col <= end:
            target_id = match.group(1).strip()
            break
            
    # 2. Search for YAML key-value pairs like former: "ID"
    # This is harder to regex cleanly without tokenizer.
    # Let's try to grab the string literal at cursor.
    if not target_id:
        # Look for "ID" or 'ID'
        # Simple heuristic: Expand from cursor until quotes
        # Not robust but P0 sufficient
        pass # Skip for now, focus on [[...]]
        
    if target_id and target_id in ls.workspace_instance.project.symbol_table:
        entity = ls.workspace_instance.project.symbol_table[target_id]
        if entity.location:
             file_path = Path(entity.location.file_path)
             uri = file_path.as_uri()
             
             return Location(
                 uri=uri,
                 range=Range(
                     start=Position(line=max(0, entity.location.line_start - 1), character=0),
                     end=Position(line=max(0, entity.location.line_end - 1), character=100) # Select full line
                 )
             )
    
    return None

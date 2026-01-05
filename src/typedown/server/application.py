import logging
import sys
import threading
from pathlib import Path
from typing import Optional

from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    DidSaveTextDocumentParams,
    InitializeParams,
    MessageType,
    LogMessageParams,
    TextDocumentSyncKind,
)
from rich.console import Console

from typedown.core.compiler import Compiler
from typedown.server.managers.diagnostics import publish_diagnostics, uri_to_path
from typedown.server.managers.watcher import ProjectWatcher

# ======================================================================================
# Server Definition
# ======================================================================================

class TypedownLanguageServer(LanguageServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compiler: Optional[Compiler] = None
        self.watcher: Optional[ProjectWatcher] = None
        self.lock = threading.Lock()

    def show_message_log(self, message: str, message_type: MessageType = MessageType.Log):
        """Wrapper to safely show messages to the client log using the built-in window_log_message."""
        self.window_log_message(LogMessageParams(type=message_type, message=message))

# Create the server instance globally so decorators can use it
server = TypedownLanguageServer("typedown-server", "0.2.8")

# ======================================================================================
# Lifecycle Events
# ======================================================================================

@server.feature("initialize")
def initialize(ls: TypedownLanguageServer, params: InitializeParams):
    root_uri = params.root_uri or params.root_path
    root_path = Path('.') # Default to current dir if no root specified
    if root_uri:
        if not root_uri.startswith('file://') and not root_uri.startswith('/'):
             root_path = Path(root_uri).resolve()
        else:
             root_path = uri_to_path(root_uri)
             
    try:
        # Configure logging to file (optional, for debugging)
        # logging.basicConfig(filename='/tmp/typedown_lsp.log', level=logging.INFO)
            
        # Use stderr for Compiler output to avoid polluting stdout (LSP protocol)
        stderr_console = Console(stderr=True)
        ls.compiler = Compiler(target=root_path, console=stderr_console)
        
        # Warm up: Initial compilation
        ls.compiler.compile()
        
        logging.info(f"Typedown Engine Ready at {root_path}")
        # ls.show_message(f"Typedown: Engine ready at {root_path}", MessageType.Info)
        
    except Exception as e:
        logging.error(f"Failed to initialize compiler: {e}")
        ls.show_message_log(f"Typedown: Initialization failed - {e}", MessageType.Error)

    # Start Filesystem Watcher
    try:
        def on_change(path: Path):
            # This runs in a thread, so be careful. 
            # Ideally we schedule this on the main event loop if simple access isn't thread safe.
            # Compiler seems mostly synchronous so might be OK, but let's wrap or be cautious.
            # For now, direct call:
             if ls.compiler:
                 try:
                     with ls.lock:
                         content = path.read_text(encoding="utf-8")
                         ls.compiler.update_document(path, content)
                         # We need to trigger diagnostics publish. 
                         # publish_diagnostics uses ls.publish_diagnostics which sends LSP notification.
                         publish_diagnostics(ls, ls.compiler)
                 except Exception as err:
                     logging.error(f"Error processing external change for {path}: {err}")

        ls.watcher = ProjectWatcher(root_path, on_change)
        ls.watcher.start()
        
    except Exception as e:
        logging.error(f"Failed to start FS watcher: {e}")
        ls.show_message_log(f"Typedown: Watcher failed - {e}", MessageType.Warning)

@server.feature("shutdown")
def shutdown(ls: TypedownLanguageServer, *args):
    if ls.watcher:
        ls.watcher.stop()

@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: TypedownLanguageServer, params: DidOpenTextDocumentParams):
    # Publish diagnostics immediately upon opening a file
    if ls.compiler:
        uri = params.text_document.uri
        path = uri_to_path(uri)
        content = params.text_document.text
        
        # DEBUG: Verify content arrival
        print(f"DEBUG: did_open {path} (URI: {uri})")
        print(f"DEBUG: Content Length: {len(content)}")
        # print(f"DEBUG: Content Preview: {content[:50]}...")
        
        with ls.lock:
            # IMPORTANT: For memory-only files (Playground), we must manually feed 
            # the content to the compiler as it won't be found during disk scan.
            ls.compiler.update_document(path, content)
            
            # Verify compilation result
            if path in ls.compiler.documents:
                doc = ls.compiler.documents[path]
                print(f"DEBUG: Document compiled. Entities found: {len(doc.entities)}")
                # for ent in doc.entities:
                #    print(f"DEBUG: Entity: {ent.name} ({ent.kind})")
            else:
                print(f"DEBUG: Document {path} NOT found in compiler after update!")

            publish_diagnostics(ls, ls.compiler)

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: TypedownLanguageServer, params: DidChangeTextDocumentParams):
    if not ls.compiler:
        return
        
    uri = params.text_document.uri
    path = uri_to_path(uri)
    
    # We assume full text sync for now (pygls default behavior for syncKind=Full)
    if params.content_changes:
        content = params.content_changes[0].text
        
        with ls.lock:
            ls.show_message_log(f"DidChange: Updating {path}...")
            # Incremental Update -> Re-Link -> Re-Validate
            # This updates the compiler's internal state for this file
            ls.compiler.update_document(path, content)
            ls.show_message_log(f"DidChange: Update {path} complete. Doc entities: {len(ls.compiler.documents.get(path).entities) if path in ls.compiler.documents else 'None'}")
            
            # Publish new diagnostics after partial recompile
            publish_diagnostics(ls, ls.compiler)

@server.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: TypedownLanguageServer, params: DidSaveTextDocumentParams):
    # On save, we rely on the in-memory state which is likely most up-to-date.
    # However, if we wanted to sync with disk-based tools, we might re-read here.
    # For now, just ensuring diagnostics are visible is enough.
    if ls.compiler:
        publish_diagnostics(ls, ls.compiler)

# ======================================================================================
# Feature Registration
# ======================================================================================
# Importing these modules registers their @server.feature handlers
import typedown.server.features.completion
import typedown.server.features.hover
import typedown.server.features.navigation
import typedown.server.features.rename
import typedown.server.features.semantic_tokens
import typedown.server.features.code_lens

# ======================================================================================
# Entry Point
# ======================================================================================

def lsp_entry():
    """Entry point for the LSP server (STDIO)."""
    server.start_io()

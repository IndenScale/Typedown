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

# ======================================================================================
# Server Definition
# ======================================================================================

class TypedownLanguageServer(LanguageServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compiler: Optional[Compiler] = None
        self.lock = threading.Lock()
        # Pure Functional Architecture: Server is NOT ready until explicitly loaded via loadProject
        self.is_ready = False

    def show_message_log(self, message: str, message_type: MessageType = MessageType.Log):
        """Wrapper to safely show messages to the client log using the built-in window_log_message."""
        self.window_log_message(LogMessageParams(type=message_type, message=message))

# Create the server instance globally so decorators can use it
server = TypedownLanguageServer("typedown-server", "0.2.16")

# ======================================================================================
# Lifecycle Events
# ======================================================================================

@server.feature("initialize")
def initialize(ls: TypedownLanguageServer, params: InitializeParams):
    root_uri = params.root_uri or params.root_path
    root_path = Path('/') # Default to system root (safe for memory_only overlay scan)
    if root_uri:
        if not root_uri.startswith('file://') and not root_uri.startswith('/'):
             root_path = Path(root_uri).resolve()
        else:
             root_path = uri_to_path(root_uri)
             
    try:
        # Configure logging to file (optional, for debugging)
        # logging.basicConfig(filename='/tmp/typedown_lsp.log', level=logging.INFO)
        
        # Suppress noisy pygls warnings (Cancel notification for unknown message id)
        logging.getLogger("pygls.protocol.json_rpc").setLevel(logging.ERROR)
            
        # Use a quiet console to suppress Compiler's verbose Stage logs
        from io import StringIO
        quiet_console = Console(file=StringIO(), stderr=False)
        
        # Determine Mode (Disk vs Memory)
        # Default to Disk (Standard LSP) unless "memory" mode is requested (Web/WASM)
        mode = "disk"
        init_opts = params.initialization_options
        
        # Handle init_opts (can be object, dict or None)
        if init_opts:
            if isinstance(init_opts, dict):
                 mode = init_opts.get("mode", "disk")
            elif hasattr(init_opts, "mode"):
                 mode = getattr(init_opts, "mode")
        
        memory_only = (mode == "memory")
        
        # Initialize Compiler
        ls.compiler = Compiler(target=root_path, console=quiet_console, memory_only=memory_only)
        
        if memory_only:
            # Memory Mode: Wait for loadProject
            ls.is_ready = False
            logging.info(f"Typedown Engine Initialized (Memory Only). Waiting for loadProject at {root_path}")
        else:
            # Disk Mode: Scan immediately and be ready
            # Perform initial scan if root_path is valid
            if root_path and root_path != Path('/'):
                 logging.info(f"Scanning project at {root_path}...")
                 ls.compiler.compile()
            
            ls.is_ready = True
            logging.info(f"Typedown Engine Initialized (Disk Mode) at {root_path}")
            
    except Exception as e:
        logging.error(f"Failed to initialize compiler: {e}")
        ls.show_message_log(f"Typedown: Initialization failed - {e}", MessageType.Error)

    # Note: ProjectWatcher removed. We rely solely on Client to push changes (didChange/loadProject).

@server.feature("shutdown")
def shutdown(ls: TypedownLanguageServer, *args):
    pass

@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: TypedownLanguageServer, params: DidOpenTextDocumentParams):
    if not ls.is_ready:
        return

    # Publish diagnostics immediately upon opening a file
    if ls.compiler:
        uri = params.text_document.uri
        path = uri_to_path(uri)
        content = params.text_document.text
        
        with ls.lock:
            # IMPORTANT: For memory-only files (Playground), we must manually feed 
            # the content to the compiler as it won't be found during disk scan.
            ls.compiler.update_document(path, content)
            
            publish_diagnostics(ls, ls.compiler)

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: TypedownLanguageServer, params: DidChangeTextDocumentParams):
    if not ls.compiler or not ls.is_ready:
        return
        
    uri = params.text_document.uri
    path = uri_to_path(uri)
    
    # We assume full text sync for now (pygls default behavior for syncKind=Full)
    if params.content_changes:
        content = params.content_changes[0].text
        
        with ls.lock:
            # Incremental Update -> Re-Link -> Re-Validate
            ls.compiler.update_document(path, content)
            publish_diagnostics(ls, ls.compiler)

@server.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: TypedownLanguageServer, params: DidSaveTextDocumentParams):
    if not ls.is_ready:
        return

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
import typedown.server.features.lifecycle

# ======================================================================================
# Entry Point
# ======================================================================================

def lsp_entry():
    """Entry point for the LSP server (STDIO)."""
    server.start_io()

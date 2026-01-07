

import logging
from pathlib import Path
from typing import Dict, Any, Union
from pydantic import BaseModel

from typedown.server.application import server
from typedown.server.managers.diagnostics import publish_diagnostics, uri_to_path

# =========================================================
#  Data Models
# =========================================================

class LoadProjectParams(BaseModel):
    """Parameters for typedown/loadProject notification."""
    files: Dict[str, str]

# =========================================================
#  Project Lifecycle Features
# =========================================================

@server.feature("typedown/loadProject")
def load_project(ls, params: LoadProjectParams):
    """
    Specific Feature: Bulk Load Project into OverlayProvider.
    Params: { "files": { "path/to/file": "content" } }
    
    This feature is essential for environments like WASM/Playground where
    FileSystem access is restricted or virtualized, requiring an explicit
    'Hydration' step to populate the compiler's memory overlay.
    """
    if not ls.compiler:
        logging.error("Compiler not initialized")
        return

    try:
        # 0. Extract files from params
        # In Pyodide/WASM, pygls converts JSON to pygls.protocol.Object instead of dict.
        # We need to extract the actual dictionary data.
        files_raw = params.files
        
        # Handle both dict (native Python) and Object (Pyodide) types
        if hasattr(files_raw, '__dict__'):
            # pygls.protocol.Object case
            files = vars(files_raw)
        elif hasattr(files_raw, 'items'):
            # Already a dict
            files = files_raw
        else:
            # Fallback: try to convert to dict
            files = dict(files_raw)
        
        logging.info(f"Loading project with {len(files)} files...")
        
        with ls.lock:
            # 1. Clear previous overlay (Fresh Start)
            # This ensures we don't have stale files from previous Demos in memory.
            if hasattr(ls.compiler.source_provider, "overlay"):
                 ls.compiler.source_provider.overlay.clear()
            
            # 2. Update Overlay
            for path_str, content in files.items():
                # Handle URI or Path
                path = Path(uri_to_path(path_str)) if "://" in path_str else Path(path_str)
                ls.compiler.source_provider.update_overlay(path, content)
                
            # 3. Trigger Full Compilation
            # This must happen inside the lock to ensure didOpen/didChange wait
            # until the project is fully hydrated.
            ls.compiler.compile()
            
            # 4. Publish Diagnostics
            publish_diagnostics(ls, ls.compiler)
            
        logging.info("Project loaded and compiled successfully.")
        
    except Exception as e:
        logging.error(f"Failed to load project: {e}")
        import traceback
        traceback.print_exc()

@server.feature("typedown/resetFileSystem")
def reset_filesystem(ls, params: Any):
    """
    Clears the internal memory overlay.
    """
    if ls.compiler and hasattr(ls.compiler.source_provider, "overlay"):
        with ls.lock:
            ls.compiler.source_provider.overlay.clear()
            logging.info("FileSystem Overlay reset.")
            # Optionally recompile to clear diagnostics?
            # ls.compiler.compile() 

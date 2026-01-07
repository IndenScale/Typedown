

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

    # 0. Extract files from params - Log type info FIRST
    files_raw = params.files
    logging.info(f"DEBUG: files_raw type: {type(files_raw)}")
    logging.info(f"DEBUG: files_raw class: {files_raw.__class__.__name__}")
    logging.info(f"DEBUG: has __dict__: {hasattr(files_raw, '__dict__')}")
    logging.info(f"DEBUG: has items: {hasattr(files_raw, 'items')}")
    logging.info(f"DEBUG: isinstance dict: {isinstance(files_raw, dict)}")

    try:
        # 0. Extract files from params
        # CRITICAL INSIGHT: In Pyodide/WASM, pygls converts JSON to pygls.protocol.Object.
        # This Object stores JSON key-value pairs as ATTRIBUTES, not dict items.
        # 
        # Example JSON: {"files": {"file:///a.td": "content"}}
        # After pygls.structure_message():
        #   - params is a LoadProjectParams instance (or Object)
        #   - params.files is an Object with attribute "file:///a.td" = "content"
        #
        # We need to extract these attributes into a proper dict.
        
        files_raw = params.files
        files = {}
        
        # Debug: Log the actual type
        logging.info(f"DEBUG: files_raw type: {type(files_raw)}")
        logging.info(f"DEBUG: files_raw class name: {files_raw.__class__.__name__}")
        
        # Strategy 1: Check if it's already a dict
        if isinstance(files_raw, dict):
            logging.info("DEBUG: files_raw is already a dict")
            files = files_raw
        # Strategy 2: Try to use __dict__ to get attributes
        elif hasattr(files_raw, '__dict__'):
            logging.info("DEBUG: Extracting from __dict__")
            # Get all attributes, filter out private/magic ones
            obj_dict = files_raw.__dict__
            logging.info(f"DEBUG: __dict__ keys: {list(obj_dict.keys())[:5]}")  # Show first 5
            
            # The actual file mappings are stored as attributes
            # We need to iterate over all attributes and extract those that look like URIs
            for key, value in obj_dict.items():
                if not key.startswith('_'):  # Skip private attributes
                    files[key] = value
        # Strategy 3: Use dir() and getattr()
        else:
            logging.info("DEBUG: Using dir() and getattr()")
            for attr in dir(files_raw):
                if not attr.startswith('_'):  # Skip private/magic attributes
                    value = getattr(files_raw, attr)
                    if isinstance(value, str):  # Only include string values (file content)
                        files[attr] = value
        
        logging.info(f"Loading project with {len(files)} files...")
        if len(files) > 0:
            logging.info(f"DEBUG: First file URI: {list(files.keys())[0]}")
        
        with ls.lock:
            # 1. Clear previous overlay (Fresh Start)
            # This ensures we don't have stale files from previous Demos in memory.
            if hasattr(ls.compiler.source_provider, "overlay"):
                 ls.compiler.source_provider.overlay.clear()
            
            # 2. Update Overlay
            for path_str, content in files.items():
                # Handle URI or Path
                path = Path(uri_to_path(path_str)) if "://" in path_str else Path(path_str)
                logging.info(f"Hydrating: {path}")
                ls.compiler.source_provider.update_overlay(path, content)
                
            # 3. Trigger Full Compilation
            # This must happen inside the lock to ensure didOpen/didChange wait
            # until the project is fully hydrated.
            ls.compiler.compile()
            
            # 4. Mark as Ready
            ls.is_ready = True
            
            # 5. Publish Diagnostics
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
            ls.is_ready = False # Reset to idle state
            ls.compiler.source_provider.overlay.clear()
            logging.info("FileSystem Overlay reset. Server is now IDLE.")
            # Optionally recompile to clear diagnostics?
            # ls.compiler.compile() 

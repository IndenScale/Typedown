

import logging
from pathlib import Path
from typing import Dict, Any, Union, List
from pydantic import BaseModel

from typedown.server.application import server
from typedown.server.managers.diagnostics import publish_diagnostics, uri_to_path

# =========================================================
#  Data Models
# =========================================================

class FileItem(BaseModel):
    """A single file item for bulk loading."""
    uri: str
    content: str

class LoadProjectParams(BaseModel):
    """Parameters for typedown/loadProject notification."""
    files: List[FileItem]

# =========================================================
#  Project Lifecycle Features
# =========================================================

@server.feature("typedown/loadProject")
def load_project(ls, params: Any):
    """
    Specific Feature: Bulk Load Project into OverlayProvider.
    Supports both:
    - New format: { "files": [ { "uri": "...", "content": "..." } ] }
    - Legacy format: { "files": { "uri": "content" } }
    """
    if not ls.compiler:
        logging.error("Compiler not initialized")
        return

    try:
        # 1. Extract raw files data
        # params can be a LoadProjectParams instance, a dict, or a pygls.protocol.Object
        files_raw = getattr(params, "files", None)
        if files_raw is None and isinstance(params, dict):
            files_raw = params.get("files")
            
        if files_raw is None:
            logging.error("No files found in params")
            return

        # 2. Normalize to a dict of {uri: content}
        normalized_files = {}
        
        # Case A: It's a list (New Format)
        if isinstance(files_raw, list):
            for item in files_raw:
                if isinstance(item, dict):
                    uri = item.get("uri")
                    content = item.get("content")
                else:
                    uri = getattr(item, "uri", None)
                    content = getattr(item, "content", None)
                
                if uri and content is not None:
                    normalized_files[uri] = content
                    
        # Case B: It's a dict (Legacy Format or direct dict)
        elif isinstance(files_raw, dict):
            normalized_files = files_raw
            
        # Case C: It's a pygls.protocol.Object (WASM proxy)
        else:
            # Try to iterate attributes
            for attr in dir(files_raw):
                if not attr.startswith("_"):
                    val = getattr(files_raw, attr)
                    if isinstance(val, str):
                        normalized_files[attr] = val

        logging.info(f"Loading project with {len(normalized_files)} files...")
        
        with ls.lock:
            if hasattr(ls.compiler.source_provider, "overlay"):
                 ls.compiler.source_provider.overlay.clear()
            
            for uri, content in normalized_files.items():
                path = Path(uri_to_path(uri)) if "://" in uri else Path(uri)
                logging.info(f"Hydrating: {path}")
                ls.compiler.source_provider.update_overlay(path, content)
                
            ls.compiler.compile()
            ls.is_ready = True
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

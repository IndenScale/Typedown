from typing import List, Dict, Tuple, Optional
from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    Range,
    Position,
    PublishDiagnosticsParams,
)
from typedown.core.compiler import Compiler
from typedown.core.base.errors import TypedownError
from pathlib import Path
import os
from urllib.parse import urlparse, unquote

def uri_to_path(uri: str) -> Path:
    parsed = urlparse(uri)
    path_str = unquote(parsed.path)
    if os.name == 'nt' and path_str.startswith('/'):
        path_str = path_str[1:]
    return Path(path_str).resolve()

def to_lsp_diagnostic(error: TypedownError) -> Diagnostic:
    start_line, start_col = 0, 0
    end_line, end_col = 0, 0
    
    if error.location:
        # Mistune/Typedown lines are 1-based usually
        # LSP is 0-based
        sl = getattr(error.location, 'line_start', 1)
        el = getattr(error.location, 'line_end', 1)
        sc = getattr(error.location, 'col_start', 1)
        ec = getattr(error.location, 'col_end', 1) 
        
        start_line = max(0, sl - 1) if sl else 0
        end_line = max(0, el - 1) if el else 0
        start_col = max(0, sc - 1) if sc else 0
        end_col = max(0, ec - 1) if ec else 100
        
    return Diagnostic(
        range=Range(
            start=Position(line=start_line, character=start_col),
            end=Position(line=end_line, character=end_col),
        ),
        message=error.message,
        severity=DiagnosticSeverity.Error if error.severity == "error" else DiagnosticSeverity.Warning,
        source="typedown"
    )

def publish_diagnostics(ls: LanguageServer, compiler: Compiler):
    """
    Groups diagnostics by file and publishes them to the client.
    """
    if not compiler:
        return

    # Group diagnostics by file
    file_diagnostics: Dict[str, List[Diagnostic]] = {}
    
    for err in compiler.diagnostics:
        if not err.location or not err.location.file_path:
            continue
        
        p = str(Path(err.location.file_path).resolve())
        if p not in file_diagnostics:
            file_diagnostics[p] = []
        file_diagnostics[p].append(to_lsp_diagnostic(err))
        
    # Broadcast to all known files (including clearing resolved errors)
    for doc_path in compiler.documents.keys():
        p_str = str(doc_path.resolve())
        diags = file_diagnostics.get(p_str, [])
        ls.text_document_publish_diagnostics(
            PublishDiagnosticsParams(uri=Path(p_str).as_uri(), diagnostics=diags)
        )

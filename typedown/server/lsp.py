import logging
import re
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import Optional, List, Dict
import os
import sys
import tempfile

# Configure logging to file
log_file = Path(tempfile.gettempdir()) / 'typedown_server.log'
try:
    logging.basicConfig(filename=str(log_file), level=logging.DEBUG, filemode='a')
except Exception:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

logging.getLogger("markdown_it").setLevel(logging.WARNING)

from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    DidSaveTextDocumentParams,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    HoverParams,
    Hover,
    DefinitionParams,
    Location,
    Diagnostic,
    DiagnosticSeverity,
    Range,
    Position,
    MessageType,
    ShowMessageParams,
    PublishDiagnosticsParams,
    SemanticTokensLegend,
    SemanticTokens,
    SemanticTokensParams,
)

from typedown.core.compiler import Compiler
from typedown.core.errors import TypedownError

class TypedownLanguageServer(LanguageServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compiler: Optional[Compiler] = None

server = TypedownLanguageServer("typedown-server", "0.1.0")

# Semantic Tokens Legend
SEMANTIC_LEGEND = SemanticTokensLegend(
    token_types=["class", "variable", "property", "struct"],
    token_modifiers=["declaration", "definition"]
)

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
        ec = getattr(error.location, 'col_end', 1) # Optional?
        
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

def validate_workspace(ls: TypedownLanguageServer):
    if not ls.compiler:
        return

    try:
        # Trigger full compilation
        # Note: In a real incremental implementation, we would update specific files in compiler.documents
        # For now, we rely on disk coherence (assuming file is saved or we update it)
        # However, LSP sends 'did_change', file might not be saved.
        # MVP: We only fully support validation on SAVE or if we implement memory-vfs in compiler.
        # Let's assume we validate what's on disk for now, or just run compile() 
        # which reads from disk in current implementation.
        
        ls.compiler.compile()
        
        # Group diagnostics by file
        file_diagnostics: Dict[str, List[Diagnostic]] = {}
        
        for err in ls.compiler.diagnostics:
            if not err.location or not err.location.file_path:
                continue
            
            p = str(Path(err.location.file_path).resolve())
            if p not in file_diagnostics:
                file_diagnostics[p] = []
            file_diagnostics[p].append(to_lsp_diagnostic(err))
            
        # Publish
        # We should ideally clear diagnostics for files that are now clean.
        # A simple strategy is to broadcast to all known files in compiler.documents
        for doc_path in ls.compiler.documents.keys():
            p_str = str(doc_path.resolve())
            diags = file_diagnostics.get(p_str, [])
            ls.text_document_publish_diagnostics(
                PublishDiagnosticsParams(uri=Path(p_str).as_uri(), diagnostics=diags)
            )

    except Exception as e:
        # ls.show_message(f"Validation Error: {e}", MessageType.Error)
        logging.error(f"Validation Error: {e}")

@server.feature("initialize")
def initialize(ls: TypedownLanguageServer, params):
    root_uri = params.root_uri or params.root_path
    if root_uri:
        if not root_uri.startswith('file://') and not root_uri.startswith('/'):
             root_path = Path(root_uri).resolve()
        else:
             root_path = uri_to_path(root_uri)
             
        try:
            from rich.console import Console
            # Use stderr for Compiler output to avoid polluting stdout (LSP protocol)
            stderr_console = Console(stderr=True)
            ls.compiler = Compiler(target=root_path, console=stderr_console)
            # Pre-compile to warm up symbols
            ls.compiler.compile()
            # ls.show_message("Typedown Engine Ready.", MessageType.Info)
            logging.info("Typedown Engine Ready.")
        except Exception as e:
            # ls.show_message(f"Failed to initialize compiler: {e}", MessageType.Error)
            logging.error(f"Failed to initialize compiler: {e}")

@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: TypedownLanguageServer, params: DidOpenTextDocumentParams):
    validate_workspace(ls)

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: TypedownLanguageServer, params: DidChangeTextDocumentParams):
    # Compiler strictly reads from disk in current impl.
    # So we don't validate on change unless we implement VFS.
    # To avoid confusion, we skip validation here or do it only if we trust disk is sync?
    # Better to wait for Save for current Architecture P0.
    pass 

@server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls: TypedownLanguageServer, params: DidSaveTextDocumentParams):
    # Disk updated, safe to compile
    validate_workspace(ls)

@server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=["[", " "]))
def completions(ls: TypedownLanguageServer, params: CompletionParams):
    if not ls.compiler: return []
    
    # Simple heuristic: Always provide IDs if we suspect a value context
    # Refinement needed later
    items = []
    for entity_id, entity in ls.compiler.symbol_table.items():
        items.append(CompletionItem(
            label=entity_id,
            kind=CompletionItemKind.Class,
            detail=entity.type_name or "Entity",
            documentation=f"Defined in {Path(entity.location.file_path).name}"
        ))
    return CompletionList(is_incomplete=False, items=items)

@server.feature(TEXT_DOCUMENT_HOVER)
def hover(ls: TypedownLanguageServer, params: HoverParams):
    if not ls.compiler: return None
    
    # We need to read the document line to find what is under cursor
    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    if params.position.line >= len(lines): return None
    line = lines[params.position.line]
    col = params.position.character
    
    # 1. Check for [[ID]]
    for match in re.finditer(r'\[\[(.*?)\]\]', line):
        if match.start() <= col <= match.end():
            ref_id = match.group(1).strip()
            if ref_id in ls.compiler.symbol_table:
                entity = ls.compiler.symbol_table[ref_id]
                md = f"**Entity**: `{ref_id}`\n\n**Type**: `{entity.type_name}`"
                return Hover(contents=md)
    
    # 2. Check for Entity Block Header: ```entity:Type
    match = re.match(r'^(\s*)(```)(entity):([a-zA-Z0-9_\.]+)', line)
    if match:
        # Check if cursor is on Type name
        type_start = match.start(4)
        type_end = match.end(4)
        if type_start <= col <= type_end:
            type_name = match.group(4)
            
            # Lookup in compiler's model registry
            if hasattr(ls.compiler, 'model_registry') and type_name in ls.compiler.model_registry:
                model_cls = ls.compiler.model_registry[type_name]
                
                md = f"**Type**: `{type_name}`\n\n"
                md += f"**Python**: `{model_cls.__name__}`\n\n"
                
                if model_cls.__doc__:
                    md += f"{model_cls.__doc__}\n\n"
                
                md += "**Fields**:\n"
                for name, field in model_cls.model_fields.items():
                    req = " (Required)" if field.is_required() else ""
                    # annot = str(field.annotation).replace("typing.", "")
                    md += f"- `{name}`{req}\n"
                
                return Hover(contents=md)
            else:
                 return Hover(contents=f"**Type**: `{type_name}` (Not Found in Registry)")

    return None

@server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: TypedownLanguageServer, params: DefinitionParams):
    if not ls.compiler: return None

    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    if params.position.line >= len(lines): return None
    line = lines[params.position.line]
    col = params.position.character
    
    # 1. Check for [[ID]]
    for match in re.finditer(r'\[\[(.*?)\]\]', line):
        if match.start() <= col <= match.end():
            ref_id = match.group(1).strip()
            if ref_id in ls.compiler.symbol_table:
                entity = ls.compiler.symbol_table[ref_id]
                if entity.location:
                    return Location(
                        uri=Path(entity.location.file_path).as_uri(),
                        range=Range(
                            start=Position(line=max(0, entity.location.line_start-1), character=0),
                            end=Position(line=max(0, entity.location.line_end), character=0)
                        )
                    )
    
    # 2. Check for Entity Block Header: ```entity:Type
    match = re.match(r'^(\s*)(```)(entity):([a-zA-Z0-9_\.]+)', line)
    if match:
        type_start = match.start(4)
        type_end = match.end(4)
        if type_start <= col <= type_end:
            type_name = match.group(4)
            
            if hasattr(ls.compiler, 'model_registry') and type_name in ls.compiler.model_registry:
                model_cls = ls.compiler.model_registry[type_name]
                import inspect
                try:
                    src_file = inspect.getsourcefile(model_cls)
                    if src_file:
                        src_lines, start_line = inspect.getsourcelines(model_cls)
                        uri = Path(src_file).as_uri()
                        return Location(
                            uri=uri,
                            range=Range(
                                start=Position(line=max(0, start_line - 1), character=0),
                                end=Position(line=max(0, start_line + len(src_lines)), character=0)
                            )
                        )
                except Exception:
                    pass

    return None


@server.feature(TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, SEMANTIC_LEGEND)
def semantic_tokens(ls: TypedownLanguageServer, params: SemanticTokensParams):
    """
    Provide semantic tokens for syntax highlighting.
    We specifically want to highlight the 'ClassName' in ```entity:ClassName as a Class.
    """
    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    
    data = []
    last_line = 0
    last_start = 0

    for line_num, line in enumerate(lines):
        # Regex for entity block header: ```entity:Type ...
        # Capture: 1=indent, 2=entity:, 3=Type
        match = re.match(r'^(\s*)(```)(entity):([a-zA-Z0-9_\.]+)', line)
        if match:
            # We want to highlight the Type (group 4)
            # Calculate absolute start col of Type
            indent_len = len(match.group(1))
            # backticks=3
            # entity=6
            # colon=1
            # But regex groups help. start of group 4 is what we want.
            type_start_col = match.start(4)
            type_len = len(match.group(4))
            
            # Semantic Tokens are Delta-encoded relative to previous token
            delta_line = line_num - last_line
            if delta_line > 0:
                delta_start = type_start_col
            else:
                delta_start = type_start_col - last_start
                
            # Emit Token: [deltaLine, deltaStart, length, tokenType, tokenModifiers]
            # tokenType index in LEGEND: "class" is 0
            data.extend([delta_line, delta_start, type_len, 0, 0])
            
            last_line = line_num
            last_start = type_start_col

    return SemanticTokens(data=data)


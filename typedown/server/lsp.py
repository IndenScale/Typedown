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
    TEXT_DOCUMENT_REFERENCES,
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
    ReferenceParams,
    RenameParams,
    TEXT_DOCUMENT_RENAME,
    WorkspaceEdit,
    TextEdit,
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

import threading

class Debouncer:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.timer = None

    def debounce(self, func, *args, **kwargs):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.interval, func, args=args, kwargs=kwargs)
        self.timer.start()

# Global debouncer for validation
validation_debouncer = Debouncer(1.0) 

def _validate_single_doc(ls: TypedownLanguageServer, uri: str, content: str):
    """
    Lightweight validation for a single dirty document.
    Does NOT trigger full compile.
    Only checks Entity Pydantic Compliance against currently loaded models.
    """
    if not ls.compiler or not hasattr(ls.compiler, 'model_registry'):
        return

    from typedown.core.mistune_parser import TypedownParser
    parser = TypedownParser()
    try:
        # Parse content in-memory
        doc = parser.parse_text(content, fake_path=uri_to_path(uri))
        
        diagnostics = []
        
        for entity in doc.entities:
            # Check if model exists
            if entity.type_name not in ls.compiler.model_registry:
                # We can report unknown type immediately
                diagnostics.append(Diagnostic(
                    range=Range(
                        start=Position(line=entity.location.line_start-1, character=0),
                        end=Position(line=entity.location.line_start-1, character=100)
                    ),
                    message=f"Unknown Entity Type: {entity.type_name}",
                    severity=DiagnosticSeverity.Error,
                    source="typedown-realtime"
                ))
                continue
            
            # Validate against Pydantic Model
            model_cls = ls.compiler.model_registry[entity.type_name]
            try:
                # Basic validation (ignoring refs for now as they require graph)
                model_cls.model_validate(entity.data)
            except Exception as e:
                # Pydantic ValidationError
                # We try to extract line numbers from e (pydantic errors have 'loc')
                # But mapping back to YAML dict inside Markdown is hard without source map.
                # Fallback: Report on the Entity Header
                diagnostics.append(Diagnostic(
                    range=Range(
                        start=Position(line=entity.location.line_start-1, character=0),
                        end=Position(line=entity.location.line_end, character=0)
                    ),
                    message=f"Validation Error: {str(e)}",
                    severity=DiagnosticSeverity.Error,
                    source="typedown-realtime"
                ))
        
        # Publish Diagnostics for this file only
        ls.text_document_publish_diagnostics(
            PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics)
        )
        
    except Exception as e:
        logging.error(f"Real-time validation failed: {e}")

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: TypedownLanguageServer, params: DidChangeTextDocumentParams):
    # Trigger debounced validation
    # We only assume full text sync for simplicity (VSCode default)
    # params.content_changes[0].text
    if params.content_changes:
        content = params.content_changes[0].text
        validation_debouncer.debounce(_validate_single_doc, ls, params.text_document.uri, content)
 

@server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls: TypedownLanguageServer, params: DidSaveTextDocumentParams):
    # Disk updated, safe to compile
    validate_workspace(ls)

@server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=["["]))
def completions(ls: TypedownLanguageServer, params: CompletionParams):
    if not ls.compiler: return []
    
    # Read context to determine if we are in a wiki link
    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    if params.position.line >= len(lines): return []
    
    line = lines[params.position.line]
    col = params.position.character
    prefix = line[:col]
    
    items = []
    
    # CASE 1: [[class:
    class_match = re.search(r'\[\[class:([\w\.\-_]*)$', prefix)
    if class_match:
        # Show all known Models
        if hasattr(ls.compiler, 'model_registry'):
            for model_name, model_cls in ls.compiler.model_registry.items():
                items.append(CompletionItem(
                    label=model_name,
                    kind=CompletionItemKind.Class,
                    detail="Model",
                    documentation=model_cls.__doc__ or f"Pydantic Model {model_name}",
                    insert_text=f"{model_name}]]",
                    sort_text=f"00_{model_name}"
                ))
        return CompletionList(is_incomplete=False, items=items)

    # CASE 2: [[entity:
    entity_match = re.search(r'\[\[entity:([\w\.\-_]*)$', prefix)
    if entity_match:
        # Show all known Entities
        for entity_id, entity in ls.compiler.symbol_table.items():
            items.append(CompletionItem(
                label=entity_id,
                kind=CompletionItemKind.Class,
                detail=entity.type_name or "Entity",
                documentation=f"Defined in {Path(entity.location.file_path).name}",
                insert_text=f"{entity_id}]]",
                sort_text=f"00_{entity_id}"
            ))
        return CompletionList(is_incomplete=False, items=items)

    # CASE 3: [[header:
    header_match = re.search(r'\[\[header:([\w\.\-_ ]*)$', prefix)
    if header_match:
        # Show all known Headers from all docs
        for doc_path, doc in ls.compiler.documents.items():
            for hdr in doc.headers:
                title = hdr.get('title', 'Untitled')
                level = hdr.get('level', 1)
                # Format: Title (File.md)
                items.append(CompletionItem(
                    label=title,
                    kind=CompletionItemKind.Reference, # Use Reference icon for headers
                    detail=f"H{level} in {doc_path.name}",
                    insert_text=f"{title}]]",
                    sort_text=f"00_{title}"
                ))
        return CompletionList(is_incomplete=False, items=items)

    # CASE 4: Generic [[
    # Valid patterns: "[[", "[[abc" (but NOT [[class: or [[entity:)
    # excluding ':' from char class ensures we don't match specific scopes halfway
    match = re.search(r'\[\[([^:\]]*)$', prefix)
    
    if match:
        # 1. Snippets
        for snip in ["entity:", "class:", "header:"]:
            items.append(CompletionItem(
                label=snip,
                kind=CompletionItemKind.Keyword,
                detail=f"Scope to {snip[:-1]}",
                insert_text=snip,
                sort_text=f"00_{snip}_snippet", 
                command={'title': 'Trigger Completion', 'command': 'editor.action.triggerSuggest'}
            ))

        # 2. Entities (Icon: Class/Struct)
        for entity_id, entity in ls.compiler.symbol_table.items():
            items.append(CompletionItem(
                label=entity_id,
                kind=CompletionItemKind.Struct, # Distinct from Class
                detail=entity.type_name or "Entity",
                documentation=f"Defined in {Path(entity.location.file_path).name}",
                insert_text=f"{entity_id}]]",
                sort_text=f"10_{entity_id}"
            ))
            
        # 3. Files (Icon: File)
        # Scan target files known to compiler
        for doc_path in ls.compiler.documents.keys():
            path_name = doc_path.name
            items.append(CompletionItem(
                label=path_name,
                kind=CompletionItemKind.File,
                detail="File",
                insert_text=f"{path_name}]]",
                sort_text=f"20_{path_name}"
            ))

        return CompletionList(is_incomplete=False, items=items)
        
    return []

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
                
                # Basic Info
                md = f"**Entity**: `{ref_id}`  |  **Type**: `{entity.type_name}`\n\n"
                
                # Fetch Content Preview if possible
                if entity.location and entity.location.file_path:
                    try:
                        p = Path(entity.location.file_path)
                        if p.exists():
                            # We want to read lines around the definition
                            # Mistune location is 1-based
                            start = entity.location.line_start
                            end = entity.location.line_end
                            
                            # Read file content safely
                            # Optimization: In real LSP use workspace documents if open
                            content_lines = p.read_text(encoding="utf-8").splitlines()
                            
                            # Extract snippet (up to 8 lines)
                            snippet_lines = content_lines[start:min(end, start + 8)]
                            snippet = "\n".join(snippet_lines)
                            
                            md += f"```yaml\n{snippet}\n```"
                            if end - start > 8:
                                md += "\n*(...)*"
                    except Exception:
                        pass

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

@server.feature(TEXT_DOCUMENT_REFERENCES)
def references(ls: TypedownLanguageServer, params: ReferenceParams):
    if not ls.compiler or not ls.compiler.dependency_graph: return None

    # Find the entity ID under cursor
    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    if params.position.line >= len(lines): return None
    line = lines[params.position.line]
    col = params.position.character
    
    target_id = None
    
    # 1. Check if we are hovering over [[ID]]
    for match in re.finditer(r'\[\[(.*?)\]\]', line):
        if match.start() <= col <= match.end():
            target_id = match.group(1).strip()
            break
            
    # 2. Check if we are at definition ```entity:Type ID
    # This requires parsing the ID from the entity block header if it exists there, 
    # OR (more commonly in Typedown) the ID is implicit or inside the block.
    # Actually, often Typedown is ```entity:Type \n id: ...```
    # But let's support explicit lookup by ID if user highlights an ID string in YAML/JSON too?
    # For now, let's stick to [[ID]] as the primary invocation method for "Find Refs" 
    # or if the user is hovering the definition itself. 
    # But definition is harder to detect regex-wise without full parser location map.
    
    # Let's try to find if the cursor is on a word that matches an EntityID
    if not target_id:
        # Simple word extraction
        word_match = re.search(r'([\w\.\-_]+)', line[col:])
        # Use a simpler approach: get word at cursor
        # (Naive implementation for MVP)
        # Check if the "word" under cursor is a known symbol
        # We walk backwards and forwards from col
        start = col
        while start > 0 and (line[start-1].isalnum() or line[start-1] in "._-"):
            start -= 1
        end = col
        while end < len(line) and (line[end].isalnum() or line[end] in "._-"):
            end += 1
        
        candidate = line[start:end]
        if candidate in ls.compiler.symbol_table:
            target_id = candidate

    if target_id and target_id in ls.compiler.dependency_graph.reverse_adj:
        locations = []
        referencing_ids = ls.compiler.dependency_graph.reverse_adj[target_id]
        
        for ref_id in referencing_ids:
            if ref_id in ls.compiler.symbol_table:
                entity = ls.compiler.symbol_table[ref_id]
                # We point to the *Definition* of the referencing entity
                # Ideally, we would point to the exact LINE usage, but we don't track column of usages yet
                # So we return the Location of the Entity that uses it.
                if entity.location:
                    locations.append(Location(
                        uri=Path(entity.location.file_path).as_uri(),
                        range=Range(
                            start=Position(line=max(0, entity.location.line_start-1), character=0),
                            end=Position(line=max(0, entity.location.line_end), character=0)
                        )
                    ))
        return locations
        
    return []


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


@server.feature(TEXT_DOCUMENT_RENAME)
def rename(ls: TypedownLanguageServer, params: RenameParams):
    if not ls.compiler or not ls.compiler.dependency_graph: return None

    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    if params.position.line >= len(lines): return None
    line = lines[params.position.line]
    col = params.position.character
    
    # Identify target ID
    target_id = None
    
    # 1. From Wiki Link [[ID]]
    for match in re.finditer(r'\[\[(.*?)\]\]', line):
        if match.start() <= col <= match.end():
            target_id = match.group(1).strip()
            break
            
    # 2. From Word (if cursor on definition or bare word)
    if not target_id:
         word_match = re.search(r'([\w\.\-_]+)', line[col:])
         start = col
         while start > 0 and (line[start-1].isalnum() or line[start-1] in "._-"):
            start -= 1
         end = col
         while end < len(line) and (line[end].isalnum() or line[end] in "._-"):
            end += 1
         candidate = line[start:end]
         if candidate in ls.compiler.symbol_table:
             target_id = candidate

    if not target_id:
        return None
        
    changes: Dict[str, List[TextEdit]] = {}
    
    # Strategy: Scan ALL documents for [[TargetID]] and update them.
    # We rely on raw text search because our Parser's reference location tracking is currently 0.
    
    for doc_path, doc_obj in ls.compiler.documents.items():
        uri = doc_path.as_uri()
        doc_edits = []
        
        try:
            content = doc_obj.raw_content 
            if not content: continue
            
            # Find all [[TargetID]]
            # Pattern: matches literal [[ + ID + ]]
            # We want to replace just the ID part.
            pattern = f"[[{target_id}]]"
            
            # Iterate all matches
            for match in re.finditer(re.escape(pattern), content):
                # match covers "[[TargetID]]"
                start_idx = match.start()
                
                # The ID starts after "[[" (2 chars)
                id_start_idx = start_idx + 2
                id_end_idx = id_start_idx + len(target_id)
                
                # Convert absolute index to Line/Col
                pre_content = content[:id_start_idx]
                line_num = pre_content.count('\n')
                last_newline = pre_content.rfind('\n')
                if last_newline == -1:
                    col_num = len(pre_content)
                else:
                    col_num = len(pre_content) - (last_newline + 1)
                
                doc_edits.append(TextEdit(
                    range=Range(
                        start=Position(line=line_num, character=col_num),
                        end=Position(line=line_num, character=col_num + len(target_id))
                    ),
                    new_text=params.new_name
                ))
                
            # TODO: Also rename the Definition itself if found?
            # E.g. ```entity Type: TargetID
            # This is harder to regex safely without strict parsing.
            # We'll skip definition rename for this safety-first MVP unless it's strictly [[ID]].
            
        except Exception as e:
            logging.error(f"Rename error in {doc_path}: {e}")
            continue

        if doc_edits:
            if uri not in changes: changes[uri] = []
            changes[uri].extend(doc_edits)

    return WorkspaceEdit(changes=changes)


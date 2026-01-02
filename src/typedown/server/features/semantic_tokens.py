from lsprotocol.types import (
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    SemanticTokensLegend,
    SemanticTokens,
    SemanticTokensParams,
)
from typedown.server.application import server, TypedownLanguageServer
import re

# Semantic Tokens Legend
SEMANTIC_LEGEND = SemanticTokensLegend(
    token_types=["class", "variable", "property", "struct"],
    token_modifiers=["declaration", "definition"]
)

@server.feature(TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, SEMANTIC_LEGEND)
def semantic_tokens(ls: TypedownLanguageServer, params: SemanticTokensParams):
    """
    Provide semantic tokens for syntax highlighting.
    We specifically want to highlight the 'ClassName' in ```entity Type: Handle
    and the 'Handle' (Instance Name) as a Variable.
    """
    doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = doc.source.splitlines()
    
    data = []
    last_line = 0
    last_start = 0

    # Strict Regex for: ```entity Type: Handle
    # Group 1: indent
    # Group 2: Type
    # Group 3: Handle (Optional)
    # Use [\w\.\-] to match words, dots, and hyphens. Hyphen escaped.
    entity_pattern = re.compile(r'^(\s*)```entity\s+([\w\.\-]+)(?:\s*:\s*([\w\.\-]+))?')

    for line_num, line in enumerate(lines):
        match = entity_pattern.match(line)
        if match:
            # 1. Highlight Type (Class) -> Token Type 0
            type_text = match.group(2)
            type_start = match.start(2)
            type_len = len(type_text)
            
            # Delta for Type
            delta_line = line_num - last_line
            if delta_line > 0:
                delta_start = type_start
            else:
                delta_start = type_start - last_start
                
            data.extend([delta_line, delta_start, type_len, 0, 0])
            
            last_line = line_num
            last_start = type_start
            
            # 2. Highlight Handle (Variable) -> Token Type 1 (if present)
            if match.group(3):
                handle_text = match.group(3)
                handle_start = match.start(3)
                handle_len = len(handle_text)
                
                # Delta for Handle (same line)
                delta_line_h = 0
                delta_start_h = handle_start - last_start
                
                data.extend([delta_line_h, delta_start_h, handle_len, 1, 0]) # 1=variable
                
                last_start = handle_start

    return SemanticTokens(data=data)

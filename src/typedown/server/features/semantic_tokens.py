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
            # backticks=3, entity=6, colon=1
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

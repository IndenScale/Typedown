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
    Provide semantic tokens for references [[...]] with context awareness.
    - Inside Entity Blocks: Enforce STRICT pattern (L0/L1 identifiers only).
    - Outside (Free Text): Allow LOOSE pattern (Query strings).
    """
    try:
        doc = ls.workspace.get_text_document(params.text_document.uri)
        
        # Try to get in-memory content first (works in both browser and desktop)
        # The workspace maintains a cache of open documents
        if hasattr(ls.workspace, '_text_documents') and params.text_document.uri in ls.workspace._text_documents:
            # Get from in-memory cache
            text_content = ls.workspace._text_documents[params.text_document.uri].source
        else:
            # Fallback to doc.source (will read from disk on desktop, may fail in browser)
            text_content = doc.source
        
        lines = text_content.splitlines()
    except Exception as e:
        # Fallback: return empty tokens if we can't get document content
        print(f"ERROR: Failed to get document content for {params.text_document.uri}: {e}")
        return SemanticTokens(data=[])
    
    data = []
    last_line = 0
    last_start = 0
    
    # Context State
    in_entity_block = False
    
    # Patterns
    loose_ref_pattern = re.compile(r'\[\[(.*?)\]\]')
    strict_content_pattern = re.compile(r'^(?:sha256:[a-fA-F0-9]+|[a-zA-Z0-9_\.-]+)$')
    block_start_pattern = re.compile(r'^\s*```entity')
    block_end_pattern = re.compile(r'^\s*```$')

    for line_num, line in enumerate(lines):
        # 1. Update Context State
        if block_start_pattern.match(line):
            in_entity_block = True
            continue # Skip header line
        
        if in_entity_block and block_end_pattern.match(line):
            in_entity_block = False
            continue # Skip footer line

        # 2. Find References using wide net (Loose Pattern)
        # We find ALL [[...]] candidates first, then filter based on context.
        for match in loose_ref_pattern.finditer(line):
            ref_raw = match.group(1)
            ref_content = ref_raw.strip()
            
            if not ref_content:
                continue
            
            # 3. Apply Context-Specific Rules
            if in_entity_block:
                # STRICT RULE: Must match L0/L1 pattern
                if not strict_content_pattern.match(ref_content):
                    continue # Ignore invalid refs inside Entity Block (let them be plain text)
            
            # 4. Generate Token (If we passed the checks)
            # Calculate range for the content ONLY (exclude brackets [[ ]])
            # And handle potential whitespace padding if any (though strict refs usually don't have them)
            
            # Find start of striped content within the group
            start_offset = ref_raw.find(ref_content)
            start_char = match.start(1) + start_offset
            length = len(ref_content)
            
            token_type_idx = 1 # Default: variable
            
            # Resolve Type (if compiler available)
            if ls.compiler and ref_content in ls.compiler.symbol_table:
                entity = ls.compiler.symbol_table[ref_content]
                type_name = getattr(entity, 'class_name', '').lower()
                
                if 'character' in type_name or 'actor' in type_name:
                    token_type_idx = 0 # class
                elif 'item' in type_name or 'weapon' in type_name:
                    token_type_idx = 3 # struct
                elif 'loc' in type_name or 'map' in type_name:
                    token_type_idx = 4 # interface
            
            # Append Token
            delta_line = line_num - last_line
            if delta_line > 0:
                delta_start = start_char
            else:
                delta_start = start_char - last_start
                
            data.extend([delta_line, delta_start, length, token_type_idx, 0])
            
            last_line = line_num
            last_start = start_char

    return SemanticTokens(data=data)

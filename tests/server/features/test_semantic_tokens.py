import pytest
from unittest.mock import MagicMock
from lsprotocol.types import SemanticTokensParams, TextDocumentIdentifier
from typedown.server.features.semantic_tokens import semantic_tokens

class MockLS:
    def __init__(self):
        self.workspace = MagicMock()
        self.compiler = MagicMock()
        self.compiler.symbol_table = {}

def test_wiki_link_free_text():
    ls = MockLS()
    doc = MagicMock()
    # Test free text loose query
    doc.source = "Plain text [[foo bar]]"
    ls.workspace.get_text_document.return_value = doc
    
    params = SemanticTokensParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td")
    )
    
    result = semantic_tokens(ls, params)
    
    # "Plain text [[foo bar]]"
    # [[ is at 11
    # foo bar is at 13
    # length of "foo bar" is 7
    # Expected: [0, 13, 7, 1, 0] (tokenType 1=variable)
    assert result.data == [0, 13, 7, 1, 0]

def test_wiki_link_entity_block_valid():
    ls = MockLS()
    doc = MagicMock()
    # Valid strict ID in entity block
    doc.source = "```entity\n[[valid.id]]\n```"
    ls.workspace.get_text_document.return_value = doc
    
    params = SemanticTokensParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td")
    )
    
    result = semantic_tokens(ls, params)
    
    # Line 0: ```entity
    # Line 1: [[valid.id]]
    #   col start of [[ is 0
    #   col start of content "valid.id" is 2
    #   length 8
    # Match found.
    # Data: [1, 2, 8, 1, 0] (delta_line=1 from start)
    assert result.data == [1, 2, 8, 1, 0]

def test_wiki_link_entity_block_invalid():
    ls = MockLS()
    doc = MagicMock()
    # Invalid ID (spaces) in entity block
    doc.source = "```entity\n[[invalid id]]\n```"
    ls.workspace.get_text_document.return_value = doc
    
    params = SemanticTokensParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td")
    )
    
    result = semantic_tokens(ls, params)
    
    # Should be empty because strict pattern check fails
    assert result.data == []

def test_context_switching():
    ls = MockLS()
    doc = MagicMock()
    expected_source = """
[[free.1]]
```entity
[[strict.1]]
[[bad id]]
```
[[free.2]]
"""
    doc.source = expected_source.strip()
    ls.workspace.get_text_document.return_value = doc
    
    params = SemanticTokensParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td")
    )
    
    result = semantic_tokens(ls, params)
    
    # Line 0: [[free.1]] -> match "free.1" (at 2, len 6) -> [0, 2, 6, 1, 0]
    # Line 1: ```entity
    # Line 2: [[strict.1]] -> match "strict.1" (at 2, len 8) -> [2, 2, 8, 1, 0] (delta line 2)
    # Line 3: [[bad id]] -> STRICT FAIL -> No Token
    # Line 4: ```
    # Line 5: [[free.2]] -> match "free.2" (at 2, len 6) -> [3, 2, 6, 1, 0] (delta line 3 from line 2)
    
    assert result.data == [
        0, 2, 6, 1, 0,
        2, 2, 8, 1, 0,
        3, 2, 6, 1, 0
    ]

import pytest
from unittest.mock import MagicMock
from lsprotocol.types import SemanticTokensParams, TextDocumentIdentifier
from typedown.server.features.semantic_tokens import semantic_tokens

class MockLS:
    def __init__(self):
        self.workspace = MagicMock()

def test_semantic_tokens_entity_header():
    ls = MockLS()
    doc = MagicMock()
    # Line 0: No match
    # Line 1: Match at col 10 (3+6+1)
    doc.source = "Plain text\n```entity UserAccount"
    ls.workspace.get_text_document.return_value = doc
    
    params = SemanticTokensParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td")
    )
    
    result = semantic_tokens(ls, params)
    
    # data: [delta_line, delta_start, length, tokenType, tokenModifiers]
    # delta_line: 1 (from line 0 to line 1)
    # delta_start: 10 (col 10)
    # length: 11 ('UserAccount')
    # tokenType: 0 ('class')
    assert result.data == [1, 10, 11, 0, 0]

def test_semantic_tokens_multiple():
    ls = MockLS()
    doc = MagicMock()
    doc.source = "```entity U1\n```entity U2"
    ls.workspace.get_text_document.return_value = doc
    
    params = SemanticTokensParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td")
    )
    
    result = semantic_tokens(ls, params)
    
    # Header 1: [0, 10, 2, 0, 0]
    # Header 2: [1, 10, 2, 0, 0]
    assert result.data == [0, 10, 2, 0, 0, 1, 10, 2, 0, 0]

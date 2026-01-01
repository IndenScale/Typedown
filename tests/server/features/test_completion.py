import pytest
from unittest.mock import MagicMock
from lsprotocol.types import CompletionParams, TextDocumentIdentifier, Position
from typedown.server.features.completion import completions
from typedown.core.ast.blocks import EntityBlock
from typedown.core.ast.base import SourceLocation

class MockLS:
    def __init__(self):
        self.compiler = MagicMock()
        self.workspace = MagicMock()

def test_completion_snippets():
    ls = MockLS()
    # Mock document content: "See [[ "
    doc = MagicMock()
    doc.source = "See [["
    ls.workspace.get_text_document.return_value = doc
    
    params = CompletionParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td"),
        position=Position(line=0, character=6)
    )
    
    # Pre-populate compiler with some symbols
    ls.compiler.symbol_table = {
        "alice": EntityBlock(id="alice", class_name="User", raw_data={}, location=SourceLocation(file_path="t.td", line_start=0, line_end=0))
    }
    ls.compiler.documents = {}
    
    result = completions(ls, params)
    
    # Should include snippets like "entity:", "class:" and also "alice"
    labels = [item.label for item in result.items]
    assert "entity:" in labels
    assert "class:" in labels
    assert "alice" in labels

def test_completion_class_scope():
    ls = MockLS()
    doc = MagicMock()
    doc.source = "[[class:"
    ls.workspace.get_text_document.return_value = doc
    
    params = CompletionParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td"),
        position=Position(line=0, character=8)
    )
    
    ls.compiler.model_registry = {"UserAccount": MagicMock()}
    
    result = completions(ls, params)
    labels = [item.label for item in result.items]
    assert "UserAccount" in labels
    assert "alice" not in labels

import pytest
from unittest.mock import MagicMock
from lsprotocol.types import RenameParams, TextDocumentIdentifier, Position
from typedown.server.features.rename import rename
from pathlib import Path

class MockLS:
    def __init__(self):
        self.compiler = MagicMock()
        self.workspace = MagicMock()

def test_rename_entity():
    ls = MockLS()
    doc = MagicMock()
    doc.source = "I like [[alice]]."
    ls.workspace.get_text_document.return_value = doc
    
    params = RenameParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td"),
        position=Position(line=0, character=10), # over 'alice'
        new_name="alice_v2"
    )
    
    # Mock documents in compiler
    doc_path = Path("/abs/test.td")
    mock_doc = MagicMock()
    mock_doc.raw_content = "I like [[alice]]."
    ls.compiler.documents = {doc_path: mock_doc}
    ls.compiler.symbol_table = {"alice": MagicMock()}
    
    result = rename(ls, params)
    
    assert result is not None
    assert len(result.changes) == 1
    uri = doc_path.as_uri()
    assert uri in result.changes
    
    edit = result.changes[uri][0]
    assert edit.new_text == "alice_v2"
    # Range should point to 'alice'
    assert edit.range.start.character == 9 # "[[a" -> start of 'a'
    assert edit.range.end.character == 14

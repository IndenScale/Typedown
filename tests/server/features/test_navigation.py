import pytest
from unittest.mock import MagicMock
from lsprotocol.types import DefinitionParams, TextDocumentIdentifier, Position, ReferenceParams, ReferenceContext
from typedown.server.features.navigation import definition, references
from typedown.core.ast.blocks import EntityBlock
from typedown.core.ast.base import SourceLocation
from pathlib import Path

class MockLS:
    def __init__(self):
        self.compiler = MagicMock()
        self.workspace = MagicMock()
        self.show_message_log = MagicMock()
        self.lock = MagicMock()

def test_goto_definition():
    ls = MockLS()
    doc = MagicMock()
    doc.raw_content = "Check [[bob]]" # Used by _find_reference_at_position
    
    # Mock references in doc
    ref = MagicMock()
    ref.target = "bob"
    ref.identifier = "bob" # Str or Identifier object
    ref.location.line_start = 1
    ref.location.col_start = 6
    ref.location.col_end = 13
    doc.references = [ref]
    doc.entities = []
    
    ls.workspace.get_text_document.return_value = doc
    
    # Setup Compiler Documents
    test_uri = "file:///test.td"
    test_path = Path("/test.td")
    ls.compiler.documents = {test_path: doc}
    
    params = DefinitionParams(
        text_document=TextDocumentIdentifier(uri=test_uri),
        position=Position(line=0, character=9) # over 'bob'
    )
    
    bob_path = str(Path("/abs/path/bob.td"))
    entity = EntityBlock(id="bob", class_name="User", raw_data={}, location=SourceLocation(file_path=bob_path, line_start=5, line_end=10))
    ls.compiler.symbol_table = {"bob": entity}
    
    result = definition(ls, params)
    assert result is not None
    assert isinstance(result, list)
    # LSP is 0-indexed, so line 5 (1-indexed) becomes 4
    assert result[0].target_selection_range.start.line == 4
    assert result[0].target_uri.endswith("bob.td")

def test_find_references():
    ls = MockLS()
    doc = MagicMock()
    doc.raw_content = "[[alice]]"
    
    ref = MagicMock()
    ref.target = "alice"
    ref.identifier = "alice"
    ref.location.line_start = 1
    ref.location.col_start = 0
    ref.location.col_end = 9
    doc.references = [ref]
    doc.entities = []
    
    ls.workspace.get_text_document.return_value = doc
    
    test_uri = "file:///test.td"
    test_path = Path("/test.td")
    ls.compiler.documents = {test_path: doc}
    
    params = ReferenceParams(
        text_document=TextDocumentIdentifier(uri=test_uri),
        position=Position(line=0, character=5), # over 'alice'
        context=ReferenceContext(include_declaration=True)
    )
    
    # Mock reverse dependencies
    ls.compiler.dependency_graph = MagicMock() # Ensure it's not None
    ls.compiler.dependency_graph.reverse_adj = {"alice": {"bob", "charlie"}}
    
    bob_path = str(Path("/abs/bob.td"))
    charlie_path = str(Path("/abs/charlie.td"))
    
    bob = EntityBlock(id="bob", class_name="T", raw_data={}, location=SourceLocation(file_path=bob_path, line_start=1, line_end=2))
    charlie = EntityBlock(id="charlie", class_name="T", raw_data={}, location=SourceLocation(file_path=charlie_path, line_start=3, line_end=4))
    
    ls.compiler.symbol_table = {"alice": MagicMock(), "bob": bob, "charlie": charlie}
    
    result = references(ls, params)
    assert result is not None
    assert len(result) == 2
    uris = [loc.uri for loc in result]
    assert any("bob.td" in u for u in uris)
    assert any("charlie.td" in u for u in uris)

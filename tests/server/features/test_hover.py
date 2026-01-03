import pytest
from unittest.mock import MagicMock
from lsprotocol.types import HoverParams, TextDocumentIdentifier, Position
from typedown.server.features.hover import hover
from typedown.core.ast.blocks import EntityBlock
from typedown.core.ast.base import SourceLocation
from pydantic import BaseModel

class UserAccount(BaseModel):
    """A user account model."""
    name: str

class MockLS:
    def __init__(self):
        self.compiler = MagicMock()
        self.workspace = MagicMock()

def test_hover_entity_reference():
    ls = MockLS()
    doc = MagicMock()
    doc.source = "See [[alice]]"
    ls.workspace.get_text_document.return_value = doc
    
    params = HoverParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td"),
        position=Position(line=0, character=8) # over 'alice'
    )
    
    entity = EntityBlock(id="alice", class_name="UserAccount", raw_data={"name": "Alice"}, location=SourceLocation(file_path="t.td", line_start=0, line_end=0))
    ls.compiler.symbol_table = {"alice": entity}
    
    result = hover(ls, params)
    assert result is not None
    assert "**Handle**: `alice`" in result.contents
    assert "**System ID**: `alice`" in result.contents
    assert "**Type**: `UserAccount`" in result.contents

def test_hover_model_header():
    ls = MockLS()
    doc = MagicMock()
    doc.source = "```entity UserAccount"
    ls.workspace.get_text_document.return_value = doc
    
    params = HoverParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td"),
        position=Position(line=0, character=15) # over 'UserAccount'
    )
    
    ls.compiler.model_registry = {"UserAccount": UserAccount}
    
    result = hover(ls, params)
    assert result is not None
    assert "**Type**: `UserAccount`" in result.contents
    assert "A user account model" in result.contents
    assert "- `name` (Required)" in result.contents

from typedown.core.ast.blocks import EntityBlock, ModelBlock, SpecBlock
from typedown.core.ast.base import SourceLocation

def test_entity_block():
    loc = SourceLocation(file_path="test.td", line_start=0, line_end=0)
    entity = EntityBlock(id="alice", class_name="User", raw_data={"name": "Alice"}, location=loc)
    assert entity.id == "alice"
    assert entity.class_name == "User"
    assert entity.raw_data["name"] == "Alice"

def test_model_block():
    loc = SourceLocation(file_path="test.td", line_start=0, line_end=0)
    model = ModelBlock(id="User", code="class User(BaseModel): pass", location=loc)
    assert model.id == "User"
    assert "class User" in model.code

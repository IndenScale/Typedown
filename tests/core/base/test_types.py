import pytest
from typedown.core.base.types import Ref, ReferenceMeta
from typing import Annotated, get_origin, get_args

def test_ref_type_annotation():
    # Test Ref["User"] syntax
    MyRef = Ref["User"]
    
    assert get_origin(MyRef) is Annotated
    args = get_args(MyRef)
    assert args[0] is str
    
    # Check metadata
    meta = args[1]
    assert isinstance(meta, ReferenceMeta)
    assert meta.target_type == "User"

def test_ref_in_pydantic():
    from pydantic import BaseModel
    
    class MyModel(BaseModel):
        owner: Ref["UserAccount"]
        
    m = MyModel(owner="alice")
    assert m.owner == "alice"
    
    # Schema check
    schema = MyModel.model_json_schema()
    assert schema["properties"]["owner"]["type"] == "string"

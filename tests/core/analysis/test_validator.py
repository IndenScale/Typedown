import pytest
from pathlib import Path
from rich.console import Console
from typedown.core.analysis.validator import Validator
from typedown.core.ast import Document, EntityBlock, SourceLocation, Reference
from typedown.core.base.types import Ref # Annotated[str, ReferenceMeta]
from typedown.core.base.identifiers import Identifier
from pydantic import BaseModel

class UserAccount(BaseModel):
    name: str
    manager: Ref["UserAccount"] = None

def test_validator_topological_resolution():
    console = Console()
    validator = Validator(console)
    
    # doc1: alice depends on bob
    doc1 = Document(path=Path("doc1.td"), raw_content="")
    ref_bob = Reference(target="bob", identifier=Identifier.parse("bob"), location=SourceLocation(file_path="doc1.td", line_start=0, line_end=0))
    alice = EntityBlock(id="alice", class_name="UserAccount", raw_data={"name": "Alice", "manager": "[[bob]]"}, location=SourceLocation(file_path="doc1.td", line_start=0, line_end=0), references=[ref_bob])
    doc1.entities.append(alice)
    
    # doc2: bob
    doc2 = Document(path=Path("doc2.td"), raw_content="")
    bob = EntityBlock(id="bob", class_name="UserAccount", raw_data={"name": "Bob"}, location=SourceLocation(file_path="doc2.td", line_start=0, line_end=0))
    doc2.entities.append(bob)
    
    docs = {doc1.path: doc1, doc2.path: doc2}
    symbol_table = {"alice": alice, "bob": bob}
    model_registry = {"UserAccount": UserAccount}
    
    validator.validate(docs, symbol_table, model_registry)
    
    assert alice.resolved_data["manager"] == bob
    assert not validator.diagnostics

def test_validator_former_linkage():
    console = Console()
    validator = Validator(console)
    
    # alice_v1 (Simulate a Slug ID by using user-alice-v1)
    # Note: In real parsing, ID would be just "user-alice-v1".
    alice_v1 = EntityBlock(id="user-alice-v1", class_name="UserAccount", raw_data={"name": "Alice", "age": 30}, location=SourceLocation(file_path="v1.td", line_start=0, line_end=0))
    alice_v1.resolved_data = alice_v1.raw_data 
    
    # alice_v2 points to alice_v1 via former
    # Using L2 Global Identifier: [[user-alice-v1]]
    alice_v2 = EntityBlock(id="users/alice-v2", class_name="UserAccount", raw_data={"former": "[[user-alice-v1]]", "age": 31, "name": "Alice V2"}, location=SourceLocation(file_path="v2.td", line_start=0, line_end=0), former_ids=["[[user-alice-v1]]"])
    
    docs = {Path("v1.td"): Document(path=Path("v1.td"), raw_content=""), Path("v2.td"): Document(path=Path("v2.td"), raw_content="")}
    docs[Path("v1.td")].entities.append(alice_v1)
    docs[Path("v2.td")].entities.append(alice_v2)
    
    symbol_table = {"user-alice-v1": alice_v1, "users/alice-v2": alice_v2}
    
    validator.validate(docs, symbol_table, {})
    
    # Assert NO merging occurred (Pure Pointer)
    # The name should be exactly what's in v2, or None if not defined (but here we defined it)
    assert alice_v2.resolved_data["name"] == "Alice V2"
    assert alice_v2.resolved_data["age"] == 31
    # Check diagnostics is empty (valid global ID)
    assert not validator.diagnostics

def test_validator_former_invalid_identifier():
    """Test that using a Local Handle for 'former' raises an error."""
    console = Console()
    validator = Validator(console)
    
    # former points to local handle "alice-local"
    entity = EntityBlock(id="alice-next", class_name="UserAccount", raw_data={"former": "alice-local", "name": "Alice"}, location=SourceLocation(file_path="test.td", line_start=0, line_end=0), former_ids=["alice-local"])
    
    docs = {Path("test.td"): Document(path=Path("test.td"), raw_content="")}
    docs[Path("test.td")].entities.append(entity)
    
    symbol_table = {"alice-next": entity}
    
    validator.validate(docs, symbol_table, {})
    
    # Should have an error about target not found (Resolution Check)
    assert len(validator.diagnostics) == 1
    assert "target 'alice-local' not found" in validator.diagnostics[0].message
    # assert "Local Handle" in validator.diagnostics[0].message # No longer relevant


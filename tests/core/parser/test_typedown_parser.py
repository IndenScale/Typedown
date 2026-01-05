import pytest
from pathlib import Path
from typedown.core.parser.typedown_parser import TypedownParser
from typedown.core.ast import EntityBlock, ModelBlock, SpecBlock, ConfigBlock

def test_parse_model_block():
    parser = TypedownParser()
    content = """
```model:UserAccount
class UserAccount(BaseModel):
    name: str
    age: int
```
"""
    doc = parser.parse_text(content, "test.td")
    assert len(doc.models) == 1
    assert doc.models[0].id == "UserAccount"
    assert "class UserAccount(BaseModel):" in doc.models[0].code

def test_parse_entity_block():
    parser = TypedownParser()
    content = """
```entity UserAccount: alice
name: "Alice"
age: 30
```
"""
    doc = parser.parse_text(content, "test.td")
    assert len(doc.entities) == 1
    entity = doc.entities[0]
    assert entity.class_name == "UserAccount"
    assert entity.id == "alice"
    # assert entity.raw_data["id"] == "user-alice-v1" # Deprecated/Removed from body
    assert entity.raw_data["name"] == "Alice"

def test_parse_entity_block_with_hyphens():
    parser = TypedownParser()
    content = """
```entity ComplianceItem: REQ-PHY-01
content: "Must be sealed."
```
"""
    doc = parser.parse_text(content, "test.td")
    assert len(doc.entities) == 1
    entity = doc.entities[0]
    assert entity.class_name == "ComplianceItem"
    assert entity.id == "REQ-PHY-01"
    # assert entity.raw_data["id"] == "REQ-PHY-01"

def test_parse_config_block():
    parser = TypedownParser()
    content = """
```config:python id=my_config
import sys
```
"""
    doc = parser.parse_text(content, "test.td")
    assert len(doc.configs) == 1
    assert doc.configs[0].id == "my_config"

def test_parse_spec_block():
    parser = TypedownParser()
    content = """
```spec: check_adult
@target(type="UserAccount")
def check_adult(subject: UserAccount):
    assert subject.age >= 18
```
"""
    doc = parser.parse_text(content, "test.td")
    assert len(doc.specs) == 1
    spec = doc.specs[0]
    assert spec.id == "check_adult"
    # Target is parsed from code via decorators in L3, not info string
    # assert spec.target == "UserAccount"

def test_scan_references():
    parser = TypedownParser()
    content = """
Alice is talking to [[bob]].
See also [[users/charlie]].
"""
    doc = parser.parse_text(content, "test.td")
    assert len(doc.references) == 2
    assert doc.references[0].target == "bob"
    assert doc.references[1].target == "users/charlie"

def test_references_in_yaml():
    parser = TypedownParser()
    content = """
```entity Project: death_star
contributors:
  - [[vader]]
  - [[tarkin]]
```
"""
    doc = parser.parse_text(content, "test.td")
    # References are scanned from the raw code as well
    assert any(ref.target == "vader" for ref in doc.references)
    assert any(ref.target == "tarkin" for ref in doc.references)

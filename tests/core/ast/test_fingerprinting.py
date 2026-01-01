import pytest
from typedown.core.ast.blocks import EntityBlock, ModelBlock, SpecBlock, ConfigBlock
from typedown.core.ast.document import Document
from typedown.core.ast.base import SourceLocation
from pathlib import Path

def test_entity_block_hashing():
    loc = SourceLocation(file_path="test.td", line_start=1, line_end=5)
    
    e1 = EntityBlock(id="alice", class_name="User", raw_data={"age": 20, "name": "Alice"}, location=loc)
    e2 = EntityBlock(id="alice", class_name="User", raw_data={"name": "Alice", "age": 20}, location=loc)
    e3 = EntityBlock(id="bob", class_name="User", raw_data={"name": "Bob"}, location=loc)
    
    # Deterministic hash regardless of key order in raw_data
    assert e1.content_hash == e2.content_hash
    # Different ID leads to different hash
    assert e1.content_hash != e3.content_hash

def test_model_block_hashing():
    loc = SourceLocation(file_path="test.td", line_start=1, line_end=5)
    m1 = ModelBlock(id="User", code="class User: pass", location=loc)
    m2 = ModelBlock(id="User", code="class User: pass", location=loc)
    m3 = ModelBlock(id="User", code="class User: \n    pass", location=loc)
    
    assert m1.content_hash == m2.content_hash
    assert m1.content_hash != m3.content_hash

def test_document_merkle_hash():
    loc = SourceLocation(file_path="test.td", line_start=1, line_end=5)
    doc = Document(path=Path("test.td"))
    
    e1 = EntityBlock(id="alice", class_name="User", raw_data={"name": "Alice"}, location=loc)
    m1 = ModelBlock(id="User", code="class User: pass", location=loc)
    
    doc.entities.append(e1)
    doc.models.append(m1)
    
    hash1 = doc.content_hash
    
    # Changing a block should change document hash
    e1.raw_data["age"] = 30
    hash2 = doc.content_hash
    assert hash1 != hash2
    
    # Order of blocks shouldn't matter for Document.content_hash if we sort them (as implemented)
    doc2 = Document(path=Path("test2.td"))
    e2 = EntityBlock(id="bob", class_name="User", raw_data={"name": "Bob"}, location=loc)
    m2 = ModelBlock(id="User", code="class User: pass", location=loc)
    
    doc2.entities.append(e2)
    doc2.models.append(m2)
    h_doc2_a = doc2.content_hash
    
    doc3 = Document(path=Path("test3.td"))
    doc3.models.append(m2) # Different order
    doc3.entities.append(e2)
    h_doc2_b = doc3.content_hash
    
    assert h_doc2_a == h_doc2_b

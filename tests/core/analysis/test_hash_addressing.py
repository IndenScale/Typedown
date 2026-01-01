import pytest
from pathlib import Path
from typedown.core.ast.blocks import EntityBlock
from typedown.core.base.symbol_table import SymbolTable
from typedown.core.analysis.query import QueryEngine

def test_symbol_table_hash_registration():
    st = SymbolTable()
    entity = EntityBlock(
        id="alice",
        class_name="User",
        raw_data={"name": "Alice"}
    )
    # The content_hash is computed dynamically
    h = entity.content_hash
    st.add(entity, Path("app/users.td"))
    
    # Resolve by hash
    resolved = st.resolve(f"sha256:{h}")
    assert resolved is entity
    
    # Resolve by handle
    resolved_handle = st.resolve("alice", Path("app/users.td"))
    assert resolved_handle is entity

def test_query_engine_hash_priority():
    st = SymbolTable()
    entity = EntityBlock(
        id="alice",
        class_name="User",
        raw_data={"name": "Alice"}
    )
    h = entity.content_hash
    st.add(entity, Path("app/users.td"))
    
    # Query by hash
    results = QueryEngine.resolve_query(f"sha256:{h}", st)
    assert len(results) == 1
    assert results[0] is entity
    
def test_hash_resolution_in_evaluation():
    st = SymbolTable()
    alice = EntityBlock(id="alice", class_name="User", raw_data={"name": "Alice"})
    h = alice.content_hash
    st.add(alice, Path("app/users.td"))
    
    data = {
        "friend": f"[[sha256:{h}]]"
    }
    
    # evaluate_data uses QueryEngine.resolve_string -> resolve_query
    resolved = QueryEngine.evaluate_data(data, st)
    assert resolved["friend"] is alice

def test_hash_nested_resolution():
    st = SymbolTable()
    alice = EntityBlock(id="alice", class_name="User", raw_data={"profile": {"city": "Berlin"}})
    h = alice.content_hash
    st.add(alice, Path("app/users.td"))
    
    # Query: hash + field
    query = f"sha256:{h}.profile.city"
    results = QueryEngine.resolve_query(query, st)
    assert len(results) == 1
    assert results[0] == "Berlin"

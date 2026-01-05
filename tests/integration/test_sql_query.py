import pytest
from pathlib import Path
from typedown.core.base.symbol_table import SymbolTable
from typedown.core.ast import EntityBlock
from typedown.core.analysis.query import QueryEngine

def test_sql_query():
    # Setup
    st = SymbolTable()
    
    # Add User entities
    user1 = EntityBlock(
        id="alice",
        class_name="User",
        raw_data={"name": "Alice", "age": 30},
        resolved_data={"name": "Alice", "age": 30}
    )
    user2 = EntityBlock(
        id="bob",
        class_name="User",
        raw_data={"name": "Bob", "age": 25},
        resolved_data={"name": "Bob", "age": 25}
    )
    
    # Path is required for scope index but not for global index logic
    st.add(user1, Path("users/alice.td"))
    st.add(user2, Path("users/bob.td"))
    
    # Test SQL
    results = QueryEngine.execute_sql("SELECT * FROM User ORDER BY age DESC", st)
    
    assert len(results) == 2
    assert results[0]["name"] == "Alice"
    assert results[1]["name"] == "Bob"
    
    # Test Aggregation
    agg = QueryEngine.execute_sql("SELECT avg(age) as avg_age FROM User", st)
    assert agg[0]["avg_age"] == 27.5

def test_sql_query_json_handling():
    """Test that nested JSON data is handled correctly (as string or struct?)"""
    st = SymbolTable()
    
    item1 = EntityBlock(
        id="item1",
        class_name="Item",
        raw_data={"tags": ["a", "b"], "meta": {"owner": "alice"}},
        resolved_data={"tags": ["a", "b"], "meta": {"owner": "alice"}}
    )
    st.add(item1, Path("items.td"))
    
    # DuckDB JSON auto-detect should handle lists and structs
    # But when we dump to JSON file, they are just JSON types.
    # DuckDB `read_json_auto` creates STRUCT/LIST columns.
    
    results = QueryEngine.execute_sql("SELECT tags, meta FROM Item", st)
    assert len(results) == 1
    
    # DuckDB returns python objects for complex types (list/dict)
    assert results[0]["tags"] == ["a", "b"]
    assert results[0]["meta"] == {"owner": "alice"}

import pytest
from pathlib import Path
from typedown.core.analysis.query import QueryEngine, QueryError
from typedown.core.ast import EntityBlock, SourceLocation

class MockNode:
    def __init__(self, id, data=None):
        self.id = id
        self.raw_data = data or {}
        self.resolved_data = data or {}
        self.location = SourceLocation(file_path="test.td", line_start=0, line_end=0)

def test_query_engine_initialization():
    """Test QueryEngine can be initialized with symbol_table."""
    st = {"alice": MockNode("alice", {"name": "Alice"})}
    engine = QueryEngine(st)
    assert engine.symbol_table == st
    assert engine.root_dir is None
    assert engine.resources == {}
    assert engine._cache == {}

def test_query_engine_with_root_dir():
    """Test QueryEngine initialization with root_dir and resources."""
    st = {"alice": MockNode("alice")}
    root = Path("/test/project")
    resources = {"assets/image.png": {"path": Path("/test/project/assets/image.png")}}
    
    engine = QueryEngine(st, root_dir=root, resources=resources)
    assert engine.symbol_table == st
    assert engine.root_dir == root
    assert engine.resources == resources

def test_query_engine_clear_cache():
    """Test cache clearing functionality."""
    st = {"alice": MockNode("alice")}
    engine = QueryEngine(st)
    
    # Manually populate cache
    engine._cache["test"] = "value"
    assert "test" in engine._cache
    
    engine.clear_cache()
    assert engine._cache == {}

def test_resolve_symbol_path_simple():
    st = {"alice": MockNode("alice", {"name": "Alice", "age": 30})}
    engine = QueryEngine(st)
    result = engine._resolve_symbol_path("alice")
    assert result.id == "alice"

def test_resolve_symbol_path_nested():
    st = {"alice": MockNode("alice", {"name": "Alice", "profile": {"city": "Wonderland"}})}
    engine = QueryEngine(st)
    
    # Nested field
    assert engine._resolve_symbol_path("alice.profile.city") == "Wonderland"
    
    # Verify transparency for resolved_data
    assert engine._resolve_symbol_path("alice.name") == "Alice"

def test_resolve_symbol_path_index():
    st = {"project": MockNode("project", {"tags": ["a", "b", "c"]})}
    engine = QueryEngine(st)
    assert engine._resolve_symbol_path("project.tags[1]") == "b"

def test_resolve_symbol_path_star():
    data = {"name": "Alice", "age": 30}
    st = {"alice": MockNode("alice", data)}
    engine = QueryEngine(st)
    # "*" should return the whole data dict
    assert engine._resolve_symbol_path("alice.*") == data

def test_resolve_string_exact():
    st = {"v": 42}
    engine = QueryEngine(st)
    assert engine.resolve_string("[[v]]") == 42

def test_resolve_string_interpolation():
    st = {"name": "Alice"}
    engine = QueryEngine(st)
    assert engine.resolve_string("Hello [[name]]!", st) == "Hello Alice!"

def test_evaluate_data_recursive():
    st = {"age": 25, "city": "NYC"}
    data = {
        "user": "[[name]]",
        "info": {
            "age": "[[age]]",
            "loc": "[[city]]"
        },
        "tags": ["[[tag1]]", "fixed"]
    }
    symbol_table = {
        "name": "Bob",
        "age": 25,
        "city": "NYC",
        "tag1": "cool"
    }
    engine = QueryEngine(symbol_table)
    resolved = engine.evaluate_data(data)
    assert resolved["user"] == "Bob"
    assert resolved["info"]["age"] == 25
    assert resolved["info"]["loc"] == "NYC"
    assert resolved["tags"] == ["cool", "fixed"]

def test_query_engine_with_mock_symbol_table():
    """Test that QueryEngine can work with a mock symbol table for testing."""
    class MockSymbolTable:
        def __init__(self, data):
            self._data = data
        
        def resolve_handle(self, name, context_path=None):
            return self._data.get(name)
        
        def resolve_slug(self, path):
            return self._data.get(path)
        
        def resolve_hash(self, hash_value):
            for v in self._data.values():
                if hasattr(v, 'hash') and v.hash == hash_value:
                    return v
            return None
    
    alice = MockNode("alice", {"name": "Alice"})
    mock_st = MockSymbolTable({"alice": alice})
    
    engine = QueryEngine(mock_st)
    result = engine._resolve_symbol_path("alice")
    assert result == alice

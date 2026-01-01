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

def test_resolve_symbol_path_simple():
    st = {"alice": MockNode("alice", {"name": "Alice", "age": 30})}
    result = QueryEngine._resolve_symbol_path("alice", st)
    assert result.id == "alice"

def test_resolve_symbol_path_nested():
    st = {"alice": MockNode("alice", {"name": "Alice", "profile": {"city": "Wonderland"}})}
    
    # Nested field
    assert QueryEngine._resolve_symbol_path("alice.profile.city", st) == "Wonderland"
    
    # Verify transparency for resolved_data
    assert QueryEngine._resolve_symbol_path("alice.name", st) == "Alice"

def test_resolve_symbol_path_index():
    st = {"project": MockNode("project", {"tags": ["a", "b", "c"]})}
    assert QueryEngine._resolve_symbol_path("project.tags[1]", st) == "b"

def test_resolve_symbol_path_star():
    data = {"name": "Alice", "age": 30}
    st = {"alice": MockNode("alice", data)}
    # "*" should return the whole data dict
    assert QueryEngine._resolve_symbol_path("alice.*", st) == data

def test_resolve_string_exact():
    st = {"v": 42}
    assert QueryEngine.resolve_string("[[v]]", st) == 42

def test_resolve_string_interpolation():
    st = {"name": "Alice"}
    assert QueryEngine.resolve_string("Hello [[name]]!", st) == "Hello Alice!"

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
    resolved = QueryEngine.evaluate_data(data, symbol_table)
    assert resolved["user"] == "Bob"
    assert resolved["info"]["age"] == 25
    assert resolved["info"]["loc"] == "NYC"
    assert resolved["tags"] == ["cool", "fixed"]

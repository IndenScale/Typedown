import pytest
from pathlib import Path
from typedown.core.base.symbol_table import SymbolTable

class MockNode:
    def __init__(self, node_id):
        self.id = node_id

def test_global_resolution():
    st = SymbolTable()
    node = MockNode("infra/db-prod")
    st.add(node, Path("/project/config.td"))
    
    assert st.resolve("infra/db-prod", Path("/project/any.td")) == node
    assert st.resolve("infra/db-prod", Path("/project/sub/any.td")) == node

def test_scoped_handle_resolution():
    st = SymbolTable()
    
    # Root level handle
    root_node = MockNode("db")
    st.add(root_node, Path("/project/config.td"))
    
    # Subdir level handle (Shadowing)
    sub_node = MockNode("db")
    st.add(sub_node, Path("/project/sub/config.td"))
    
    # Resolve from root
    assert st.resolve("db", Path("/project/main.td")) == root_node
    
    # Resolve from sub (should see shadowed)
    assert st.resolve("db", Path("/project/sub/main.td")) == sub_node
    
    # Resolve from deep sub (should see nearest parent's shadow)
    assert st.resolve("db", Path("/project/sub/deep/main.td")) == sub_node

def test_handle_shadowing():
    st = SymbolTable()

    # Scope 1: /project/dir1/
    node1 = MockNode("alice")
    st.add(node1, Path("/project/dir1/data.td"))

    # Scope 2: /project/dir2/
    node2 = MockNode("alice")
    st.add(node2, Path("/project/dir2/data.td"))

    # Resolve 'alice' from dir1 -> node1
    assert st.resolve("alice", Path("/project/dir1/main.td")) == node1
    
    # Resolve 'alice' from dir2 -> node2
    assert st.resolve("alice", Path("/project/dir2/main.td")) == node2

def test_slug_global_access():
    st = SymbolTable()
    
    # Define global slug in a deep file
    global_node = MockNode("users/bob")
    st.add(global_node, Path("/project/deep/nested/file.td"))
    
    # Access from completely different path
    # "users/bob" is parsed as Slug, resolved via resolve_slug (global index)
    assert st.resolve("users/bob", Path("/project/other/main.td")) == global_node

def test_missing_handle_falls_back_to_global():
    st = SymbolTable()
    
    global_node = MockNode("global_id")
    st.add(global_node, Path("/project/global.td"))
    
    # Resolve from a path with NO local handles
    assert st.resolve("global_id", Path("/project/anywhere/else.td")) == global_node

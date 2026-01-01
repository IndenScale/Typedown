from typedown.core.ast.base import SourceLocation, Node

def test_source_location():
    loc = SourceLocation(file_path="test.td", line_start=1, line_end=5)
    assert loc.file_path == "test.td"
    assert loc.line_start == 1
    assert loc.line_end == 5

def test_node_id():
    node = Node(id="test-node")
    assert node.id == "test-node"

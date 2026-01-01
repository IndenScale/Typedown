from pathlib import Path
from typedown.core.ast.document import Document

def test_document_initialization():
    doc = Document(path=Path("test.td"), raw_content="# Hello")
    assert doc.path == Path("test.td")
    assert doc.raw_content == "# Hello"
    assert doc.entities == []
    assert doc.models == []

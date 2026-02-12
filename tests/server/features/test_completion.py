import pytest
from unittest.mock import MagicMock
from pathlib import Path

from typedown.server.services import CompletionService, CompletionContext
from typedown.core.ast.blocks import EntityBlock
from typedown.core.ast.base import SourceLocation


def test_completion_snippets():
    """Test generic [[ completion returns snippets and entities."""
    # Setup mock compiler
    compiler = MagicMock()
    compiler.symbol_table = {
        "alice": EntityBlock(
            id="alice",
            class_name="User",
            raw_data={},
            location=SourceLocation(file_path="t.td", line_start=0, line_end=0)
        )
    }
    compiler.documents = {}
    
    # Create service and context
    service = CompletionService(compiler)
    context = CompletionContext(
        file_path=Path("test.td"),
        content="See [[",
        line=0,
        character=6
    )
    
    # Execute
    result = service.complete(context)
    
    # Verify
    labels = [item.label for item in result.items]
    assert "entity:" in labels
    assert "class:" in labels
    assert "alice" in labels


def test_completion_class_scope():
    """Test [[class: scope returns only models."""
    # Setup mock compiler
    compiler = MagicMock()
    compiler.symbol_table = {
        "alice": EntityBlock(
            id="alice",
            class_name="User",
            raw_data={},
            location=SourceLocation(file_path="t.td", line_start=0, line_end=0)
        )
    }
    compiler.model_registry = {"UserAccount": MagicMock()}
    
    # Create service and context
    service = CompletionService(compiler)
    context = CompletionContext(
        file_path=Path("test.td"),
        content="[[class:",
        line=0,
        character=8
    )
    
    # Execute
    result = service.complete(context)
    
    # Verify
    labels = [item.label for item in result.items]
    assert "UserAccount" in labels
    assert "alice" not in labels


def test_completion_entity_scope():
    """Test [[entity: scope returns only entities."""
    # Setup mock compiler
    compiler = MagicMock()
    compiler.symbol_table = {
        "alice": EntityBlock(
            id="alice",
            class_name="User",
            raw_data={},
            location=SourceLocation(file_path="t.td", line_start=0, line_end=0)
        ),
        "bob": EntityBlock(
            id="bob",
            class_name="User",
            raw_data={},
            location=SourceLocation(file_path="t.td", line_start=1, line_end=1)
        )
    }
    compiler.model_registry = {"UserAccount": MagicMock()}
    
    # Create service and context
    service = CompletionService(compiler)
    context = CompletionContext(
        file_path=Path("test.td"),
        content="[[entity:",
        line=0,
        character=9
    )
    
    # Execute
    result = service.complete(context)
    
    # Verify
    labels = [item.label for item in result.items]
    assert "alice" in labels
    assert "bob" in labels
    # Model should not appear in entity scope
    assert "UserAccount" not in labels


def test_completion_header_scope():
    """Test [[header: scope returns headers from documents."""
    # Setup mock compiler
    compiler = MagicMock()
    compiler.symbol_table = {}
    
    # Mock document with headers
    mock_doc = MagicMock()
    mock_doc.headers = [
        {"title": "Introduction", "level": 1},
        {"title": "Getting Started", "level": 2},
    ]
    compiler.documents = {Path("test.td"): mock_doc}
    
    # Create service and context
    service = CompletionService(compiler)
    context = CompletionContext(
        file_path=Path("test.td"),
        content="[[header:",
        line=0,
        character=9
    )
    
    # Execute
    result = service.complete(context)
    
    # Verify
    labels = [item.label for item in result.items]
    assert "Introduction" in labels
    assert "Getting Started" in labels


def test_completion_with_files():
    """Test generic [[ completion includes files."""
    # Setup mock compiler
    compiler = MagicMock()
    compiler.symbol_table = {}
    compiler.documents = {
        Path("/project/doc1.td"): MagicMock(),
        Path("/project/doc2.td"): MagicMock(),
    }
    
    # Create service and context
    service = CompletionService(compiler)
    context = CompletionContext(
        file_path=Path("test.td"),
        content="[[",
        line=0,
        character=2
    )
    
    # Execute
    result = service.complete(context)
    
    # Verify
    labels = [item.label for item in result.items]
    assert "doc1.td" in labels
    assert "doc2.td" in labels
    assert "entity:" in labels
    assert "class:" in labels
    assert "header:" in labels


def test_completion_empty_line():
    """Test completion returns empty list when line doesn't have [[ trigger."""
    # Setup mock compiler
    compiler = MagicMock()
    compiler.symbol_table = {}
    compiler.documents = {}
    
    # Create service and context
    service = CompletionService(compiler)
    context = CompletionContext(
        file_path=Path("test.td"),
        content="Some regular text without trigger",
        line=0,
        character=35
    )
    
    # Execute
    result = service.complete(context)
    
    # Verify - should return empty list when no [[ pattern matches
    assert result == []


def test_completion_line_out_of_range():
    """Test completion returns empty list when line number is out of range."""
    # Setup mock compiler
    compiler = MagicMock()
    compiler.symbol_table = {}
    compiler.documents = {}
    
    # Create service and context
    service = CompletionService(compiler)
    context = CompletionContext(
        file_path=Path("test.td"),
        content="Single line",
        line=5,  # Out of range
        character=0
    )
    
    # Execute
    result = service.complete(context)
    
    # Verify
    assert result == []

import pytest
from pathlib import Path
from lsprotocol.types import DiagnosticSeverity, Position
from typedown.server.managers.diagnostics import to_lsp_diagnostic, uri_to_path
from typedown.core.base.errors import TypedownError
from typedown.core.ast.base import SourceLocation

def test_uri_to_path():
    # Test file URI conversion
    uri = "file:///project/data.td"
    path = uri_to_path(uri)
    assert path.suffix == ".td"
    assert "project" in str(path)

def test_to_lsp_diagnostic():
    loc = SourceLocation(file_path="test.td", line_start=10, line_end=10, col_start=5, col_end=15)
    err = TypedownError(message="Syntax Error", location=loc, severity="error")
    
    diag = to_lsp_diagnostic(err)
    
    assert diag.message == "Syntax Error"
    assert diag.severity == DiagnosticSeverity.Error
    # LSP is 0-indexed, so line 10 becomes 9
    assert diag.range.start.line == 9
    assert diag.range.start.character == 4
    assert diag.range.end.line == 9
    assert diag.range.end.character == 14

def test_to_lsp_diagnostic_no_location():
    err = TypedownError(message="Generic Error", severity="warning")
    diag = to_lsp_diagnostic(err)
    
    assert diag.message == "Generic Error"
    assert diag.severity == DiagnosticSeverity.Warning
    assert diag.range.start == Position(line=0, character=0)

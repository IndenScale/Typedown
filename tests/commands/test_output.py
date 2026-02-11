"""
Tests for CLI output handling module.
"""

import json
import pytest
from pathlib import Path
from io import StringIO

import typer
from rich.console import Console
from pydantic import BaseModel

from typedown.commands.output import (
    json_serializer,
    cli_result,
    cli_error,
    cli_success,
    cli_warning,
    output_result,
    exit_with_code,
)
from typedown.commands.context import CLIContext, cli_session


class DummyModel(BaseModel):
    """Dummy model for testing."""
    name: str
    value: int


class TestJsonSerializer:
    """Tests for json_serializer function."""
    
    def test_serialize_none(self):
        """Test serializing None."""
        assert json_serializer(None) is None
    
    def test_serialize_primitives(self):
        """Test serializing primitive types."""
        assert json_serializer("hello") == "hello"
        assert json_serializer(42) == 42
        assert json_serializer(3.14) == 3.14
        assert json_serializer(True) is True
        assert json_serializer(False) is False
    
    def test_serialize_dict(self):
        """Test serializing dictionaries."""
        data = {"a": 1, "b": "test", "c": None}
        result = json_serializer(data)
        assert result == {"a": 1, "b": "test", "c": None}
    
    def test_serialize_list(self):
        """Test serializing lists."""
        data = [1, "two", None, {"nested": True}]
        result = json_serializer(data)
        assert result == [1, "two", None, {"nested": True}]
    
    def test_serialize_path(self):
        """Test serializing Path objects."""
        path = Path("/tmp/test.txt")
        result = json_serializer(path)
        assert result == "/tmp/test.txt"
    
    def test_serialize_set(self):
        """Test serializing sets."""
        data = {1, 2, 3}
        result = json_serializer(data)
        assert sorted(result) == [1, 2, 3]
    
    def test_serialize_pydantic_model(self):
        """Test serializing Pydantic models."""
        model = DummyModel(name="test", value=42)
        result = json_serializer(model)
        assert result == {"name": "test", "value": 42}
    
    def test_serialize_pydantic_model_class(self):
        """Test serializing Pydantic model classes."""
        result = json_serializer(DummyModel)
        assert "properties" in result
        assert "name" in result["properties"]
    
    def test_serialize_nested(self):
        """Test serializing nested structures."""
        data = {
            "path": Path("/tmp"),
            "model": DummyModel(name="nested", value=100),
            "list": [Path("a"), Path("b")],
        }
        result = json_serializer(data)
        assert result["path"] == "/tmp"
        assert result["model"]["name"] == "nested"
        assert result["list"] == ["a", "b"]


class MockCLIContext:
    """Mock CLIContext for testing output functions."""
    
    def __init__(self, as_json=False):
        self.as_json = as_json
        self.display_console = Console(file=StringIO())


class TestCliResult:
    """Tests for cli_result function."""
    
    def test_cli_result_json_mode(self, capsys):
        """Test cli_result in JSON mode outputs JSON."""
        ctx = MockCLIContext(as_json=True)
        data = {"status": "ok", "count": 42}
        
        cli_result(ctx, data, exit_on_error=False)
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "ok"
        assert output["count"] == 42
    
    def test_cli_result_human_mode(self):
        """Test cli_result in human mode calls printer."""
        ctx = MockCLIContext(as_json=False)
        data = {"status": "ok"}
        called = False
        
        def printer(d):
            nonlocal called
            called = True
            assert d["status"] == "ok"
        
        cli_result(ctx, data, human_printer=printer, exit_on_error=False)
        assert called
    
    def test_cli_result_exit_on_error_true(self):
        """Test cli_result exits on error when exit_on_error=True."""
        ctx = MockCLIContext(as_json=False)
        
        with pytest.raises(typer.Exit) as exc_info:
            cli_result(ctx, {"passed": False}, exit_on_error=True, success_indicator=False)
        
        assert exc_info.value.exit_code == 1
    
    def test_cli_result_exit_on_error_false(self):
        """Test cli_result does not exit when exit_on_error=False."""
        ctx = MockCLIContext(as_json=False)
        
        # Should not raise
        cli_result(ctx, {"passed": False}, exit_on_error=False, success_indicator=False)


class TestCliError:
    """Tests for cli_error function."""
    
    def test_cli_error_json_mode(self, capsys):
        """Test cli_error in JSON mode."""
        ctx = MockCLIContext(as_json=True)
        
        with pytest.raises(typer.Exit):
            cli_error("Something went wrong", ctx, details={"code": 500})
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["error"] == "Something went wrong"
        assert output["code"] == 500
    
    def test_cli_error_human_mode(self):
        """Test cli_error in human mode."""
        ctx = MockCLIContext(as_json=False)
        
        with pytest.raises(typer.Exit):
            cli_error("Something went wrong", ctx)
        
        output = ctx.display_console.file.getvalue()
        assert "Error: Something went wrong" in output
    
    def test_cli_error_no_context(self, capsys):
        """Test cli_error without context (defaults to human)."""
        with pytest.raises(typer.Exit):
            cli_error("Simple error", raise_exit=True)
    
    def test_cli_error_no_raise(self):
        """Test cli_error with raise_exit=False."""
        ctx = MockCLIContext(as_json=False)
        
        # Should not raise
        cli_error("Error message", ctx, raise_exit=False)


class TestCliSuccess:
    """Tests for cli_success function."""
    
    def test_cli_success_json_mode(self, capsys):
        """Test cli_success in JSON mode."""
        ctx = MockCLIContext(as_json=True)
        
        cli_success(ctx, "Done", {"result": "success"})
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["result"] == "success"
    
    def test_cli_success_json_mode_default_data(self, capsys):
        """Test cli_success in JSON mode with default data."""
        ctx = MockCLIContext(as_json=True)
        
        cli_success(ctx, "Done")
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["success"] is True
    
    def test_cli_success_human_mode(self):
        """Test cli_success in human mode."""
        ctx = MockCLIContext(as_json=False)
        
        cli_success(ctx, "Operation completed")
        
        output = ctx.display_console.file.getvalue()
        assert "Operation completed" in output


class TestCliWarning:
    """Tests for cli_warning function."""
    
    def test_cli_warning_json_mode(self, capsys):
        """Test cli_warning in JSON mode produces no output."""
        ctx = MockCLIContext(as_json=True)
        
        cli_warning(ctx, "Deprecated feature")
        
        captured = capsys.readouterr()
        assert captured.out == ""
    
    def test_cli_warning_human_mode(self):
        """Test cli_warning in human mode."""
        ctx = MockCLIContext(as_json=False)
        
        cli_warning(ctx, "Deprecated feature")
        
        output = ctx.display_console.file.getvalue()
        assert "Warning: Deprecated feature" in output


class TestExitWithCode:
    """Tests for exit_with_code function."""
    
    def test_exit_with_code_success(self):
        """Test exit_with_code with success code."""
        with pytest.raises(typer.Exit) as exc_info:
            exit_with_code(0)
        assert exc_info.value.exit_code == 0
    
    def test_exit_with_code_error(self):
        """Test exit_with_code with error code."""
        with pytest.raises(typer.Exit) as exc_info:
            exit_with_code(2)
        assert exc_info.value.exit_code == 2


class TestOutputResult:
    """Tests for output_result function (legacy)."""
    
    def test_output_result_json(self, capsys):
        """Test output_result in JSON mode."""
        data = {"key": "value"}
        output_result(data, as_json=True)
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["key"] == "value"
    
    def test_output_result_human(self):
        """Test output_result in human mode."""
        data = {"key": "value"}
        called = False
        
        def printer(d):
            nonlocal called
            called = True
        
        output_result(data, as_json=False, console_printer=printer)
        assert called

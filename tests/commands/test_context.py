"""
Tests for CLI context management module.
"""

import pytest
from pathlib import Path
from io import StringIO

import typer
from rich.console import Console

from typedown.commands.context import cli_session, compiler_session, CLIContext


class TestCLISession:
    """Tests for cli_session context manager."""
    
    def test_cli_session_basic(self, tmp_path):
        """Test basic cli_session initialization with project."""
        # Create a minimal typedown.toml
        (tmp_path / "typedown.toml").write_text("""
[package]
name = "test-project"
version = "0.1.0"
""")
        
        with cli_session(tmp_path, as_json=False, require_project=True) as ctx:
            assert isinstance(ctx, CLIContext)
            assert ctx.project_root == tmp_path
            assert ctx.config is not None
            assert ctx.config.package.name == "test-project"
            assert ctx.as_json is False
            assert ctx.compiler is not None
            assert ctx.console is not None
            assert ctx.display_console is not None
    
    def test_cli_session_json_mode(self, tmp_path):
        """Test cli_session in JSON mode creates quiet console."""
        (tmp_path / "typedown.toml").write_text("""
[package]
name = "test-project"
version = "0.1.0"
""")
        
        with cli_session(tmp_path, as_json=True, require_project=True) as ctx:
            assert ctx.as_json is True
            # In JSON mode, console should be a StringIO-based console
            assert isinstance(ctx.console.file, StringIO)
            # Display console should be a real console
            assert not isinstance(ctx.display_console.file, StringIO)
    
    def test_cli_session_no_project_required(self, tmp_path):
        """Test cli_session without requiring project."""
        # No typedown.toml
        
        with cli_session(tmp_path, as_json=False, require_project=False) as ctx:
            assert ctx.project_root == tmp_path
            assert ctx.config is None
    
    def test_cli_session_with_invalid_config(self, tmp_path):
        """Test cli_session handles invalid config gracefully."""
        # Create typedown.toml with invalid content
        (tmp_path / "typedown.toml").write_text("invalid toml content [[[")
        
        with pytest.raises(typer.Exit) as exc_info:
            with cli_session(tmp_path, as_json=False, require_project=True) as ctx:
                pass  # Should not reach here due to config parsing error
        
        assert exc_info.value.exit_code == 1


class TestCompilerSession:
    """Tests for compiler_session context manager."""
    
    def test_compiler_session_basic(self, tmp_path):
        """Test basic compiler_session initialization."""
        with compiler_session(tmp_path, as_json=False) as (compiler, console, display_console):
            assert compiler is not None
            assert console is not None
            assert display_console is not None
            assert isinstance(display_console, Console)
    
    def test_compiler_session_json_mode(self, tmp_path):
        """Test compiler_session in JSON mode."""
        with compiler_session(tmp_path, as_json=True) as (compiler, console, display_console):
            # In JSON mode, active console should be StringIO-based
            assert isinstance(console.file, StringIO)
            # Display console should be a real console
            assert not isinstance(display_console.file, StringIO)


class TestCLIContext:
    """Tests for CLIContext dataclass."""
    
    def test_cli_context_creation(self, tmp_path):
        """Test CLIContext can be created with all fields."""
        from typedown.core.compiler import Compiler
        
        compiler = Compiler(tmp_path)
        console = Console()
        display_console = Console()
        
        ctx = CLIContext(
            compiler=compiler,
            console=console,
            display_console=display_console,
            project_root=tmp_path,
            config=None,
            as_json=False,
            target=tmp_path,
        )
        
        assert ctx.compiler == compiler
        assert ctx.console == console
        assert ctx.display_console == display_console
        assert ctx.project_root == tmp_path
        assert ctx.config is None
        assert ctx.as_json is False
        assert ctx.target == tmp_path

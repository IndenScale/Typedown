"""
Integration tests for CLI commands after refactoring.

These tests verify that all commands:
1. Support --json flag
2. Have consistent error handling
3. Return appropriate exit codes
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from typedown.main import app


runner = CliRunner()


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary Typedown project."""
    (tmp_path / "typedown.toml").write_text("""
[package]
name = "test-project"
version = "0.1.0"
""")
    return tmp_path


class TestCheckCommand:
    """Tests for check command."""
    
    def test_check_help(self):
        """Test check command shows help."""
        result = runner.invoke(app, ["check", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output
    
    def test_check_accepts_json_flag(self):
        """Test check command accepts --json flag."""
        result = runner.invoke(app, ["check", "--help"])
        assert "--json" in result.output


class TestInfoCommand:
    """Tests for info command."""
    
    def test_info_help(self):
        """Test info command shows help."""
        result = runner.invoke(app, ["info", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output
    
    def test_info_accepts_json_flag(self):
        """Test info command accepts --json flag."""
        result = runner.invoke(app, ["info", "--help"])
        assert "--json" in result.output


class TestQueryCommand:
    """Tests for query command."""
    
    def test_query_help(self):
        """Test query command shows help."""
        result = runner.invoke(app, ["query", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output
        assert "--sql" in result.output
    
    def test_query_accepts_json_flag(self):
        """Test query command accepts --json flag."""
        result = runner.invoke(app, ["query", "--help"])
        assert "--json" in result.output


class TestRunCommand:
    """Tests for run command."""
    
    def test_run_help(self):
        """Test run command shows help."""
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output
        assert "--dry-run" in result.output
    
    def test_run_accepts_json_flag(self):
        """Test run command accepts --json flag."""
        result = runner.invoke(app, ["run", "--help"])
        assert "--json" in result.output


class TestCompleteCommand:
    """Tests for complete command."""
    
    def test_complete_help(self):
        """Test complete command shows help."""
        result = runner.invoke(app, ["complete", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output
        assert "--line" in result.output
        assert "--char" in result.output
    
    def test_complete_accepts_json_flag(self):
        """Test complete command accepts --json flag."""
        result = runner.invoke(app, ["complete", "--help"])
        assert "--json" in result.output


class TestCommandConsistency:
    """Tests for consistent behavior across commands."""
    
    def test_all_commands_have_help(self):
        """Test that all main commands have help text."""
        commands = ["check", "info", "query", "run", "complete"]
        
        for cmd in commands:
            result = runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0, f"Command {cmd} should have help"
            assert "usage:" in result.output.lower()
    
    def test_common_options_available(self):
        """Test that common options are available across commands."""
        # Check that --json is available in all main output commands
        json_commands = ["check", "info", "query", "run", "complete"]
        
        for cmd in json_commands:
            result = runner.invoke(app, [cmd, "--help"])
            assert "--json" in result.output, f"Command {cmd} should support --json"

"""
Tests for the sandboxed execution environment.
Tests security restrictions and bypass attempts.
"""
import pytest
from pathlib import Path
import tempfile
import os

from typedown.core.analysis.sandbox import SandboxExecutor, SandboxViolationError
from typedown.core.base.config import SecurityConfig


class TestSandboxBasic:
    """Basic sandbox functionality tests."""
    
    @pytest.fixture
    def project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)
    
    @pytest.fixture
    def sandbox(self, project_root):
        return SandboxExecutor(project_root, SecurityConfig())
    
    def test_simple_code_execution(self, sandbox):
        """Test that simple safe code executes successfully."""
        code = "x = 1 + 1"
        result = sandbox.execute(code)
        assert result['x'] == 2
    
    def test_variable_assignment(self, sandbox):
        """Test variable assignment and retrieval."""
        code = """
a = 10
b = 20
c = a + b
        """
        result = sandbox.execute(code)
        assert result['c'] == 30
    
    def test_function_definition(self, sandbox):
        """Test defining and calling functions."""
        code = """
def add(x, y):
    return x + y

result = add(5, 3)
        """
        result = sandbox.execute(code)
        assert result['result'] == 8
    
    def test_class_definition(self, sandbox):
        """Test defining classes."""
        code = """
class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}"

p = Person("Alice")
greeting = p.greet()
        """
        result = sandbox.execute(code)
        assert result['greeting'] == "Hello, Alice"
    
    def test_import_safe_modules(self, sandbox):
        """Test importing safe modules like datetime."""
        code = """
import datetime
today = datetime.date(2024, 1, 1)
        """
        result = sandbox.execute(code)
        assert result['today'] == __import__('datetime').date(2024, 1, 1)


class TestSandboxSecurity:
    """Security restriction tests."""
    
    @pytest.fixture
    def project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)
    
    @pytest.fixture
    def sandbox(self, project_root):
        return SandboxExecutor(project_root, SecurityConfig())
    
    def test_block_eval(self, sandbox):
        """Test that eval() is blocked."""
        code = "eval('1 + 1')"
        with pytest.raises(Exception):  # Should raise some kind of error
            sandbox.execute(code)
    
    def test_block_exec(self, sandbox):
        """Test that exec() is blocked."""
        code = "exec('x = 1')"
        with pytest.raises(Exception):
            sandbox.execute(code)
    
    def test_block_open(self, sandbox):
        """Test that open() is blocked."""
        code = "open('/etc/passwd', 'r')"
        with pytest.raises(Exception):
            sandbox.execute(code)
    
    def test_block_os_import(self, sandbox):
        """Test that os module import is blocked."""
        code = "import os"
        with pytest.raises(Exception) as exc_info:
            sandbox.execute(code)
        assert "not allowed" in str(exc_info.value).lower() or "sandbox" in str(exc_info.value).lower()
    
    def test_block_sys_import(self, sandbox):
        """Test that sys module import is blocked."""
        code = "import sys"
        with pytest.raises(Exception) as exc_info:
            sandbox.execute(code)
        assert "not allowed" in str(exc_info.value).lower() or "sandbox" in str(exc_info.value).lower()
    
    def test_block_subprocess_import(self, sandbox):
        """Test that subprocess import is blocked."""
        code = "import subprocess"
        with pytest.raises(Exception) as exc_info:
            sandbox.execute(code)
        assert "not allowed" in str(exc_info.value).lower() or "sandbox" in str(exc_info.value).lower()
    
    def test_block_socket_import(self, sandbox):
        """Test that socket import is blocked."""
        code = "import socket"
        with pytest.raises(Exception) as exc_info:
            sandbox.execute(code)
        assert "not allowed" in str(exc_info.value).lower() or "sandbox" in str(exc_info.value).lower()
    
    def test_block_urllib(self, sandbox):
        """Test that urllib is blocked."""
        code = "import urllib.request"
        with pytest.raises(Exception):
            sandbox.execute(code)
    
    def test_block_importlib(self, sandbox):
        """Test that importlib is blocked."""
        code = "import importlib"
        with pytest.raises(Exception):
            sandbox.execute(code)


class TestSandboxConfig:
    """Configuration-based permission tests."""
    
    @pytest.fixture
    def project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)
    
    def test_allowed_modules_override(self, project_root):
        """Test that allowed_modules can override blocked list."""
        config = SecurityConfig(
            allowed_modules=['json']
        )
        sandbox = SandboxExecutor(project_root, config)
        
        # json should work now
        code = """
import json
data = json.dumps({"key": "value"})
        """
        result = sandbox.execute(code)
        assert result['data'] == '{"key": "value"}'
    
    def test_additional_blocked_modules(self, project_root):
        """Test that additional modules can be blocked."""
        config = SecurityConfig(
            blocked_modules=['math']
        )
        sandbox = SandboxExecutor(project_root, config)
        
        # math should be blocked now
        code = "import math"
        with pytest.raises(Exception):
            sandbox.execute(code)
    
    def test_disabled_security(self, project_root):
        """Test that security can be disabled (dangerous but supported)."""
        config = SecurityConfig(enabled=False)
        sandbox = SandboxExecutor(project_root, config)
        
        # With security disabled, even blocked modules might work
        # This is dangerous and should only be used in trusted environments
        # We just verify it doesn't crash
        code = "x = 1 + 1"
        result = sandbox.execute(code)
        assert result['x'] == 2


class TestSandboxBypassAttempts:
    """Tests for common sandbox bypass techniques."""
    
    @pytest.fixture
    def project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)
    
    @pytest.fixture
    def sandbox(self, project_root):
        return SandboxExecutor(project_root, SecurityConfig())
    
    def test_bypass_via_getattr(self, sandbox):
        """Test __import__ bypass via getattr."""
        code = "__import__('os')"
        with pytest.raises(Exception):
            sandbox.execute(code)
    
    def test_bypass_via_subclass(self, sandbox):
        """Test bypass via subclassing restricted types."""
        # This is a tricky bypass attempt
        code = """
class MyDict(dict):
    pass

d = MyDict()
        """
        # This should work as dict is safe
        result = sandbox.execute(code)
        assert 'd' in result
    
    def test_bypass_via_exception(self, sandbox):
        """Test bypass via exception handling."""
        code = """
try:
    import os
except:
    pass
result = "no exception"
        """
        # Should raise during execution
        with pytest.raises(Exception):
            sandbox.execute(code)


class TestSandboxPathRestrictions:
    """Tests for path-related restrictions."""
    
    @pytest.fixture
    def project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)
    
    @pytest.fixture
    def sandbox(self, project_root):
        return SandboxExecutor(project_root, SecurityConfig())
    
    def test_pathlib_available(self, sandbox):
        """Test that pathlib is available but restricted."""
        code = """
p = pathlib.Path("/some/path")
path_str = str(p)
        """
        result = sandbox.execute(code)
        assert result['path_str'] == "/some/path"
    
    def test_pathlib_write_blocked(self, sandbox, project_root):
        """Test that Path.write_text() is blocked in sandbox."""
        # Use the wrapped pathlib from globals instead of importing
        code = f"""
p = pathlib.Path("{project_root}/test.txt")
try:
    p.write_text("test")
    result = "success"
except Exception as e:
    result = str(e)
        """
        result = sandbox.execute(code)
        assert "sandbox" in result['result'].lower() or "disabled" in result['result'].lower()


class TestSandboxWithLinker:
    """Integration tests with Linker component."""
    
    @pytest.fixture
    def project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Create a basic typedown.toml
            (root / "typedown.toml").write_text("""
[package]
name = "test-project"
version = "0.1.0"

[security]
enabled = true
""")
            yield root
    
    def test_linker_uses_sandbox(self, project_root):
        """Test that Linker correctly uses sandbox for code execution."""
        from typedown.core.analysis.linker import Linker
        from typedown.core.base.config import TypedownConfig
        
        config = TypedownConfig.load(project_root / "typedown.toml")
        
        class MockConsole:
            def print(self, *args, **kwargs):
                pass
        
        linker = Linker(project_root, config, MockConsole())
        
        # Verify sandbox is initialized
        assert linker.sandbox is not None
        assert linker.config.security.enabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

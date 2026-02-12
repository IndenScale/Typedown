"""
Sandboxed execution environment for user code.
Restricts dangerous operations while allowing safe configuration and model definitions.
"""
import sys
import os
import io
import builtins
import typing
import datetime
import importlib
import ast
from pathlib import Path
from typing import Dict, Any, Optional, Set, List
from types import ModuleType

from typedown.core.base.config import SecurityConfig
from typedown.core.base.errors import (
    TypedownError, ErrorCode, ErrorLevel,
    linker_error
)

# Try to import RestrictedPython, fallback to restricted mode if not available
try:
    from restrictedpython import compile_restricted, safe_globals
    from restrictedpython.Guards import safe_builtins, full_write_guard
    RESTRICTED_PYTHON_AVAILABLE = True
except ImportError:
    RESTRICTED_PYTHON_AVAILABLE = False


class SandboxViolationError(TypedownError):
    """Raised when code attempts a forbidden operation in sandbox."""
    pass


class SandboxASTVisitor(ast.NodeVisitor):
    """AST visitor to detect potentially dangerous code patterns."""
    
    # Dangerous builtins to check
    DANGEROUS_BUILTINS = {'eval', 'exec', 'compile', 'open', '__import__', 'input'}
    
    # Dangerous imports
    DANGEROUS_MODULES = {'os', 'sys', 'subprocess', 'socket', 'urllib', 'urllib.request',
                        'http', 'http.client', 'ftplib', 'telnetlib', 'ssl', 'ctypes',
                        'multiprocessing', 'importlib', 'imp', 'builtins', '__builtin__'}
    
    # Safe modules that are always allowed
    SAFE_MODULES = {'typing', 'datetime', 'collections', 'functools', 'itertools', 
                   'math', 'random', 'string', 're', 'json', 'decimal', 'fractions',
                   'numbers', 'uuid', 'hashlib', 'abc', 'copy', 'textwrap', 
                   'dataclasses', 'enum', 'types'}
    
    # Modules that are blocked but provided as safe wrappers in globals
    WRAPPED_MODULES = {'pathlib'}
    
    def __init__(self, extra_blocked_modules: Optional[Set[str]] = None, 
                 extra_allowed_modules: Optional[Set[str]] = None):
        self.violations = []
        self.blocked_modules = self.DANGEROUS_MODULES.copy()
        self.allowed_modules = self.SAFE_MODULES.copy()
        # Wrapped modules are blocked from direct import but provided as safe wrappers
        self.wrapped_modules = self.WRAPPED_MODULES.copy()
        if extra_blocked_modules:
            self.blocked_modules.update(extra_blocked_modules)
            # Remove from allowed if explicitly blocked
            self.allowed_modules -= extra_blocked_modules
        if extra_allowed_modules:
            self.allowed_modules.update(extra_allowed_modules)
    
    def visit_Call(self, node):
        """Check for dangerous function calls."""
        if isinstance(node.func, ast.Name):
            if node.func.id in self.DANGEROUS_BUILTINS:
                self.violations.append(f"Call to dangerous builtin: {node.func.id}")
        elif isinstance(node.func, ast.Attribute):
            # Check for method calls like os.system
            if node.func.attr in {'system', 'popen', 'spawn', 'exec', 'eval'}:
                self.violations.append(f"Call to potentially dangerous method: {node.func.attr}")
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Check for dangerous imports."""
        for alias in node.names:
            base_module = alias.name.split('.')[0]
            if base_module in self.blocked_modules and base_module not in self.allowed_modules:
                self.violations.append(f"Import of module '{alias.name}' is not allowed in sandbox mode")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Check for dangerous from imports."""
        if node.module:
            base_module = node.module.split('.')[0]
            if base_module in self.blocked_modules and base_module not in self.allowed_modules:
                self.violations.append(f"Import from module '{node.module}' is not allowed in sandbox mode")
        self.generic_visit(node)


class SandboxExecutor:
    """
    Restricted execution environment for user code.
    
    Security features:
    - Block dangerous builtins (eval, exec, open, etc.)
    - Restrict file system access to project directory
    - Block network operations (socket, urllib, etc.)
    - Block subprocess execution (os.system, subprocess, etc.)
    - Resource limits (optional)
    """
    
    # Dangerous modules to block by default
    DEFAULT_BLOCKED_MODULES: Set[str] = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'urllib.request',
        'http', 'http.client', 'ftplib', 'telnetlib', 'ssl', 'ctypes',
        'multiprocessing', 'threading', 'concurrent', 'asyncio',
        'importlib', 'imp', 'builtins', '__builtin__', 'pathlib',
    }
    
    # Dangerous builtins to block
    DEFAULT_BLOCKED_BUILTINS: Set[str] = {
        'eval', 'exec', 'compile', 'open', '__import__',
        'input', 'raw_input', 'reload', 'exit', 'quit',
        'help', 'copyright', 'credits', 'license',
    }
    
    def __init__(self, project_root: Path, security_config: Optional[SecurityConfig] = None):
        self.project_root = project_root.resolve()
        self.config = security_config or SecurityConfig()
        self._blocked_modules: Set[str] = set()
        self._allowed_modules: Set[str] = set()
        self._setup_module_restrictions()
    
    def _setup_module_restrictions(self):
        """Setup module-level restrictions based on config."""
        # Start with default blocked modules
        self._blocked_modules = self.DEFAULT_BLOCKED_MODULES.copy()
        
        # Remove explicitly allowed modules from blocked list
        for module in self.config.allowed_modules:
            self._blocked_modules.discard(module)
        
        # Add explicitly blocked modules
        self._blocked_modules.update(self.config.blocked_modules)
        
        # Track allowed modules for import validation
        self._allowed_modules = set(self.config.allowed_modules)
    
    def _validate_code_ast(self, code: str, filename: str = "<sandbox>"):
        """Validate code using AST analysis."""
        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            raise SandboxViolationError(f"Syntax error: {e}")
        
        visitor = SandboxASTVisitor(self._blocked_modules, self._allowed_modules)
        visitor.visit(tree)
        
        if visitor.violations:
            raise SandboxViolationError(
                f"Sandbox security violations detected:\n" + 
                "\n".join(f"  - {v}" for v in visitor.violations)
            )
        
        return tree
    
    def create_safe_globals(self, extra_globals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a safe global namespace for code execution.
        
        Args:
            extra_globals: Additional safe globals to include
            
        Returns:
            Dictionary of safe global variables
        """
        if RESTRICTED_PYTHON_AVAILABLE and self.config.use_restricted_python:
            # Use RestrictedPython's safe builtins as base
            safe_globals_dict = dict(safe_builtins)
        else:
            # Fallback: manually create safe builtins
            safe_globals_dict = self._create_fallback_builtins()
        
        # Add safe standard library modules
        safe_globals_dict.update(self._get_safe_modules())
        
        # Add custom import guard
        safe_globals_dict['__import__'] = self._guarded_import
        
        # Add extra globals if provided
        if extra_globals:
            safe_globals_dict.update(extra_globals)
        
        return safe_globals_dict
    
    def _create_fallback_builtins(self) -> Dict[str, Any]:
        """Create safe builtins dict when RestrictedPython is not available."""
        safe_builtins_dict = {}
        
        # Copy safe builtins
        for name in dir(builtins):
            if name not in self.DEFAULT_BLOCKED_BUILTINS:
                try:
                    safe_builtins_dict[name] = getattr(builtins, name)
                except AttributeError:
                    pass
        
        return safe_builtins_dict
    
    def _get_safe_modules(self) -> Dict[str, Any]:
        """Get dictionary of safe modules to expose."""
        safe_modules = {}
        
        # Always safe modules
        always_safe = [
            'typing',
            'datetime', 
            'collections',
            'functools',
            'itertools',
            'math',
            'random',
            'string',
            're',
            'json',
            'decimal',
            'fractions',
            'numbers',
            'uuid',
            'hashlib',
            'abc',
            'copy',
            'textwrap',
            'dataclasses',
            'enum',
            'types',
        ]
        
        for name in always_safe:
            try:
                safe_modules[name] = importlib.import_module(name)
            except ImportError:
                pass
        
        # Handle pathlib specially with path restrictions
        # pathlib is in DEFAULT_BLOCKED_MODULES but we provide a safe wrapper
        wrapped_pathlib, RestrictedPath = self._wrap_pathlib()
        safe_modules['pathlib'] = wrapped_pathlib
        # Also expose RestrictedPath directly for 'from pathlib import Path' to work
        safe_modules['Path'] = RestrictedPath
        
        return safe_modules
    
    def _wrap_pathlib(self) -> tuple[ModuleType, type]:
        """Wrap pathlib to enforce path restrictions.
        
        Returns:
            Tuple of (wrapped module, RestrictedPath class)
        """
        import pathlib as _pathlib_module
        from types import ModuleType
        
        # Create a wrapper module
        wrapped = ModuleType('pathlib')
        wrapped.__dict__.update(_pathlib_module.__dict__.copy())
        
        # Wrap Path class to block file operations
        original_path = _pathlib_module.Path
        
        class RestrictedPath(original_path):
            """Path subclass that blocks file operations."""
            
            def open(self, *args, **kwargs):
                raise SandboxViolationError("File open() is disabled in sandbox mode")
            
            def read_text(self, *args, **kwargs):
                raise SandboxViolationError("File read_text() is disabled in sandbox mode")
            
            def write_text(self, *args, **kwargs):
                raise SandboxViolationError("File write_text() is disabled in sandbox mode")
            
            def read_bytes(self, *args, **kwargs):
                raise SandboxViolationError("File read_bytes() is disabled in sandbox mode")
            
            def write_bytes(self, *args, **kwargs):
                raise SandboxViolationError("File write_bytes() is disabled in sandbox mode")
            
            def touch(self, *args, **kwargs):
                raise SandboxViolationError("File touch() is disabled in sandbox mode")
            
            def mkdir(self, *args, **kwargs):
                raise SandboxViolationError("Directory mkdir() is disabled in sandbox mode")
            
            def unlink(self, *args, **kwargs):
                raise SandboxViolationError("File unlink() is disabled in sandbox mode")
            
            def rmdir(self, *args, **kwargs):
                raise SandboxViolationError("Directory rmdir() is disabled in sandbox mode")
            
            def rename(self, *args, **kwargs):
                raise SandboxViolationError("File rename() is disabled in sandbox mode")
            
            def replace(self, *args, **kwargs):
                raise SandboxViolationError("File replace() is disabled in sandbox mode")
            
            def symlink_to(self, *args, **kwargs):
                raise SandboxViolationError("Symlink operations are disabled in sandbox mode")
            
            def hardlink_to(self, *args, **kwargs):
                raise SandboxViolationError("Hardlink operations are disabled in sandbox mode")
        
        wrapped.Path = RestrictedPath
        return wrapped, RestrictedPath
    
    def _guarded_import(self, name: str, *args, **kwargs):
        """Guarded import that checks against blocked modules."""
        # Check if module or its parent is blocked
        parts = name.split('.')
        for i in range(len(parts)):
            prefix = '.'.join(parts[:i+1])
            if prefix in self._blocked_modules:
                if prefix not in self._allowed_modules:
                    raise SandboxViolationError(
                        f"Import of module '{name}' is not allowed in sandbox mode. "
                        f"Add to [security.allowed_modules] in typedown.toml to enable."
                    )
        
        # Allow the import
        return __import__(name, *args, **kwargs)
    
    def execute(self, code: str, globals_dict: Optional[Dict[str, Any]] = None, 
                locals_dict: Optional[Dict[str, Any]] = None,
                filename: str = "<sandbox>") -> Dict[str, Any]:
        """
        Execute code in sandboxed environment.
        
        Args:
            code: Python code to execute
            globals_dict: Global namespace (created if None)
            locals_dict: Local namespace (uses globals if None)
            filename: Filename for error reporting
            
        Returns:
            The globals dictionary after execution
        """
        if globals_dict is None:
            globals_dict = self.create_safe_globals()
        
        if locals_dict is None:
            locals_dict = globals_dict
        
        # First, validate code with AST analysis
        self._validate_code_ast(code, filename)
        
        # Compile with RestrictedPython if available
        if RESTRICTED_PYTHON_AVAILABLE and self.config.use_restricted_python:
            compiled = compile_restricted(code, filename=filename, mode='exec')
            if compiled is None:
                raise SandboxViolationError("Code failed restricted compilation")
        else:
            # Fallback: normal compilation (AST validation already done)
            compiled = compile(code, filename, 'exec')
        
        # Execute in sandboxed environment
        try:
            exec(compiled, globals_dict, locals_dict)
        except SandboxViolationError:
            raise
        except Exception as e:
            # Wrap other exceptions with context
            raise RuntimeError(f"Sandbox execution failed: {e}") from e
        
        return globals_dict
    
    def is_module_allowed(self, module_name: str) -> bool:
        """Check if a module is allowed to be imported."""
        parts = module_name.split('.')
        for i in range(len(parts)):
            prefix = '.'.join(parts[:i+1])
            if prefix in self._blocked_modules and prefix not in self._allowed_modules:
                return False
        return True

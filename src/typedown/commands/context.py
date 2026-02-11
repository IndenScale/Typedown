"""
CLI context management - Shared tools for command initialization and session handling.

This module provides a unified context manager for CLI commands, handling:
- Compiler initialization with consistent console handling
- JSON/Console output mode switching
- Standardized error handling and exit codes
"""

from contextlib import contextmanager
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Generator, Optional, Union

import typer
from rich.console import Console

from typedown.core.compiler import Compiler
from typedown.core.base.utils import find_project_root
from typedown.core.base.config import TypedownConfig


@dataclass
class CLIContext:
    """Container for CLI session context."""
    
    compiler: Compiler
    """Initialized compiler instance."""
    
    console: Console
    """Console for human-readable output (may be quiet mode for JSON)."""
    
    display_console: Console
    """Console always available for display output (not redirected)."""
    
    project_root: Path
    """Resolved project root path."""
    
    config: Optional[TypedownConfig]
    """Loaded project configuration (None if not found)."""
    
    as_json: bool
    """Whether JSON output mode is enabled."""
    
    target: Path
    """Target path (file or directory) for the command."""


@contextmanager
def cli_session(
    target: Path = Path("."),
    as_json: bool = False,
    script: Optional[str] = None,
    require_project: bool = True,
    console: Optional[Console] = None,
) -> Generator[CLIContext, None, None]:
    """
    Context manager for CLI command sessions.
    
    Provides unified initialization of Compiler and Console with proper
    handling for JSON output mode.
    
    Args:
        target: Target path (file or directory), defaults to current directory
        as_json: Whether to enable JSON output mode (redirects console output)
        script: Optional script name to use for compiler configuration
        require_project: Whether to require a valid project root
        console: Optional external console to use (otherwise creates one)
        
    Yields:
        CLIContext: Initialized context with compiler, consoles, and config
        
    Raises:
        typer.Exit: If project root is required but not found (exit code 1)
        
    Example:
        @app.command()
        def my_command(
            path: Path = typer.Argument(Path(".")),
            as_json: bool = typer.Option(False, "--json"),
        ):
            with cli_session(path, as_json=as_json) as ctx:
                result = ctx.compiler.lint()
                cli_result(ctx, {"passed": result}, lambda d: console.print("OK" if d["passed"] else "Failed"))
    """
    # Always create a display console for human output
    display_console = Console()
    
    # For JSON mode, create a quiet console that captures output
    if as_json:
        quiet_console = Console(file=StringIO(), stderr=False)
        compiler_console = quiet_console
    else:
        quiet_console = None
        compiler_console = console if console else display_console
    
    # Resolve project root if required
    project_root = None
    config = None
    
    if require_project:
        try:
            project_root = find_project_root(target.resolve())
        except Exception:
            if as_json:
                from typedown.commands.output import cli_error
                cli_error("Not a Typedown project", exit_code=1)
            else:
                display_console.print(f"[red]Error: Could not find typedown.toml in ancestors of {target}[/red]")
            raise typer.Exit(code=1)
        
        # Load config if project root found
        try:
            config_path = project_root / "typedown.toml"
            config = TypedownConfig.load(config_path)
        except Exception as e:
            if as_json:
                from typedown.commands.output import cli_error
                cli_error(f"Failed to load config: {e}", exit_code=1)
            else:
                display_console.print(f"[red]Error loading config: {e}[/red]")
            raise typer.Exit(code=1)
    else:
        # Use target as project root if not requiring project
        project_root = target.resolve()
    
    # Initialize compiler with appropriate console
    compiler = Compiler(target, console=compiler_console)
    
    yield CLIContext(
        compiler=compiler,
        console=compiler_console,
        display_console=display_console,
        project_root=project_root,
        config=config,
        as_json=as_json,
        target=target,
    )


@contextmanager
def compiler_session(
    target: Path = Path("."),
    as_json: bool = False,
    console: Optional[Console] = None,
) -> Generator[tuple[Compiler, Console, Console], None, None]:
    """
    Simplified context manager that yields (compiler, console, display_console).
    
    This is a lower-level alternative to cli_session() for commands that don't
    need project root/config resolution.
    
    Args:
        target: Target path (file or directory)
        as_json: Whether to enable JSON output mode
        console: Optional external console to use
        
    Yields:
        Tuple of (compiler, active_console, display_console)
        
    Example:
        with compiler_session(path, as_json) as (compiler, console, display):
            compiler.lint()
    """
    display_console = Console()
    
    if as_json:
        active_console = Console(file=StringIO(), stderr=False)
    else:
        active_console = console if console else display_console
    
    compiler = Compiler(target, console=active_console)
    
    yield compiler, active_console, display_console

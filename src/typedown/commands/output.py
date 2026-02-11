"""
CLI output handling - Unified output formatting and error handling.

This module provides standardized functions for:
- JSON and human-readable output
- Error handling with consistent formatting
- Exit code management
"""

import json
import sys
from pathlib import Path
from typing import Any, Callable, Optional, Union

import typer
from pydantic import BaseModel
from rich.console import Console

from typedown.core.base.errors import TypedownError
from typedown.commands.context import CLIContext


def json_serializer(obj: Any) -> Any:
    """
    JSON serializer for objects not serializable by default json code.
    
    Handles:
    - Path objects (converted to strings)
    - TypedownError objects (converted to dicts)
    - Pydantic models (converted to dicts)
    - Sets (converted to lists)
    - Dataclasses (converted to dicts)
    - Attrs classes (converted to dicts)
    - Objects with `resolved_data` or `to_dict` methods
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: json_serializer(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_serializer(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, TypedownError):
        loc = None
        if obj.location:
            loc = {
                "file_path": str(getattr(obj.location, "file_path", "")),
                "line_start": getattr(obj.location, "line_start", 0),
                "col_start": getattr(obj.location, "col_start", 0),
                "line_end": getattr(obj.location, "line_end", 0),
                "col_end": getattr(obj.location, "col_end", 0),
            }
        return {
            "severity": obj.severity,
            "message": obj.message,
            "location": loc
        }
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if hasattr(obj, "resolved_data"):
        return json_serializer(obj.resolved_data)
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    # Handle Sets
    if isinstance(obj, set):
        return list(obj)
    # Handle Classes (Pydantic Models)
    if isinstance(obj, type) and issubclass(obj, BaseModel):
        return obj.model_json_schema()
    
    import dataclasses
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    
    try:
        import attrs
        if attrs.has(obj):
            return attrs.asdict(obj)
    except ImportError:
        pass

    return str(obj)


def cli_result(
    ctx: CLIContext,
    data: Any,
    human_printer: Optional[Callable[[Any], None]] = None,
    exit_on_error: bool = True,
    success_indicator: Optional[bool] = None,
) -> None:
    """
    Unified result output handler.
    
    Outputs data as JSON if ctx.as_json is True, otherwise calls the human_printer.
    Handles exit codes consistently based on success_indicator.
    
    Args:
        ctx: CLI context containing output mode configuration
        data: The data to output (will be serialized for JSON)
        human_printer: Function to print human-readable output (ignored in JSON mode)
        exit_on_error: Whether to exit with code 1 on failure
        success_indicator: Optional boolean indicating success/failure for auto exit handling
        
    Example:
        with cli_session(path, as_json) as ctx:
            passed = ctx.compiler.lint()
            cli_result(ctx, {"passed": passed}, lambda d: console.print("OK"), success_indicator=passed)
    """
    if ctx.as_json:
        typer.echo(json.dumps(data, default=json_serializer, indent=2, ensure_ascii=False))
    else:
        if human_printer:
            human_printer(data)
    
    # Handle exit codes
    if exit_on_error and success_indicator is not None and not success_indicator:
        raise typer.Exit(code=1)


def cli_error(
    message: str,
    ctx: Optional[CLIContext] = None,
    exit_code: int = 1,
    details: Optional[dict] = None,
    raise_exit: bool = True,
) -> None:
    """
    Unified error output handler.
    
    Outputs error message as JSON or human-readable format depending on mode.
    
    Args:
        message: The error message
        ctx: Optional CLI context (determines output format; defaults to human-readable)
        exit_code: Exit code to use (default 1)
        details: Additional error details for JSON output
        raise_exit: Whether to raise typer.Exit (set to False for testing)
        
    Example:
        cli_error("File not found", ctx, details={"path": str(file_path)})
    """
    is_json_mode = ctx.as_json if ctx else False
    
    if is_json_mode:
        error_data = {
            "error": message,
            **(details or {})
        }
        typer.echo(json.dumps(error_data, default=json_serializer, indent=2, ensure_ascii=False))
    else:
        console = ctx.display_console if ctx else Console()
        console.print(f"[red]Error: {message}[/red]")
    
    if raise_exit:
        raise typer.Exit(code=exit_code)


def cli_success(
    ctx: CLIContext,
    message: str,
    data: Optional[Any] = None,
) -> None:
    """
    Unified success output handler.
    
    In JSON mode: outputs data as JSON
    In human mode: prints success message with green styling
    
    Args:
        ctx: CLI context
        message: Success message for human mode
        data: Optional data to output in JSON mode (defaults to {"success": True})
        
    Example:
        cli_success(ctx, "Operation completed", {"result": result_data})
    """
    if ctx.as_json:
        output_data = data if data is not None else {"success": True}
        typer.echo(json.dumps(output_data, default=json_serializer, indent=2, ensure_ascii=False))
    else:
        ctx.display_console.print(f"[green]{message}[/green]")


def cli_warning(
    ctx: CLIContext,
    message: str,
) -> None:
    """
    Unified warning output handler.
    
    Args:
        ctx: CLI context
        message: Warning message
        
    Example:
        cli_warning(ctx, "Deprecated feature used")
    """
    if not ctx.as_json:
        ctx.display_console.print(f"[yellow]Warning: {message}[/yellow]")


def output_result(
    data: Any, 
    as_json: bool, 
    console_printer: Optional[Callable[[Any], None]] = None
) -> None:
    """
    Legacy output handler - kept for backward compatibility.
    
    Use cli_result() for new code.
    
    Args:
        data: Data to output
        as_json: Whether to output as JSON
        console_printer: Function for human-readable output
    """
    if as_json:
        typer.echo(json.dumps(data, default=json_serializer, indent=2, ensure_ascii=False))
    else:
        if console_printer:
            console_printer(data)


def exit_with_code(code: int = 0) -> None:
    """
    Exit with a specific code in a testable way.
    
    Args:
        code: Exit code (0 for success, non-zero for error)
    """
    raise typer.Exit(code=code)

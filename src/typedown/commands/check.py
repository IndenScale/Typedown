import typer
from pathlib import Path
from typing import Optional
from typedown.core.compiler import Compiler

from rich.console import Console
from io import StringIO

from typedown.commands.utils import output_result

def check(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Project root directory"),
    script: Optional[str] = typer.Option(None, "--script", "-s", help="Script configuration to use"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """L2: Schema Compliance Check (Native Pydantic)."""
    # Use quiet console if JSON output is requested
    console = Console(file=StringIO(), stderr=False) if as_json else None
    
    compiler = Compiler(path, console=console)
    passed = compiler.check(script_name=script)
    
    if as_json:
        output_result(compiler.diagnostics, True)
        if not passed:
             raise typer.Exit(code=1)
        return

    if passed:
        typer.echo("[green]Check Passed[/green]")
    else:
        typer.echo("[red]Check Failed[/red]")
        raise typer.Exit(code=1)

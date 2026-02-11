import typer
from pathlib import Path
from typing import Optional
from typedown.core.compiler import Compiler

from rich.console import Console
from io import StringIO
from typedown.commands.utils import output_result

def validate(
    path: Path = typer.Argument(Path("."), help="Project root directory"),
    script: Optional[str] = typer.Option(None, "--script", "-s", help="Script configuration to use"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """L3: Business Logic Integrity (Graph Resolution + Specs)."""
    console = Console(file=StringIO(), stderr=False) if as_json else None
    compiler = Compiler(path, console=console)
    
    # compile() runs the full pipeline L1-L3
    passed = compiler.compile(script_name=script)
    
    if as_json:
        output_result(compiler.diagnostics, True)
        if not passed:
             raise typer.Exit(code=1)
        return

    if passed:
        typer.echo("[green]Validation Passed[/green]")
    else:
        typer.echo("[red]Validation Failed[/red]")
        raise typer.Exit(code=1)

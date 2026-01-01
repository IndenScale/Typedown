import typer
from pathlib import Path
from typing import Optional
from typedown.core.compiler import Compiler

def validate(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Project root directory"),
    script: Optional[str] = typer.Option(None, "--script", "-s", help="Script configuration to use"),
):
    """L3: Business Logic Integrity (Graph Resolution + Specs)."""
    compiler = Compiler(path)
    # compile() runs the full pipeline L1-L3
    if compiler.compile(script_name=script):
        typer.echo("[green]Validation Passed[/green]")
    else:
        typer.echo("[red]Validation Failed[/red]")
        raise typer.Exit(code=1)

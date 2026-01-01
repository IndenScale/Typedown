import typer
from pathlib import Path
from typing import Optional
from typedown.core.compiler import Compiler

def check(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Project root directory"),
    script: Optional[str] = typer.Option(None, "--script", "-s", help="Script configuration to use"),
):
    """L2: Schema Compliance Check (Native Pydantic)."""
    compiler = Compiler(path)
    if compiler.check(script_name=script):
        typer.echo("[green]Check Passed[/green]")
    else:
        typer.echo("[red]Check Failed[/red]")
        raise typer.Exit(code=1)

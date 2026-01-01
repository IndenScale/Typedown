import typer
from pathlib import Path
from typedown.core.compiler import Compiler

def lint(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Project root directory"),
):
    """L1: Syntax & Format Check (Fast Loop)."""
    compiler = Compiler(path)
    if compiler.lint():
        typer.echo("[green]Lint Passed[/green]")
    else:
        typer.echo("[red]Lint Failed[/red]")
        raise typer.Exit(code=1)

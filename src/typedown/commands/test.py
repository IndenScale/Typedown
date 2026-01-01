import typer
from pathlib import Path
from typing import Optional
from typedown.core.compiler import Compiler

def test(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Project root directory"),
    tags: str = typer.Option("", "--tags", help="Filter specs by tag (comma separated)"),
):
    """L4: External Verification (Oracles & Reality Check)."""
    compiler = Compiler(path)
    # We need to compile first to have the context for testing
    if not compiler.compile():
         typer.echo("[red]Compilation failed, aborting tests.[/red]")
         raise typer.Exit(code=1)
    
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    exit_code = compiler.run_tests(tags=tag_list)
    if exit_code != 0:
        raise typer.Exit(code=exit_code)

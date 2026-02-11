import typer
from pathlib import Path
from typing import Optional

from typedown.commands.context import cli_session
from typedown.commands.output import cli_result, cli_error

def test(
    path: Path = typer.Argument(Path("."), help="Project root directory"),
    tags: str = typer.Option("", "--tags", help="Filter specs by tag (comma separated)"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """L4: External Verification (Oracles & Reality Check)."""
    with cli_session(path, as_json=as_json, require_project=True) as ctx:
        # We need to compile first to have the context for testing
        if not ctx.compiler.compile():
            if as_json:
                cli_result(ctx, {
                    "error": "Compilation failed, aborting tests",
                    "diagnostics": ctx.compiler.diagnostics
                }, exit_on_error=False)
            else:
                ctx.display_console.print("[red]Compilation failed, aborting tests.[/red]")
            raise typer.Exit(code=1)
        
        tag_list = [t.strip() for t in tags.split(",")] if tags else []
        exit_code = ctx.compiler.run_tests(tags=tag_list)
        
        if as_json:
            cli_result(ctx, {"exit_code": exit_code}, exit_on_error=False)
        
        if exit_code != 0:
            raise typer.Exit(code=exit_code)

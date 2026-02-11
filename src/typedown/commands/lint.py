import typer
from pathlib import Path
from typing import Optional

from typedown.commands.context import cli_session
from typedown.commands.output import cli_result, cli_error

def lint(
    path: Path = typer.Argument(Path("."), help="Project root directory"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """L1: Syntax & Format Check (Fast Loop)."""
    with cli_session(path, as_json=as_json, require_project=True) as ctx:
        passed = ctx.compiler.lint()
        
        if as_json:
            result_data = {
                "passed": passed,
                "diagnostics": ctx.compiler.diagnostics
            }
            cli_result(ctx, result_data, exit_on_error=False)
            if not passed:
                raise typer.Exit(code=1)
        else:
            if passed:
                ctx.display_console.print("[green]Lint Passed[/green]")
            else:
                ctx.display_console.print("[red]Lint Failed[/red]")
                raise typer.Exit(code=1)

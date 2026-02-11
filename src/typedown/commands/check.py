import typer
from pathlib import Path
from typing import Optional

from typedown.commands.context import cli_session
from typedown.commands.output import cli_result

def check(
    path: Path = typer.Argument(Path("."), help="Project root directory"),
    script: Optional[str] = typer.Option(None, "--script", "-s", help="Script configuration to use"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """L2: Schema Compliance Check (Native Pydantic)."""
    with cli_session(path, as_json=as_json, require_project=True) as ctx:
        passed = ctx.compiler.check(script_name=script)
        
        if as_json:
            cli_result(ctx, ctx.compiler.diagnostics, exit_on_error=False)
            if not passed:
                raise typer.Exit(code=1)
        else:
            if passed:
                ctx.display_console.print("[green]Check Passed[/green]")
            else:
                ctx.display_console.print("[red]Check Failed[/red]")
                raise typer.Exit(code=1)

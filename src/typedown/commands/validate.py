import typer
from pathlib import Path
from typing import Optional

from typedown.commands.context import cli_session
from typedown.commands.output import cli_result

def validate(
    path: Path = typer.Argument(Path("."), help="Project root directory"),
    script: Optional[str] = typer.Option(None, "--script", "-s", help="Script configuration to use"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """L3: Business Logic Integrity (Graph Resolution + Specs)."""
    with cli_session(path, as_json=as_json, require_project=True) as ctx:
        # compile() runs the full pipeline L1-L3
        passed = ctx.compiler.compile(script_name=script)
        
        if as_json:
            cli_result(ctx, ctx.compiler.diagnostics, exit_on_error=False)
            if not passed:
                raise typer.Exit(code=1)
        else:
            if passed:
                ctx.display_console.print("[green]Validation Passed[/green]")
            else:
                ctx.display_console.print("[red]Validation Failed[/red]")
                raise typer.Exit(code=1)

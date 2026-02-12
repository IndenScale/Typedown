import typer
from pathlib import Path

from typedown.commands.context import cli_session
from typedown.commands.output import cli_result, cli_error

def info(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path inside the project"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """
    Get information about the current Typedown project.
    """
    with cli_session(path, as_json=as_json, require_project=True) as ctx:
        # Config is already loaded by cli_session
        config = ctx.config
        
        project_name = config.package.name if config.package else "Unnamed"
        project_version = config.package.version if config.package else "0.0.0"

        info_data = {
            "root": str(ctx.project_root),
            "config_path": str(ctx.project_root / "typedown.toml"),
            "project_name": project_name,
            "version": project_version,
            "oracles": config.test.oracles
        }
        
        def print_human(data):
            ctx.display_console.print(f"[bold green]Project:[/bold green] {data['project_name']} ({data['version']})")
            ctx.display_console.print(f"[bold]Root:[/bold] {data['root']}")
        
        cli_result(ctx, info_data, print_human, exit_on_error=False)

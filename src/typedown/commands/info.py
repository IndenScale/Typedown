import typer
from pathlib import Path
from rich.console import Console

from typedown.core.base.utils import find_project_root
from typedown.core.base.config import TypedownConfig
from typedown.commands.utils import output_result

console = Console()

def info(
    path: Path = typer.Option(Path("."), "--path", "-p", help="Path inside the project"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """
    Get information about the current Typedown project.
    """
    try:
        project_root = find_project_root(path.resolve())
    except Exception:
        if as_json:
            output_result({"error": "Not a Typedown project"}, True)
        else:
            console.print(f"[red]Error: Could not find typedown.toml in ancestors of {path}[/red]")
        raise typer.Exit(code=1)

    try:
        config_path = project_root / "typedown.toml"
        config = TypedownConfig.load(config_path)
        
        project_name = config.package.name if config.package else "Unnamed"
        project_version = config.package.version if config.package else "0.0.0"

        info_data = {
            "root": str(project_root),
            "config_path": str(config_path),
            "project_name": project_name,
            "version": project_version,
            "scripts": list(config.scripts.keys()),
            "tasks": list(config.tasks.keys()),
            "oracles": config.test.oracles
        }
        
        def print_human(data):
            console.print(f"[bold green]Project:[/bold green] {data['project_name']} ({data['version']})")
            console.print(f"[bold]Root:[/bold] {data['root']}")
            console.print(f"[bold]Scripts:[/bold] {', '.join(data['scripts'])}")
            console.print(f"[bold]Tasks:[/bold] {', '.join(data['tasks'])}")
            
        output_result(info_data, as_json, print_human)
        
    except Exception as e:
        if as_json:
            output_result({"error": str(e)}, True)
        else:
            console.print(f"[red]Error loading config: {e}[/red]")
        raise typer.Exit(code=1)

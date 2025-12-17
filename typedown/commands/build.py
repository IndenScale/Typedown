import typer
import json
import shutil
import sys
from pathlib import Path
from rich.console import Console

from typedown.core.workspace import Workspace

console = Console()

def _check_output_safety(output_dir: Path, source_path: Path, force: bool):
    """
    Ensure we are not deleting something important.
    """
    resolved_output = output_dir.resolve()
    resolved_source = source_path.resolve()
    resolved_cwd = Path.cwd().resolve()
    
    # 1. Path Safety Check
    
    # Protect System Paths
    if resolved_output == Path("/").resolve() or resolved_output == Path.home().resolve():
         console.print(f"[bold red]Error:[/bold red] Output directory cannot be system root or home directory.")
         raise typer.Exit(code=1)

    # Protect Source and CWD
    if resolved_output == resolved_cwd:
         console.print(f"[bold red]Error:[/bold red] Output directory cannot be the current working directory.")
         raise typer.Exit(code=1)
         
    if resolved_output == resolved_source:
         console.print(f"[bold red]Error:[/bold red] Output directory cannot be the project source directory.")
         raise typer.Exit(code=1)
         
    # Protect Containment: Source inside Output (The "rm -rf parent" danger)
    # If output is /foo and source is /foo/bar, deleting /foo deletes source.
    if resolved_output in resolved_source.parents:
         console.print(f"[bold red]Error:[/bold red] Output directory cannot contain the source directory.")
         raise typer.Exit(code=1)

    # 2. Existence Check
    if output_dir.exists():
        if not output_dir.is_dir():
             console.print(f"[bold red]Error:[/bold red] Output path '{output_dir}' exists and is not a directory.")
             raise typer.Exit(code=1)

        if any(output_dir.iterdir()):
             if force:
                 console.print(f"[yellow]Warning:[/yellow] Output directory '{output_dir}' exists. Forcing clean.")
                 shutil.rmtree(output_dir)
             else:
                 # Interactive check
                 if sys.stdin.isatty():
                     confirm = typer.confirm(f"Output directory '{output_dir}' is not empty. Clean and overwrite?")
                     if not confirm:
                         console.print("Aborted.")
                         raise typer.Exit(code=0)
                     shutil.rmtree(output_dir)
                 else:
                     # Non-interactive (CI) -> Fail safe
                     console.print(f"[bold red]Error:[/bold red] Output directory '{output_dir}' is not empty. Use --force to overwrite.")
                     raise typer.Exit(code=1)

def build(
    path: Path = typer.Argument(Path("."), help="Project root to build"),
    output: Path = typer.Option(Path("dist"), "--output", "-o", help="Output directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite output directory")
):
    """
    Build the project into a self-contained distribution package.
    It processes content from 'docs/', loads models from 'models/',
    and generates 'dist/data.json' along with copying 'assets/' and 'docs/' content.
    """
    console.print(f"[bold blue]Typedown:[/bold blue] Building {path}...")
    
    # Check output safety BEFORE running validation (fail fast)
    output_dir = output.resolve()
    _check_output_safety(output_dir, path, force)

    # 1. Validation Phase
    workspace = Workspace(root=path if path.is_dir() else path.parent)
    try:
        workspace.load(path)
        workspace.resolve() # This will raise typer.Exit(1) on validation failure
    except Exception as e:
        console.print(f"[bold red]Build Failed during Validation:[/bold red] {e}")
        raise typer.Exit(code=1)

    # 2. Artifact Generation Phase
    console.print(f"[blue]Generating artifacts in:[/blue] {output_dir}")
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # 2.1 Generate data.json (The Giant Blob)
    data_map = {}
    for entity_id, entity in workspace.project.symbol_table.items():
        # We export the Resolved Data
        data_map[entity_id] = entity.resolved_data
    
    data_file = output_dir / "data.json"
    data_file.write_text(json.dumps(data_map, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"  [green]✓[/green] Created data.json ({len(data_map)} entities)")

    # 2.2 Copy Content (Markdown Files)
    # We want to maintain relative structure from project root.
    content_dir = output_dir / "content"
    if not content_dir.exists():
        content_dir.mkdir()
        
    for rel_path, doc in workspace.project.documents.items():
        # Source Absolute Path
        src = doc.path
        # Dest Absolute Path
        dest = content_dir / rel_path
        
        # Ensure parent dirs exist
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(src, dest)
        
    console.print(f"  [green]✓[/green] Copied {len(workspace.project.documents)} markdown files to content/")

    # 2.3 Copy Assets
    assets_src = workspace.root / "assets"
    if assets_src.exists() and assets_src.is_dir():
         assets_dest = output_dir / "assets"
         # shutil.copytree requires dest to usually not exist or be empty depending on python version
         # We already cleaned output_dir, so if assets_dest exists it means it was created in this run? 
         # Unlikely. But copytree dirs_exist_ok verified in python 3.8+
         shutil.copytree(assets_src, assets_dest, dirs_exist_ok=True)
         console.print(f"  [green]✓[/green] Copied assets directory")

    console.print(f"[bold green]Build successful![/bold green]")

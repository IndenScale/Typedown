import typer
from pathlib import Path
from typedown.commands import debug
from typedown.commands.test import test as test_cmd
from typedown.commands.build import build as build_cmd
from typedown.commands.lsp import lsp as lsp_cmd

app = typer.Typer(help="Typedown CLI: Progressive Formalization for Markdown")

# Register 'debug' group
app.add_typer(debug.app, name="debug")

# Register 'test' command
app.command(name="test")(test_cmd)

# Register 'lsp' command
app.command(name="lsp")(lsp_cmd)

@app.command()
def init(name: str):
    """
    Initialize a new Typedown project with the standard directory structure.
    """
    project_root = Path(name).resolve()
    if project_root.exists():
        typer.echo(f"Error: Directory '{project_root}' already exists.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Initializing new Typedown project: {project_root}")

    # Create core directories
    (project_root / "docs").mkdir(parents=True)
    (project_root / "models").mkdir(parents=True)
    (project_root / "specs").mkdir(parents=True)
    (project_root / "assets").mkdir(parents=True)

    # Add placeholder files
    (project_root / "docs" / "config.td").write_text("# Typedown Configuration")
    (project_root / "docs" / "README.md").write_text("# Welcome to your Typedown Project\n\nThis is your main documentation directory.")
    (project_root / "models" / "__init__.py").touch() # Empty init file for Python module
    (project_root / "specs" / "__init__.py").touch() # Empty init file for Python module
    (project_root / "specs" / "example_spec.md").write_text("""
# Example Specifications

This file contains example specifications for your project.

```spec
def test_example_spec(workspace):
    assert True
```
""")

    typer.echo(f"[green]Successfully initialized project '{name}' at {project_root}[/green]")

# Using wrapper to map Typer's CLI args to our function
@app.command(name="build")
def build_cli(
    path: Path = typer.Argument(Path("."), help="Project root to build"),
    output: Path = typer.Option(Path("dist"), "--output", "-o", help="Output directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite output directory")
):
    """
    Build the project into a self-contained distribution package.
    """
    build_cmd(path, output, force)

if __name__ == "__main__":
    app()
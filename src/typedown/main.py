import typer
from pathlib import Path
from typedown.commands.lsp import lsp as lsp_cmd
from typedown.commands.query import query as query_cmd

def version_callback(value: bool):
    if value:
        import importlib.metadata
        try:
            version = importlib.metadata.version("typedown")
        except importlib.metadata.PackageNotFoundError:
            version = "0.1.0" # Fallback for development
        typer.echo(f"Typedown version: {version}")
        raise typer.Exit()

app = typer.Typer()

@app.callback()
def main(
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show version and exit.")
):
    pass

from typedown.commands.lint import lint as lint_cmd
from typedown.commands.check import check as check_cmd
from typedown.commands.validate import validate as validate_cmd
from typedown.commands.test import test as test_cmd
from typedown.commands.run import run as run_cmd

# Register 'lsp' command
app.command(name="lsp")(lsp_cmd)

# Register 'query' command
app.command(name="query")(query_cmd)

# Register QC commands
app.command(name="lint")(lint_cmd)
app.command(name="check")(check_cmd)
app.command(name="validate")(validate_cmd)
app.command(name="test")(test_cmd)

# Register 'run' command (Script System)
app.command(name="run")(run_cmd)

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


if __name__ == "__main__":
    app()
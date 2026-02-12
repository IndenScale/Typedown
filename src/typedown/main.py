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
    """
    Typedown CLI - Progressive Formalization for Markdown.
    
    Core concepts for Agents:
    
    1. Model-First Design:
       - Define your domain concepts using ```model:Name blocks
       - Use Pydantic syntax for field types and validators
       - Models are the single source of truth for structure
    
    2. Entity Instantiation:
       - Create concrete instances using ```entity Model:id blocks
       - ID format: lowercase-with-hyphens (e.g., user-alice-v1)
       - YAML syntax, strictly validated against the model
    
    3. Reference System:
       - Use [[entity-id]] for linking entities
       - References are bidirectional and type-checked
       - Prefer references over embedding foreign keys as strings
    
    4. Validation Layers:
       - Field validators: format/transform individual fields
       - Model validators: cross-field consistency within entity
       - Spec blocks: cross-entity business rules and aggregations
    
    5. Workflow:
       - edit files -> typedown check -> fix errors -> iterate
       - Use --json for programmatic output in Agent workflows
       - Use --full for CI/CD to run all validation stages
    
    Commands:
        check       Validate files (primary command)
        query       Query entities and references
        info        Show project information
        lsp         Start language server
        init        Initialize a new project
        complete    Get completions for a file position
    
    See --help for individual commands for detailed guidance.
    """
    pass

# Import unified check command
from typedown.commands.check import check as check_cmd  # noqa: E402

# Register 'lsp' command
app.command(name="lsp")(lsp_cmd)

# Register 'query' command
app.command(name="query")(query_cmd)

# Register unified 'check' command (FEAT-0008)
app.command(name="check")(check_cmd)

from typedown.commands.info import info as info_cmd  # noqa: E402
app.command(name="info")(info_cmd)

from typedown.commands.complete import complete as complete_cmd  # noqa: E402
app.command(name="complete")(complete_cmd)

from typedown.commands.setup import setup_cmd  # noqa: E402
app.add_typer(setup_cmd, name="setup")

@app.command()
def init(name: str):
    """
    Initialize a new Typedown project with the standard directory structure.
    
    [Project Structure]
    
    The init command creates the following layout:
    
        <name>/
        ├── docs/           # Documentation and configuration
        │   ├── config.td   # Project-level configuration
        │   └── README.md   # Entry point documentation
        ├── models/         # Python model definitions (if needed)
        │   └── __init__.py
        ├── specs/          # Validation specs
        │   ├── __init__.py
        │   └── example_spec.md
        └── assets/         # Static assets (images, files)
    
    [Best Practices]
    
    1. File Organization:
       - Group by domain: users/, orders/, inventory/
       - Or group by type: models/, entities/, specs/
       - Keep config.td at docs/ root (loaded automatically)
    
    2. Naming Conventions:
       - Model names: PascalCase (User, OrderItem)
       - Entity IDs: lowercase-with-hyphens (user-alice, order-2024-001)
       - Files: descriptive, match content (users.td, orders.td)
    
    3. Model Granularity:
       - One model per logical concept
       - Use inheritance for shared fields (BaseEntity)
       - Extract Value Objects for complex fields (Address, Money)
    
    4. Spec Organization:
       - Group related specs in one file
       - Name specs by what they check: check_admin_mfa, validate_order_total
       - Use @target decorator to limit scope
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

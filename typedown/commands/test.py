import typer
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
import pytest
import tempfile
import shutil

from markdown_it import MarkdownIt
from typedown.core.workspace import Workspace

console = Console()
md = MarkdownIt()

_global_workspace = None # To hold the workspace instance

def test(
    path: Path = typer.Argument(Path("."), help="File or directory to validate"),
    tags: List[str] = typer.Option([], "--tag", "-t", help="Tags for filter specs execution")
):
    """
    Run the analysis pipeline and execute all detected spec blocks using Pytest.
    Includes Parsing, Dependency Resolution, Data Version/Validation and Spec Execution.
    """
    console.print(f"[bold blue]Typedown:[/bold blue] Running tests for {path}...")
    
    global _global_workspace # Access the global variable

    workspace = Workspace(root=path if path.is_dir() else path.parent)
    try:
        workspace.load(path)
        workspace.resolve(tags=tags)
        _global_workspace = workspace # Store the initialized workspace
    except Exception as e:
        console.print(f"[bold red]Fatal Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    
    stats = workspace.get_stats()

    # Summary Table
    table = Table(title="Project Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Root Directory", stats["root"])
    table.add_row("Documents Parsed", str(stats["documents"]))
    table.add_row("Entities Found", str(stats["entities"]))
    table.add_row("Specs Found", str(stats["specs"]))

    console.print(table)

    if stats["entities"] == 0 and stats["documents"] > 0:
        console.print("[yellow]Warning: No entities found. Did you use ```entity:Type ... ``` blocks?[/yellow]")

    # --- New Test Execution Logic ---
    console.print("[bold blue]Typedown:[/bold blue] Extracting and running spec blocks...")

    # Create a temporary directory for pytest files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_files = []

        # Create a conftest.py for the workspace fixture
        conftest_content = """
import pytest
from typedown.core.workspace import Workspace
from typedown.commands.test import _global_workspace

@pytest.fixture(scope="session")
def workspace():
    if _global_workspace is None:
        raise RuntimeError("Workspace not initialized. Ensure td test command was run correctly.")
    return _global_workspace
"""
        (tmp_path / "conftest.py").write_text(conftest_content)
        console.print(f"Created temporary conftest.py in {tmp_path}")

        # Discover markdown files in the workspace
        # Support both .md and .td
        from itertools import chain
        files = chain(workspace.root.glob("**/*.md"), workspace.root.glob("**/*.td"))
        for md_file in files:
            extracted_specs = extract_spec_blocks(md_file)
            if extracted_specs:
                console.print(f"  Found {len(extracted_specs)} spec blocks in {md_file.relative_to(workspace.root)}")
                for i, spec_code in enumerate(extracted_specs):
                    test_file = tmp_path / f"test_{md_file.stem}_{i}.py"
                    test_file.write_text(spec_code)
                    test_files.append(test_file)

        if not test_files:
            console.print("[yellow]No spec blocks found to test.[/yellow]")
            console.print(f"[green]Test command complete, no tests executed.[/green]")
            return # Exit if no test files were created

        # Run pytest
        console.print(f"[bold blue]Typedown:[/bold blue] Running Pytest from {tmp_path}...")
        # This will run pytest in the temporary directory, discovering our generated tests and conftest.py
        exit_code = pytest.main([str(tmp_path)])

        if exit_code == 0:
            console.print(f"[green]All spec tests passed.[/green]")
        else:
            console.print(f"[bold red]Some spec tests failed. Exit code: {exit_code}[/bold red]")
            raise typer.Exit(code=exit_code)

    console.print(f"[green]Test command complete.[/green]")


def extract_spec_blocks(filepath: Path) -> List[str]:
    """
    Extracts Python code from 'spec' fenced code blocks in a Markdown file.
    """
    md_content = filepath.read_text()
    tokens = md.parse(md_content)

    spec_blocks = []
    for i, token in enumerate(tokens):
        if token.type == 'fence' and token.info.strip() == 'spec':
            # Auto-inject pytest as per RFC 006
            script = "import pytest\n" + token.content
            spec_blocks.append(script)
    return spec_blocks

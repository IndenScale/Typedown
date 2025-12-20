import typer
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
import pytest
import tempfile
import shutil
import sys
import os

from typedown.core.compiler import Compiler

console = Console()

_global_compiler = None 

def test(
    path: Path = typer.Argument(Path("."), help="File or directory to validate"),
    tags: List[str] = typer.Option([], "--tag", "-t", help="Tags for filter specs execution")
):
    """
    Run the analysis pipeline and execute all detected spec blocks using Pytest.
    Includes Scanning, Linking, Validation and Execution.
    """
    global _global_compiler
    
    # Handle :script syntax
    script_name = None
    target_path = path
    path_str = str(path)
    
    if path_str.startswith(":"):
        script_name = path_str[1:]
        target_path = Path(".") # Use CWD to find project root

    compiler = Compiler(target_path)
    if not compiler.compile(script_name):
        raise typer.Exit(code=1)
    
    _global_compiler = compiler
    stats = compiler.get_stats()

    # Summary Table
    table = Table(title="Typedown Build Summary", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Project Root", stats["root"])
    table.add_row("Documents", f"{stats['documents']} ({stats['target_documents']} targeted)")
    table.add_row("Entities", str(stats["entities"]))
    table.add_row("Models", str(stats["models"]))
    table.add_row("Specs", str(stats["specs"]))
    table.add_row("Total Named Symbols", str(stats["symbols"]), end_section=True)

    console.print(table)

    if stats["specs"] == 0:
        console.print("[yellow]No spec blocks found to test.[/yellow]")
        return

    console.print("[bold blue]Typedown:[/bold blue] Running spec tests via Pytest...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create conftest.py in the same process
        conftest_content = f"""
import pytest
import sys
from pathlib import Path

@pytest.fixture(scope="session")
def compiler():
    from typedown.commands.test import _global_compiler
    return _global_compiler

@pytest.fixture(scope="session")
def workspace(compiler):
    return compiler
"""
        (tmp_path / "conftest.py").write_text(conftest_content)

        # Generator for test files
        for doc_path, doc in compiler.documents.items():
            # Only generate tests for Target Files
            if doc_path not in compiler.target_files:
                continue

            if not doc.specs:
                continue
            
            sanitized_path = doc_path.relative_to(compiler.project_root).with_suffix("").as_posix().replace("/", "_").replace(".", "_")
            
            # Use absolute paths for sys.path injection
            p1 = str(doc_path.parent.resolve())
            p2 = str(doc_path.parent.parent.resolve())
            root = str(compiler.project_root)
            
            for i, spec in enumerate(doc.specs):
                test_file = tmp_path / f"test_{sanitized_path}_{i}.py"
                
                header = f"""
import sys
import os
from pathlib import Path

# Path injection for modular use cases
paths_to_add = [r"{p1}", r"{p2}", r"{root}"]
for p in paths_to_add:
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
"""
                content = header + spec.code
                test_file.write_text(content)

        # Prepare Pytest arguments
        pytest_args = [str(tmp_path), "-p", "no:warnings"]
        
        # Merge tags from CLI and Script
        final_tags = set(tags)
        if compiler.active_script and compiler.active_script.tags:
            final_tags.update(compiler.active_script.tags)
            
        if final_tags:
            marker_expr = " or ".join(final_tags)
            pytest_args.extend(["-m", marker_expr])

        # Run pytest in the SAME process
        exit_code = pytest.main(pytest_args)
        
        if exit_code == 0:
            console.print(f"[bold green]✨ All specs passed![/bold green]")
        elif exit_code == 1:
             console.print(f"[bold yellow]⚠️ Some specs failed.[/bold yellow]")
        elif exit_code == 5:
             console.print(f"[bold yellow]⚠️ No specs matched the filters.[/bold yellow]") # Pytest code 5 = no tests collected
        else:
            console.print(f"[bold red]❌ Pytest Error (Exit Code: {exit_code})[/bold red]")
            raise typer.Exit(code=exit_code)

import typer
import json
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax

from typedown.core.parser import Parser

app = typer.Typer(help="Debug internal states and ASTs.")
console = Console()

@app.command("parse")
def debug_parse(
    file_path: Path = typer.Argument(..., help="Path to the markdown file to parse", exists=True),
    raw: bool = typer.Option(False, help="Show raw JSON without formatting")
):
    """
    Parse a single file and dump its AST (Document Node).
    """
    parser = Parser()
    try:
        doc = parser.parse_file(file_path)
        
        # Pydantic v2 dump (model_dump_json)
        # Assuming pydantic v2. If v1, use .json()
        json_output = doc.model_dump_json(indent=2)
        
        if raw:
            print(json_output)
        else:
            syntax = Syntax(json_output, "json", theme="monokai", line_numbers=True)
            console.print(syntax)
            
    except Exception as e:
        console.print(f"[bold red]Error parsing file:[/bold red] {e}")
        raise typer.Exit(code=1)

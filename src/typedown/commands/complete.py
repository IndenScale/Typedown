import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console

from lsprotocol.types import CompletionParams, Position, TextDocumentIdentifier, CompletionList, CompletionItem

from typedown.core.compiler import Compiler
from typedown.commands.utils import output_result

class MockWorkspace:
    def __init__(self, file_path: Path, content: str):
        self.file_path = file_path
        self.content = content
        
    def get_text_document(self, uri: str):
        # Return a mocked document object with 'source' attribute
        return type('MockDocument', (), {'source': self.content})

class MockLS:
    def __init__(self, compiler: Compiler, workspace):
        self.compiler = compiler
        self.workspace = workspace
        self.is_ready = True

def complete(
    file: Path = typer.Argument(..., help="File path to complete in"),
    line: int = typer.Option(..., "--line", "-l", help="Line number (0-indexed)"),
    character: int = typer.Option(..., "--char", "-c", help="Character offset (0-indexed)"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Project root directory"),
    content: Optional[str] = typer.Option(None, "--content", help="Override file content (for unsaved changes)"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """
    Get LSP completions for a specific position in a file.
    """
    # 1. Initialize Compiler (Silent)
    from io import StringIO
    console = Console(file=StringIO(), stderr=False)
    compiler = Compiler(path, console=console)
    
    # 2. Compile to populate symbol table
    # We must scan the project to know about entities
    compiler.compile(run_specs=False)
    
    # 3. Prepare Content
    target_file = file.resolve()
    file_content = content
    if file_content is None:
        if target_file.exists():
            file_content = target_file.read_text()
        else:
             # If file doesn't exist and no content provided, we can't context match
             file_content = ""

    # 4. Mock LS Environment
    workspace = MockWorkspace(target_file, file_content)
    ls = MockLS(compiler, workspace)
    
    # 5. Call Completion Logic
    from typedown.server.features.completion import completions
    
    # Mock Params
    # URI doesn't matter much as long as workspace.get_text_document returns our mock
    params = CompletionParams(
        text_document=TextDocumentIdentifier(uri=str(target_file)),
        position=Position(line=line, character=character)
    )
    
    results = completions(ls, params)
    
    # 6. Output
    if isinstance(results, list):
        items = results
    elif isinstance(results, CompletionList):
        items = results.items
    else:
        items = []

    if as_json:
        # Serialize CompletionItems
        output_result(items, True)
    else:
        # Human readable
        console = Console()
        console.print(f"[bold]Completions at {line}:{character}[/bold]")
        for item in items:
            console.print(f"- {item.label} ({item.kind.name})")
            if item.detail:
                console.print(f"  [dim]{item.detail}[/dim]")

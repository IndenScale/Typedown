import typer
from pathlib import Path
from typing import Optional, List

from rich.console import Console
from lsprotocol.types import CompletionList, CompletionItem

from typedown.commands.context import compiler_session
from typedown.commands.output import cli_result
from typedown.server.services import CompletionService, CompletionContext


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
    with compiler_session(path, as_json=as_json) as (compiler, console, display_console):
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

        # 4. Create completion context
        context = CompletionContext(
            file_path=target_file,
            content=file_content,
            line=line,
            character=character
        )
        
        # 5. Call CompletionService directly
        service = CompletionService(compiler)
        results = service.complete(context)
        
        # 6. Output
        if isinstance(results, list):
            items = results
        elif isinstance(results, CompletionList):
            items = results.items
        else:
            items = []

        if as_json:
            # Serialize CompletionItems
            cli_result(
                type('Ctx', (), {'as_json': True, 'display_console': display_console})(),
                items,
                exit_on_error=False
            )
        else:
            # Human readable
            display_console.print(f"[bold]Completions at {line}:{character}[/bold]")
            for item in items:
                display_console.print(f"- {item.label} ({item.kind.name})")
                if item.detail:
                    display_console.print(f"  [dim]{item.detail}[/dim]")

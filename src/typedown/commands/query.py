import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table

from typedown.core.compiler import Compiler

console = Console()

def query(
    query_str: str = typer.Argument(..., help="The query string to execute (e.g., 'User.alice' or 'SELECT * FROM User')"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Project root directory"),
    scope: Optional[Path] = typer.Option(None, "--scope", "-s", help="Limit search to this directory"),
    is_sql: bool = typer.Option(False, "--sql", help="Treat query as SQL"),
):
    """
    Execute a query against the Typedown project.
    Supports Logical IDs, Property Access, and Asset Paths.
    """
    compiler = Compiler(path, console)
    
    # We need to compile first to populate symbol table and resources
    # Using a fast compile mode if possible? For now full compile.
    if not compiler.compile():
        raise typer.Exit(code=1)
        
    # Resolve scope relative to CWD if provided
    resolved_scope = scope.resolve() if scope else None
    
    # Execute SQL Query
    if is_sql:
        from typedown.core.analysis.query import QueryEngine, QueryError
        try:
            results = QueryEngine.execute_sql(query_str, compiler.symbol_table)
            
            if not results:
                console.print(f"[yellow]No results found for SQL: {query_str}[/yellow]")
                return

            table = Table(title=f"SQL Results: {query_str}")
            if results:
                columns = results[0].keys()
                for col in columns:
                    table.add_column(str(col))
                
                for row in results:
                    table.add_row(*[str(row.get(col, "")) for col in columns])
            
            console.print(table)
            return
            
        except QueryError as e:
            console.print(f"[red]SQL Error: {e}[/red]")
            raise typer.Exit(code=1)
    
    # Execute Standard Query
    from typedown.core.analysis.query import QueryEngine
    
    results = QueryEngine.resolve_query(
        query=query_str, 
        symbol_table=compiler.symbol_table,
        root_dir=compiler.project_root,
        scope=resolved_scope,
        context_path=resolved_scope or compiler.target
    )
    
    if not results:
        console.print(f"[yellow]No results found for '{query_str}'[/yellow]")
        return

    table = Table(title=f"Query Results: {query_str}")
    table.add_column("Type", style="cyan")
    table.add_column("Value/Preview", style="white")
    table.add_column("Location", style="dim")

    for item in results:
        item_type = type(item).__name__
        loc = ""
        preview = str(item)
        
        if hasattr(item, 'location') and item.location:
             loc = f"{item.location.file_path}:{item.location.line_start}"
        
        if hasattr(item, 'id'):
             preview = f"ID: {item.id}"
             
        # AST Nodes
        if hasattr(item, 'resolved_data'):
             import json
             preview = json.dumps(item.resolved_data, indent=2, ensure_ascii=False)
        elif hasattr(item, 'path'): # Resource
             preview = f"File: {item.path}"
             
        table.add_row(item_type, preview[:200] + "..." if len(preview)>200 else preview, loc)

    console.print(table)

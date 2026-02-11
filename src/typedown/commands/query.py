import typer
from pathlib import Path
from typing import Optional

from rich.table import Table

from typedown.commands.context import cli_session
from typedown.commands.output import cli_result, cli_error

def query(
    query_str: str = typer.Argument(..., help="The query string to execute (e.g., 'User.alice' or 'SELECT * FROM User')"),
    path: Path = typer.Option(Path("."), "--path", "-p", help="Project root directory"),
    scope: Optional[Path] = typer.Option(None, "--scope", "-s", help="Limit search to this directory"),
    is_sql: bool = typer.Option(False, "--sql", help="Treat query as SQL"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """
    Execute a query against the Typedown project.
    Supports Logical IDs, Property Access, and Asset Paths.
    """
    with cli_session(path, as_json=as_json, require_project=True) as ctx:
        # We need to compile first to populate symbol table and resources
        # We ignore the return value (True/False) because we want to query partial results even on error.
        # Exclude specs if outputting JSON to avoid noise
        ctx.compiler.compile(run_specs=not as_json)
        
        # Resolve scope relative to CWD if provided
        resolved_scope = scope.resolve() if scope else None
        
        # Execute SQL Query
        if is_sql:
            from typedown.core.analysis.query import QueryEngine, QueryError
            try:
                results = QueryEngine.execute_sql(query_str, ctx.compiler.symbol_table)
                
                if not results:
                    if as_json:
                        cli_result(ctx, [], exit_on_error=False)
                    else:
                        ctx.display_console.print(f"[yellow]No results found for SQL: {query_str}[/yellow]")
                    return

                def print_sql_table(items):
                    table = Table(title=f"SQL Results: {query_str}")
                    if items:
                        columns = items[0].keys()
                        for col in columns:
                            table.add_column(str(col))
                        
                        for row in items:
                            table.add_row(*[str(row.get(col, "")) for col in columns])
                    
                    ctx.display_console.print(table)

                cli_result(ctx, results, print_sql_table, exit_on_error=False)
                return
                
            except QueryError as e:
                if as_json:
                    cli_result(ctx, {"error": str(e)}, exit_on_error=False)
                else:
                    ctx.display_console.print(f"[red]SQL Error: {e}[/red]")
                raise typer.Exit(code=1)
        
        # Execute Standard Query
        from typedown.core.analysis.query import QueryEngine
        
        results = QueryEngine.resolve_query(
            query=query_str, 
            symbol_table=ctx.compiler.symbol_table,
            root_dir=ctx.compiler.project_root,
            scope=resolved_scope,
            context_path=resolved_scope or ctx.compiler.target
        )
        
        if not results:
            if as_json:
                cli_result(ctx, [], exit_on_error=False)
            else:
                ctx.display_console.print(f"[yellow]No results found for '{query_str}'[/yellow]")
            return

        def print_table(items):
            table = Table(title=f"Query Results: {query_str}")
            table.add_column("Type", style="cyan")
            table.add_column("Value/Preview", style="white")
            table.add_column("Location", style="dim")

            for item in items:
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
                elif hasattr(item, 'path'):  # Resource
                    preview = f"File: {item.path}"
                    
                table.add_row(item_type, preview[:200] + "..." if len(preview)>200 else preview, loc)

            ctx.display_console.print(table)

        cli_result(ctx, results, print_table, exit_on_error=False)

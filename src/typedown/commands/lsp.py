import typer
import sys
import logging


def lsp(
    port: int = typer.Option(None, "--port", help="Run in TCP/WebSocket mode on this port instead of stdio"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to for TCP/WebSocket mode"),
    ws: bool = typer.Option(False, "--ws", help="Run in WebSocket mode (requires --port)"),
):
    """
    Start the Typedown Language Server.
    """
    try:
        from typedown.server.application import server
    except ImportError as e:
        typer.echo(f"Error: Could not import LSP server. Is 'pygls' installed? ({e})", err=True)
        typer.echo("Try installing with: uv sync --extra server", err=True)
        raise typer.Exit(code=1)

    # Setup basic logging to stderr so it doesn't interfere with stdio communication
    # logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    if ws:
        typer.echo(f"Starting LSP server on ws://{host}:{port}...", err=True)
        server.start_ws(host, port)
    elif port:
        typer.echo(f"Starting LSP server on {host}:{port}...", err=True)
        server.start_tcp(host, port)
    else:
        # Prevent any accidental print() from corrupting LSP stdout
        original_stdout = sys.stdout
        
        class StderrWriter:
            def write(self, message):
                sys.stderr.write(message)
            def flush(self):
                sys.stderr.flush()
                
        sys.stdout = StderrWriter()
        
        # Pass the binary streams to pygls to ensure correct protocol handling (bytes vs string)
        server.start_io(stdin=sys.stdin.buffer, stdout=original_stdout.buffer)

from typing import Any, Optional
from rich.console import Console
from rich.panel import Panel

class TypedownError(Exception):
    """
    Base class for all Typedown errors that should be reported cleanly to the user.
    """
    def __init__(self, message: str, location: Optional[Any] = None, severity: str = "error"):
        super().__init__(message)
        self.message = message
        self.location = location # Should be SourceLocation or compatible object
        self.severity = severity

def print_diagnostic(console: Console, error: TypedownError):
    """
    Print a diagnostic message in a compiler-like style.
    """
    loc_str = "Unknown location"
    context = ""
    
    if error.location:
        # Assuming SourceLocation structure
        file_path = getattr(error.location, "file_path", "??")
        line = getattr(error.location, "line_start", "?")
        col = getattr(error.location, "col_start", "?")
        loc_str = f"{file_path}:{line}:{col}"
        
        # Ideally, we would read the file line content here to show context
        # For P0, let's keep it simple.
        
    color = "red" if error.severity == "error" else "yellow"
    
    console.print(f"[{color} bold]{error.severity.capitalize()}: {error.message}[/{color} bold]")
    console.print(f"  --> {loc_str}")
    
    if hasattr(error, '__cause__') and error.__cause__:
        console.print(f"  [dim]Caused by: {error.__cause__}[/dim]")

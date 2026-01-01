from typing import Any, Optional
from rich.console import Console

class TypedownError(Exception):
    """Base class for all Typedown errors that should be reported cleanly."""
    def __init__(self, message: str, location: Optional[Any] = None, severity: str = "error"):
        super().__init__(message)
        self.message = message
        self.location = location
        self.severity = severity

class CycleError(TypedownError):
    """Raised when a circular dependency is detected."""
    pass

class ReferenceError(TypedownError):
    """Raised when a referenced symbol is missing."""
    pass

class QueryError(TypedownError):
    """Raised when a query cannot be resolved (syntax or semantic)."""
    pass

def print_diagnostic(console: Console, error: TypedownError):
    """Print a diagnostic message in a compiler-like style."""
    loc_str = "Unknown location"
    if error.location:
        # Assuming SourceLocation structure
        file_path = getattr(error.location, "file_path", "??")
        line = getattr(error.location, "line_start", "?")
        col = getattr(error.location, "col_start", "?")
        loc_str = f"{file_path}:{line}:{col}"

    color = "red" if error.severity == "error" else "yellow"
    console.print(f"[{color} bold]{error.severity.capitalize()}: {error.message}[/{color} bold]")
    console.print(f"  --> {loc_str}")
    
    if hasattr(error, '__cause__') and error.__cause__:
        console.print(f"  [dim]Caused by: {error.__cause__}[/dim]")

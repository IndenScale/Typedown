"""
Typedown Error System: Structured error codes and levels for machine-readable diagnostics.

Error Code Format: E{level}{category}{sequence}
- Level: 01=L1 (Scanner), 02=L2 (Linker), 03=L3 (Validator), 04=L4 (Spec)
- Category: 0=Syntax, 1=Execution, 2=Reference, 3=Schema, 4=System
- Sequence: 01-99

Example: E0101 = L1 Syntax Error #01
"""

from enum import Enum, auto
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field
from rich.console import Console


class ErrorLevel(str, Enum):
    """Severity level for diagnostics."""
    ERROR = "error"       # Critical error, blocks execution
    WARNING = "warning"   # Potential issue, execution continues
    INFO = "info"         # Informational message
    HINT = "hint"         # Suggestion for improvement
    
    def __str__(self) -> str:
        return self.value


class ErrorCode(str, Enum):
    """
    Comprehensive error code system for Typedown.
    
    Format: E{stage}{category}{number}
    - Stage: 01=L1 Scanner, 02=L2 Linker, 03=L3 Validator, 04=L4 Spec, 09=System
    - Category within stage: 
      - 0x/1x = Syntax/Parse errors
      - 2x/3x = Execution errors  
      - 4x/5x = Reference/Link errors
      - 6x/7x = Schema/Type errors
      - 8x/9x = System errors
    """
    
    # L1: Scanner Errors (E01xx) - Syntax/Parse: 01-19, Execution: 20-39
    E0101 = "E0101"  # Syntax parse failure
    E0102 = "E0102"  # Config block location error
    E0103 = "E0103"  # Nested list anti-pattern
    E0104 = "E0104"  # File read error
    E0105 = "E0105"  # Document structure error
    
    # L2: Linker Errors (E02xx) - Execution: 20-39, Reference: 40-59, Schema: 60-79
    E0221 = "E0221"  # Model execution failed
    E0222 = "E0222"  # Config execution failed
    E0231 = "E0231"  # Class name mismatch in model
    E0241 = "E0241"  # Duplicate ID definition
    E0223 = "E0223"  # Prelude symbol load failed
    E0224 = "E0224"  # Model rebuild failed (warning)
    E0232 = "E0232"  # Reserved field 'id' used
    E0233 = "E0233"  # Invalid model type (not BaseModel or Enum)
    
    # L3: Validator Errors (E03xx) - Reference: 40-59, Schema: 60-79
    E0341 = "E0341"  # Reference resolution failed
    E0342 = "E0342"  # Circular dependency detected
    E0361 = "E0361"  # Schema validation failed
    E0362 = "E0362"  # Type mismatch in Ref[T]
    E0343 = "E0343"  # Evolution target not found
    E0363 = "E0363"  # ID conflict in body vs signature
    E0364 = "E0364"  # Missing model class
    E0365 = "E0365"  # Query syntax error
    
    # L4: Spec Errors (E04xx) - Execution: 20-39
    E0421 = "E0421"  # Spec execution failed
    E0422 = "E0422"  # Oracle execution failed
    E0423 = "E0423"  # Spec target not found
    E0424 = "E0424"  # Spec assertion failed
    
    # System Errors (E09xx) - System: 80-99
    E0981 = "E0981"  # Internal compiler error
    E0982 = "E0982"  # File system error
    E0983 = "E0983"  # Configuration error
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def stage(self) -> str:
        """Get the compilation stage for this error code."""
        stage_map = {
            "01": "L1-Scanner",
            "02": "L2-Linker", 
            "03": "L3-Validator",
            "04": "L4-Spec",
            "09": "System"
        }
        return stage_map.get(self.value[1:3], "Unknown")
    
    @property
    def category(self) -> str:
        """Get the error category based on the second digit."""
        cat_digit = self.value[3]
        # Map to broader categories
        if cat_digit in "01":
            return "Syntax/Parse"
        elif cat_digit in "23":
            return "Execution"
        elif cat_digit in "45":
            return "Reference/Link"
        elif cat_digit in "67":
            return "Schema/Type"
        elif cat_digit in "89":
            return "System"
        return "Unknown"
    
    @property
    def default_level(self) -> ErrorLevel:
        """Get the default severity level for this error code."""
        # Most errors are ERROR level by default
        warning_codes = {ErrorCode.E0224}  # Model rebuild warning
        return ErrorLevel.WARNING if self in warning_codes else ErrorLevel.ERROR


# Error message templates for consistent messaging
ERROR_TEMPLATES: Dict[ErrorCode, str] = {
    # L1: Scanner
    ErrorCode.E0101: "Parse error: {details}",
    ErrorCode.E0102: "Config block in wrong location: {details}",
    ErrorCode.E0103: "Nested list anti-pattern detected: {details}",
    ErrorCode.E0104: "Cannot read file: {details}",
    ErrorCode.E0105: "Document structure error: {details}",
    
    # L2: Linker
    ErrorCode.E0221: "Model execution failed: {details}",
    ErrorCode.E0222: "Config execution failed: {details}",
    ErrorCode.E0231: "Model block ID '{id}' does not match defined class name",
    ErrorCode.E0241: "Duplicate ID '{id}' defined",
    ErrorCode.E0223: "Failed to load prelude symbol '{symbol}': {details}",
    ErrorCode.E0224: "Model rebuild warning: {details}",
    ErrorCode.E0232: "Model '{model}' uses reserved field 'id'",
    ErrorCode.E0233: "'{name}' is not a valid Pydantic model or Enum",
    
    # L3: Validator
    ErrorCode.E0341: "Cannot resolve reference: {details}",
    ErrorCode.E0342: "Circular dependency: {details}",
    ErrorCode.E0361: "Schema violation in {entity}: {details}",
    ErrorCode.E0362: "Type mismatch: field '{field}' expects Ref[{expected}], but '{value}' is '{actual}'",
    ErrorCode.E0343: "Evolution target not found: '{target}'",
    ErrorCode.E0363: "ID conflict: System ID must be in signature, not body",
    ErrorCode.E0364: "Model class '{model}' not found",
    ErrorCode.E0365: "Query syntax error: {details}",
    
    # L4: Spec
    ErrorCode.E0421: "Spec execution failed: {details}",
    ErrorCode.E0422: "Oracle execution failed: {details}",
    ErrorCode.E0423: "Spec target not found: {details}",
    ErrorCode.E0424: "Spec assertion failed: {details}",
    
    # System
    ErrorCode.E0981: "Internal error: {details}",
    ErrorCode.E0982: "File system error: {details}",
    ErrorCode.E0983: "Configuration error: {details}",
}


class TypedownError(Exception):
    """
    Base class for all Typedown errors with machine-readable codes.
    
    Attributes:
        message: Human-readable error message
        code: Machine-readable error code (e.g., E0101)
        level: Severity level (error, warning, info, hint)
        location: Optional source location information
        details: Additional structured data about the error
    """
    
    def __init__(
        self, 
        message: str, 
        code: ErrorCode = ErrorCode.E0981,
        level: Optional[ErrorLevel] = None,
        location: Optional[Any] = None,
        severity: Optional[str] = None,  # Backwards compatibility
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code if isinstance(code, ErrorCode) else ErrorCode.E0901
        
        # Support both new 'level' and legacy 'severity' parameters
        if level is not None:
            self.level = level
        elif severity is not None:
            self.level = ErrorLevel(severity)
        else:
            self.level = self.code.default_level
            
        self.location = location
        self.details = details or {}
    
    @property
    def severity(self) -> str:
        """Legacy property for backwards compatibility."""
        return self.level.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization."""
        loc = None
        if self.location:
            loc = {
                "file_path": str(getattr(self.location, "file_path", "")),
                "line_start": getattr(self.location, "line_start", 0),
                "col_start": getattr(self.location, "col_start", 0),
                "line_end": getattr(self.location, "line_end", 0),
                "col_end": getattr(self.location, "col_end", 0),
            }
        
        return {
            "code": str(self.code),
            "level": self.level.value,
            "severity": self.severity,  # For backwards compatibility
            "message": self.message,
            "stage": self.code.stage,
            "category": self.code.category,
            "location": loc,
            "details": self.details
        }
    
    @classmethod
    def from_template(
        cls,
        code: ErrorCode,
        location: Optional[Any] = None,
        level: Optional[ErrorLevel] = None,
        **kwargs
    ) -> "TypedownError":
        """Create an error from a template with formatted message."""
        template = ERROR_TEMPLATES.get(code, "{details}")
        try:
            message = template.format(**kwargs)
        except KeyError:
            # Fallback if template formatting fails
            message = f"[{code}] {kwargs.get('details', 'Unknown error')}"
        
        return cls(
            message=message,
            code=code,
            level=level,
            location=location,
            details=kwargs
        )


# Legacy error classes - maintained for backwards compatibility
# These now include appropriate error codes

class CycleError(TypedownError):
    """Raised when a circular dependency is detected."""
    def __init__(self, message: str, location: Optional[Any] = None, **kwargs):
        super().__init__(
            message=message,
            code=ErrorCode.E0342,
            level=ErrorLevel.ERROR,
            location=location,
            details={"cycle": message, **kwargs}
        )


class ReferenceError(TypedownError):
    """Raised when a referenced symbol is missing."""
    def __init__(self, message: str, location: Optional[Any] = None, **kwargs):
        super().__init__(
            message=message,
            code=ErrorCode.E0341,
            level=ErrorLevel.ERROR,
            location=location,
            details={"reference": message, **kwargs}
        )


class QueryError(TypedownError):
    """Raised when a query cannot be resolved (syntax or semantic)."""
    def __init__(self, message: str, location: Optional[Any] = None, **kwargs):
        super().__init__(
            message=message,
            code=ErrorCode.E0365,
            level=ErrorLevel.ERROR,
            location=location,
            details={"query": message, **kwargs}
        )


# Stage-specific error factory functions for convenient error creation

def scanner_error(
    code: ErrorCode,
    message: Optional[str] = None,
    location: Optional[Any] = None,
    level: Optional[ErrorLevel] = None,
    **kwargs
) -> TypedownError:
    """Create a Scanner (L1) error."""
    if message is None:
        return TypedownError.from_template(code, location, level, **kwargs)
    return TypedownError(message, code, level, location, details=kwargs)


def linker_error(
    code: ErrorCode,
    message: Optional[str] = None,
    location: Optional[Any] = None,
    level: Optional[ErrorLevel] = None,
    **kwargs
) -> TypedownError:
    """Create a Linker (L2) error."""
    if message is None:
        return TypedownError.from_template(code, location, level, **kwargs)
    return TypedownError(message, code, level, location, details=kwargs)


def validator_error(
    code: ErrorCode,
    message: Optional[str] = None,
    location: Optional[Any] = None,
    level: Optional[ErrorLevel] = None,
    **kwargs
) -> TypedownError:
    """Create a Validator (L3) error."""
    if message is None:
        return TypedownError.from_template(code, location, level, **kwargs)
    return TypedownError(message, code, level, location, details=kwargs)


def spec_error(
    code: ErrorCode,
    message: Optional[str] = None,
    location: Optional[Any] = None,
    level: Optional[ErrorLevel] = None,
    **kwargs
) -> TypedownError:
    """Create a Spec (L4) error."""
    if message is None:
        return TypedownError.from_template(code, location, level, **kwargs)
    return TypedownError(message, code, level, location, details=kwargs)


# Diagnostic collection and reporting

@dataclass
class DiagnosticReport:
    """Collection of diagnostics from a compilation run."""
    errors: List[TypedownError] = field(default_factory=list)
    
    def add(self, error: TypedownError) -> None:
        """Add a diagnostic."""
        self.errors.append(error)
    
    def extend(self, errors: List[TypedownError]) -> None:
        """Add multiple diagnostics."""
        self.errors.extend(errors)
    
    def has_errors(self) -> bool:
        """Check if there are any ERROR level diagnostics."""
        return any(e.level == ErrorLevel.ERROR for e in self.errors)
    
    def by_level(self, level: ErrorLevel) -> List[TypedownError]:
        """Get diagnostics filtered by level."""
        return [e for e in self.errors if e.level == level]
    
    def by_code(self, code: ErrorCode) -> List[TypedownError]:
        """Get diagnostics filtered by error code."""
        return [e for e in self.errors if e.code == code]
    
    def by_stage(self, stage: str) -> List[TypedownError]:
        """Get diagnostics filtered by compilation stage."""
        return [e for e in self.errors if e.code.stage == stage]
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert all diagnostics to list of dictionaries."""
        return [e.to_dict() for e in self.errors]
    
    def __iter__(self):
        """Allow iterating over errors directly."""
        return iter(self.errors)
    
    def __len__(self) -> int:
        """Return the number of diagnostics."""
        return len(self.errors)


def print_diagnostic(console: Console, error: TypedownError):
    """Print a diagnostic message in a compiler-like style."""
    loc_str = "Unknown location"
    if error.location:
        # Assuming SourceLocation structure
        file_path = getattr(error.location, "file_path", "??")
        line = getattr(error.location, "line_start", "?")
        col = getattr(error.location, "col_start", "?")
        loc_str = f"{file_path}:{line}:{col}"

    # Color based on level
    color_map = {
        ErrorLevel.ERROR: "red",
        ErrorLevel.WARNING: "yellow", 
        ErrorLevel.INFO: "blue",
        ErrorLevel.HINT: "dim"
    }
    color = color_map.get(error.level, "red")
    
    # Format: [CODE] Level: Message
    console.print(f"[{color} bold][{error.code}] {error.level.value.capitalize()}: {error.message}[/{color} bold]")
    console.print(f"  --> {loc_str}")
    
    if error.details:
        for key, value in error.details.items():
            if key not in ["details", "message"] and value:
                console.print(f"  [dim]{key}: {value}[/dim]")
    
    if hasattr(error, '__cause__') and error.__cause__:
        console.print(f"  [dim]Caused by: {error.__cause__}[/dim]")


def print_diagnostic_report(console: Console, report: DiagnosticReport):
    """Print a full diagnostic report."""
    if not report.errors:
        console.print("[green]✓ No diagnostics[/green]")
        return
    
    # Group by level
    errors = report.by_level(ErrorLevel.ERROR)
    warnings = report.by_level(ErrorLevel.WARNING)
    infos = report.by_level(ErrorLevel.INFO)
    hints = report.by_level(ErrorLevel.HINT)
    
    console.print(f"\n[bold]Diagnostic Report:[/bold]")
    console.print(f"  [red]Errors: {len(errors)}[/red]")
    console.print(f"  [yellow]Warnings: {len(warnings)}[/yellow]")
    console.print(f"  [blue]Info: {len(infos)}[/blue]")
    console.print(f"  [dim]Hints: {len(hints)}[/dim]")
    console.print("")
    
    for error in report.errors:
        print_diagnostic(console, error)
        console.print("")

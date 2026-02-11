import json
from pathlib import Path
from typing import Any, List
from pydantic import BaseModel
import typer

from typedown.core.base.errors import TypedownError, DiagnosticReport

def json_serializer(obj: Any) -> Any:
    """JSON serializer for objects not serializable by default json code"""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: json_serializer(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_serializer(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, TypedownError):
        # Use the new to_dict() method which includes all error code info
        return obj.to_dict()
    if isinstance(obj, DiagnosticReport):
        # Serialize diagnostic report to list of error dicts
        return obj.to_dict_list()
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if hasattr(obj, "resolved_data"):
        return json_serializer(obj.resolved_data)
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    # Handle Sets
    if isinstance(obj, set):
        return list(obj)
    # Handle Classes (Pydantic Models)
    if isinstance(obj, type) and issubclass(obj, BaseModel):
        return obj.model_json_schema()
        
    import dataclasses
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
        
    try:
        import attrs
        if attrs.has(obj):
            return attrs.asdict(obj)
    except ImportError:
        pass

    return str(obj)

def output_result(data: Any, as_json: bool, console_printer=None):
    """
    Standard output handler.
    If as_json is True, prints JSON to stdout (via typer.echo).
    Otherwise calls the console_printer function.
    """
    if as_json:
        typer.echo(json.dumps(data, default=json_serializer, indent=2, ensure_ascii=False))
    else:
        if console_printer:
            console_printer(data)


def format_diagnostics_for_output(
    scanner_diagnostics: Any,
    linker_diagnostics: Any = None,
    validator_diagnostics: Any = None,
    spec_diagnostics: Any = None
) -> dict:
    """
    Format all diagnostics from compilation stages for structured output.
    
    Returns a dictionary with:
    - summary: counts by level and stage
    - diagnostics: list of all diagnostic dicts
    """
    all_diagnostics = []
    
    def collect(diags):
        if isinstance(diags, DiagnosticReport):
            all_diagnostics.extend(diags.to_dict_list())
        elif isinstance(diags, list):
            for d in diags:
                if isinstance(d, TypedownError):
                    all_diagnostics.append(d.to_dict())
                elif isinstance(d, dict):
                    all_diagnostics.append(d)
    
    collect(scanner_diagnostics)
    collect(linker_diagnostics)
    collect(validator_diagnostics)
    collect(spec_diagnostics)
    
    # Build summary
    summary = {
        "total": len(all_diagnostics),
        "by_level": {"error": 0, "warning": 0, "info": 0, "hint": 0},
        "by_stage": {
            "L1-Scanner": 0,
            "L2-Linker": 0,
            "L3-Validator": 0,
            "L4-Spec": 0,
            "System": 0
        }
    }
    
    for diag in all_diagnostics:
        level = diag.get("level", "error")
        stage = diag.get("stage", "Unknown")
        
        if level in summary["by_level"]:
            summary["by_level"][level] += 1
        if stage in summary["by_stage"]:
            summary["by_stage"][stage] += 1
    
    return {
        "summary": summary,
        "diagnostics": all_diagnostics
    }

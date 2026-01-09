import json
from pathlib import Path
from typing import Any, List
from pydantic import BaseModel
import typer

from typedown.core.base.errors import TypedownError

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
        loc = None
        if obj.location:
            loc = {
                "file_path": str(getattr(obj.location, "file_path", "")),
                "line_start": getattr(obj.location, "line_start", 0),
                "col_start": getattr(obj.location, "col_start", 0),
                "line_end": getattr(obj.location, "line_end", 0),
                "col_end": getattr(obj.location, "col_end", 0),
            }
        return {
            "severity": obj.severity,
            "message": obj.message,
            "location": loc
        }
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

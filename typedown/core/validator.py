from typing import Any, Dict, Type
from pydantic import BaseModel, ValidationError
from rich.console import Console
from typedown.core.loader import ClassRegistry

console = Console()

class Validator:
    def __init__(self, registry: ClassRegistry):
        self.registry = registry

    def validate(self, entity_id: str, class_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data against the Pydantic model found in registry.
        Returns the dumped model data (dict) if successful.
        """
        model_cls = self.registry.get(class_name)
        if not model_cls:
            # If no class found, we cannot validate. 
            # Depending on strictness, we might warn or error.
            # For MVP, let's warn and return raw data.
            console.print(f"[yellow]Warning:[/yellow] No model class found for '{class_name}' (Entity: {entity_id}). Validation skipped.")
            return data

        try:
            # Instantiate and Validate
            instance = model_cls(**data)
            return instance.model_dump()
        except ValidationError as e:
            console.print(f"[bold red]Validation Error[/bold red] in Entity '{entity_id}' ({class_name}):")
            for err in e.errors():
                loc = ".".join(str(l) for l in err['loc'])
                console.print(f"  - [cyan]{loc}[/cyan]: {err['msg']}")
            # We raise so the build fails? Or return partial?
            # Let's fail fast for now.
            raise e

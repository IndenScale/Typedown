from typing import Dict, List, Any, Callable
from pathlib import Path
import importlib.util
import sys
import os
from rich.console import Console

from typedown.core.ast import Project, SpecBlock, EntityBlock
from typedown.core.errors import TypedownError, print_diagnostic

# Use stderr for console output only in LSP mode
use_stderr = os.getenv("TYPEDOWN_LSP_MODE") == "1"
console = Console(stderr=use_stderr)

class WrapperContext:
    """Context object passed to spec check functions."""
    def __init__(self, project: Project):
        self.project = project
        self.avg_hp = 0 # Example derived metric

class SpecRunner:
    def __init__(self, project: Project, root: Path):
        self.project = project
        self.root = root
        self.loaded_modules = {}

    def run(self, tags: List[str] = []) -> bool:
        """
        Run all specs in the project.
        Returns True if all critical checks pass, False otherwise.
        """
        all_passed = True
        context = WrapperContext(self.project)
        
        console.print(f"[blue]Running {len(self.project.spec_table)} specs...[/blue]")
        
        for spec_id, spec_block in self.project.spec_table.items():
            # 1. Determine Severity
            severity = "warning"
            if isinstance(spec_block.severity, str):
                severity = spec_block.severity
            elif isinstance(spec_block.severity, dict):
                severity = spec_block.severity.get("default", "warning")
                for tag in tags:
                    if tag in spec_block.severity:
                        severity = spec_block.severity[tag]
                        break
            
            # 2. Select Targets
            targets = self._select_targets(spec_block.target)
            if not targets:
                continue
                
            # 3. Load Check Function
            check_func = self._load_check_function(spec_block.check)
            if not check_func:
                console.print(f"[red]Error:[/red] Spec '{spec_id}' refers to missing function '{spec_block.check}'")
                all_passed = False
                continue
                
            # 4. Execute Check
            for entity in targets:
                try:
                    result = check_func(entity, context, spec_block.params)
                    
                    success = True
                    message = ""
                    
                    if isinstance(result, bool):
                        success = result
                    elif isinstance(result, tuple):
                        success = result[0]
                        message = result[1]
                        
                    if not success:
                        self._report_failure(spec_id, spec_block, entity, message, severity)
                        if severity == "error":
                            all_passed = False
                            
                except Exception as e:
                    console.print(f"[red]Exception running spec '{spec_id}' on '{entity.id}':[/red] {e}")
                    import traceback
                    traceback.print_exc()
                    all_passed = False

        return all_passed

    def _select_targets(self, selector: str) -> List[EntityBlock]:
        """
        Simple Selector Engine:
        - "entity:ClassName"
        - "tag:Tag" (TODO)
        - "*" (All)
        """
        results = []
        if selector == "*":
            return list(self.project.symbol_table.values())
            
        if selector.startswith("entity:"):
            target_class = selector[len("entity:") :].strip()
            for entity in self.project.symbol_table.values():
                if entity.class_name == target_class:
                    results.append(entity)
        else:
             # Fallback: Assume it's a class name
             for entity in self.project.symbol_table.values():
                if entity.class_name == selector:
                    results.append(entity)
                    
        return results

    def _load_check_function(self, path: str) -> Callable:
        """
        Load python function from string "module.submodule.func_name".
        """
        if path in self.loaded_modules:
            return self.loaded_modules[path]
            
        parts = path.split(".")
        func_name = parts[-1]
        module_path = ".".join(parts[:-1])
        
        try:
            if str(self.root) not in sys.path:
                sys.path.insert(0, str(self.root))
                
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            self.loaded_modules[path] = func
            return func
        except (ImportError, AttributeError) as e:
            console.print(f"[yellow]Failed to load check function '{path}': {e}[/yellow]")
            return None

    def _report_failure(self, spec_id: str, spec: SpecBlock, entity: EntityBlock, message: str, severity: str):
        # Construct a descriptive message
        full_msg = f"[{spec_id}] {message}" if message else f"[{spec_id}] Failed check"
        
        # Create TypedownError (which wraps the location)
        # We point to the ENTITY that failed, because that's what the user needs to fix.
        error = TypedownError(
            message=full_msg,
            location=entity.location,
            severity=severity
        )
        
        print_diagnostic(console, error)

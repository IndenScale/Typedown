import sys
import os
import logging
import importlib
from pathlib import Path
from typing import Dict, Any, Type, List, Optional
from pydantic import BaseModel
from rich.console import Console

console = Console()

class ClassRegistry:
    """
    Manages Pydantic classes registered for a specific scope.
    """
    def __init__(self, parent_registry: Optional['ClassRegistry'] = None):
        self._classes: Dict[str, Type[BaseModel]] = {}
        self._parent = parent_registry
        if parent_registry:
            self._classes.update(parent_registry._classes) # Inherit parent classes
            
    def register(self, name: str, cls: Type[BaseModel]):
        if not issubclass(cls, BaseModel):
            console.print(f"[yellow]Warning: Attempted to register non-Pydantic class '{name}'[/yellow]")
            return
        self._classes[name] = cls
        
    def get(self, name: str) -> Optional[Type[BaseModel]]:
        return self._classes.get(name)

    def all_classes(self) -> Dict[str, Type[BaseModel]]:
        return self._classes

    @property
    def models(self) -> Dict[str, Type[BaseModel]]:
        return self._classes

class ContextManager:
    """
    Manages the execution context (Python scripts, Pydantic class registration)
    for different scopes (directories/documents) in a cascading manner.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._cache: Dict[Path, ClassRegistry] = {} # Cache registry per config.td path

    def _execute_script(self, script_code: str, script_path: Path, current_registry: ClassRegistry) -> Dict[str, Any]:
        """
        Executes a Python script in a controlled environment and discovers Pydantic models.
        """
        # Create a fresh global and local scope for execution to avoid polluting globals
        # Inherit current sys.path but isolate changes for this script
        
        # We need to make sure the script's directory is in sys.path for relative imports
        script_dir = script_path.parent
        original_sys_path = sys.path[:]
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        
        script_globals = {
            "__builtins__": __builtins__,
            "__file__": str(script_path),
            "__name__": "__typedown_config_script__",
            "__package__": None,
            "__loader__": None,
            "sys": sys,
            "os": os,
            "Path": Path, # Make Pathlib available
            "BaseModel": BaseModel # Make BaseModel available for direct use
        }
        script_locals = script_globals.copy()

        try:
            # Capture output to prevent polluting stdout (which breaks LSP)
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                exec(script_code, script_globals, script_locals)
        except Exception as e:
            # console.print(f"[bold red]Error executing config script in {script_path}:[/bold red] {e}")
            logging.error(f"Error executing config script in {script_path}: {e}")
            raise

        finally:
            sys.path = original_sys_path # Restore sys.path
            
        # Discover Pydantic models after execution
        self._discover_pydantic_models(script_locals, current_registry)
        
        return script_locals # Return the locals for potential future inspection

    def _discover_pydantic_models(self, executed_scope: Dict[str, Any], registry: ClassRegistry):
        """
        Inspects the executed scope for Pydantic BaseModel subclasses and registers them.
        """
        for name, obj in executed_scope.items():
            if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel:
                # console.print(f"[debug] Discovered Pydantic model: {name}")
                registry.register(name, obj)
    
    def get_document_registry(self, doc_path: Path, config_td_docs: Dict[Path, Any], current_doc: Optional[Any] = None) -> ClassRegistry:
        """
        Determines the effective ClassRegistry for a given document by
        cascading config.td scripts from parent directories.
        If current_doc is provided and has model_scripts, they are executed 
        in a child registry extending the config cascade.
        """
        doc_path = doc_path.resolve()
        
        # Find all config.td files in the ancestry of doc_path
        ancestors = list(doc_path.parents)
        ancestors.reverse() # Start from project root towards the document
        
        relevant_config_paths: List[Path] = []
        
        # Include project_root's config.td if exists
        project_root_config = self.project_root / "config.td"
        if project_root_config.is_file() and project_root_config in config_td_docs:
             relevant_config_paths.append(project_root_config)

        for ancestor_dir in ancestors:
            if ancestor_dir == self.project_root:
                continue # Already handled or covered by deeper paths
            
            config_file = ancestor_dir / "config.td"
            if config_file.is_file() and config_file in config_td_docs:
                relevant_config_paths.append(config_file)
        
        # Also include config.td in the same directory as the doc, if it's not a config.td itself
        if doc_path.is_file():
            current_dir_config = doc_path.parent / "config.td"
            if current_dir_config.is_file() and current_dir_config in config_td_docs and current_dir_config not in relevant_config_paths:
                relevant_config_paths.append(current_dir_config)
        elif doc_path.is_dir(): # if doc_path is a directory, its config.td applies
             current_dir_config = doc_path / "config.td"
             if current_dir_config.is_file() and current_dir_config in config_td_docs and current_dir_config not in relevant_config_paths:
                relevant_config_paths.append(current_dir_config)

        # Build the cascading registry
        current_registry: ClassRegistry = ClassRegistry() # Base registry
        
        for config_path in relevant_config_paths:
            if config_path not in self._cache:
                # If not cached, execute script and build new registry
                config_doc = config_td_docs[config_path]
                if config_doc.python_scripts:
                    new_registry = ClassRegistry(parent_registry=current_registry)
                    # For config.td, we only execute the first python script for now
                    self._execute_script(config_doc.python_scripts[0], config_path, new_registry)
                    self._cache[config_path] = new_registry
                else:
                    self._cache[config_path] = ClassRegistry(parent_registry=current_registry) # Cache an empty registry
            
            # Use cached or newly built registry as the base for the next level
            current_registry = self._cache[config_path]
            
        # If the document itself has model definitions (model blocks),
        # create a specialized registry for this document.
        if current_doc and getattr(current_doc, "model_scripts", None):
            doc_registry = ClassRegistry(parent_registry=current_registry)
            for script in current_doc.model_scripts:
                self._execute_script(script, doc_path, doc_registry)
            return doc_registry
            
        return current_registry

import sys
import importlib
from pathlib import Path
from typing import Dict, Any, Type, Optional, Union
from pydantic import BaseModel

class ClassRegistry:
    """
    Registry for loaded Pydantic classes.
    """
    def __init__(self):
        self._classes: Dict[str, Type[BaseModel]] = {}

    def register(self, name: str, cls: Type[BaseModel]):
        self._classes[name] = cls

    def get(self, name: str) -> Optional[Type[BaseModel]]:
        return self._classes.get(name)

class Loader:
    """
    Handles dynamic importing of Python modules from the project.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.registry = ClassRegistry()
        self._setup_sys_path()

    def _setup_sys_path(self):
        """
        Add project root to sys.path so we can import 'models.xxx'.
        """
        root_str = str(self.project_root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)

    def load_imports(self, imports_config: list[dict]):
        """
        Process a list of import definitions.
        Format: 
          - {'from': 'models.user', 'import': 'User', 'as': 'UserV1'}
          - {'from': 'models.schema', 'import': ['User', 'Post']}
        """
        if not imports_config:
            return

        for item in imports_config:
            module_name = item.get("from")
            imports = item.get("import") 
            
            if not module_name or not imports:
                continue
                
            try:
                # Dynamic Import
                module = importlib.import_module(module_name)
                
                # Handle single import (str) or multiple (list)
                if isinstance(imports, str):
                    class_name = imports
                    alias = item.get("as", class_name)
                    self._register_class(module, class_name, alias)
                elif isinstance(imports, list):
                    for class_name in imports:
                        # Aliasing not supported for list imports
                        self._register_class(module, class_name, class_name)
                
            except ImportError as e:
                # TODO: Log error properly
                sys.stderr.write(f"Failed to import module {module_name}: {e}\n")

    def _register_class(self, module, class_name: str, alias: str):
        try:
            cls = getattr(module, class_name)
            if isinstance(cls, type):
                 self.registry.register(alias, cls)
            else:
                 sys.stderr.write(f"Warning: {class_name} is not a class.\n")
        except AttributeError:
            sys.stderr.write(f"Class {class_name} not found in module {module.__name__}\n")
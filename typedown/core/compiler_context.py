import sys
import importlib.abc
import importlib.util
from pathlib import Path
from typing import Optional
from typedown.core.resolver import Resolver

class TypedownMetaFinder(importlib.abc.MetaPathFinder):
    """
    Custom Import Hook to support mapped imports like '@lib.math'.
    Hooks into Python's native `import` system.
    """
    def __init__(self, resolver: Resolver):
        self.resolver = resolver

    def find_spec(self, fullname: str, path=None, target=None):
        """
        Called by Python when importing a module.
        We intercept if the name matches one of our mappings.
        """
        # We only care if the import might be resolvable by our resolver (e.g. starts with @ or is a managed path)
        # But our resolver handles everything via config.
        
        try:
            # Attempt to resolve using our configuration
            # 'fullname' is "lib.math" or "@lib.math"
            
            # Optimization: only try if it looks like a virtual import or if normal import failed?
            # For robustness, we try to resolve everything that fits our config patterns.
            # But we must avoid intercepting standard libs (os, sys).
            
            # Heuristic: Check if fullname starts with a known dependency key in config
            is_managed = False
            for key in self.resolver.config.dependencies.keys():
                if fullname == key or fullname.startswith(key + "."):
                    is_managed = True
                    break
            
            if not is_managed:
                return None

            resolved_path = self.resolver.resolve(fullname)
            
            if not resolved_path.exists():
                return None
                
            # Create module spec
            return importlib.util.spec_from_file_location(fullname, resolved_path)
            
        except (FileNotFoundError, ValueError):
            # Not found by us, let other finders try
            return None

class CompilerContext:
    """
    Manages the execution environment for Typedown.
    Installs and uninstalls the import hook.
    """
    def __init__(self, root: Path):
        self.resolver = Resolver(root)
        self.finder = TypedownMetaFinder(self.resolver)
        
    def __enter__(self):
        # 1. Install the hook at the front of sys.meta_path
        sys.meta_path.insert(0, self.finder)
        
        # 2. Add project root to sys.path to support standard local imports
        # during runtime execution of models/preludes.
        self._old_path = list(sys.path)
        sys.path.insert(0, str(self.resolver.project_root))
        
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up
        if self.finder in sys.meta_path:
            sys.meta_path.remove(self.finder)
        sys.path = self._old_path

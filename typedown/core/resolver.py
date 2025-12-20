from pathlib import Path
from typing import Optional, Dict, Tuple
import sys

from typedown.core.config import TypedownConfig

class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected in the model/entity graph."""
    pass

class Resolver:
    """
    Compiler Component: Path Resolver & Dependency Manager.
    Responsible for mapping logical import strings (e.g. "@lib.math") to physical file paths.
    """

    def __init__(self, root: Path):
        self.start_root = root.resolve()
        self.project_root, self.config = self._find_project_root(self.start_root)
        
        # Cache for resolved paths to avoid repeated disk I/O
        # import_string -> resolved_absolute_path
        self._resolution_cache: Dict[str, Path] = {}

    def _find_project_root(self, start: Path) -> Tuple[Path, TypedownConfig]:
        """
        Climb up the directory tree to find `typedown.toml`.
        If not found, defaults to start_path and empty config.
        """
        current = start
        while True:
            config_file = current / "typedown.toml"
            if config_file.exists():
                try:
                    config = TypedownConfig.load(config_file)
                    return current, config
                except Exception as e:
                    # TODO: Log warning via proper logger
                    print(f"Warning: Failed to parse {config_file}: {e}", file=sys.stderr)
            
            parent = current.parent
            if parent == current: # Reached filesystem root
                break
            current = parent
            
        # Fallback: No config found, treat start_dir as root with default config
        return start, TypedownConfig()

    def resolve(self, source: str, relative_to: Optional[Path] = None) -> Path:
        """
        Resolve an import string to a physical file path.
        
        Args:
            source: The import string, e.g., "@lib.math", "models.user", "./utils"
            relative_to: The file path doing the importing (for relative imports)
            
        Returns:
            Absolute Path to the target file (.py or .td)
            
        Raises:
            FileNotFoundError: If the module cannot be found.
        """
        if source in self._resolution_cache:
            return self._resolution_cache[source]

        # 1. Handle Virtual Namespace Mappings (e.g., "@lib")
        # We look for the longest matching prefix in dependencies
        matched_dep_path = None
        remaining_parts = source
        
        # Sort dependencies by key length descending to match specific prefixes first
        sorted_deps = sorted(self.config.dependencies.items(), key=lambda x: len(x[0]), reverse=True)
        
        for dep_name, dep_config in sorted_deps:
            if source == dep_name or source.startswith(dep_name + "."):
                # Found a match!
                if dep_config.path:
                    # Resolve dependency root relative to the project root (where typedown.toml is)
                    dep_root = (self.project_root / dep_config.path).resolve()
                    
                    if source == dep_name:
                        matched_dep_path = dep_root
                        remaining_parts = ""
                    else:
                        # Remove prefix and dot
                        matched_dep_path = dep_root
                        remaining_parts = source[len(dep_name) + 1:] 
                    break
        
        # 2. Construct search base
        if matched_dep_path:
            # We are inside a mapped dependency
            search_base = matched_dep_path
        else:
            # Standard import
            if source.startswith("."):
                # Relative import
                if relative_to is None:
                     raise ValueError(f"Cannot resolve relative import '{source}' without context.")
                search_base = relative_to.parent
                # Handling ".." is tricky with string split, simpler to use resolve() later
                # For now, simplistic handling of "./" logic via relative conversion
                # But Python relative imports use dots differently (from . import x). 
                # Here we assume file-path like relative imports from standard 'import:' block?
                # If it's python import 'from .mod import', source is usually absolute in AST or handled by python.
                # Let's assume 'source' is the module path.
                remaining_parts = source
            else:
                # Absolute import relative to project root (default behavior)
                search_base = self.project_root
                remaining_parts = source

        # 3. Resolve file path from parts
        # "math" -> "math.py" or "math.td" or "math/__init__.py"
        path_parts = remaining_parts.split(".") if remaining_parts else []
        
        current_path = search_base
        for part in path_parts:
            current_path = current_path / part
            
        # 4. Probe for extensions
        candidates = [
            current_path.with_suffix(".py"),
            current_path.with_suffix(".td"),
            current_path.with_suffix(".md"),
            current_path / "__init__.py",
            current_path / "index.td",
             current_path / "index.md"
        ]
        
        # If it's a direct directory mapping (like import @lib), current_path might be the dir itself
        if current_path.is_dir():
             candidates.insert(0, current_path / "__init__.py")

        for candidate in candidates:
            if candidate.exists():
                resolved = candidate.resolve()
                self._resolution_cache[source] = resolved
                return resolved

        raise FileNotFoundError(f"Could not resolve module '{source}' from '{relative_to or self.project_root}'")
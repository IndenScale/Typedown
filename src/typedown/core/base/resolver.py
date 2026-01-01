from pathlib import Path
from typing import Optional
from typedown.core.base.config import TypedownConfig

class Resolver:
    """
    Manages path resolution for dependencies and imports.
    """
    def __init__(self, root: Path, config: Optional[TypedownConfig] = None):
        self.project_root = root.resolve()
        if config:
            self.config = config
        else:
            # Lazy load config if not provided, for context bootstrap
            # Assuming 'docs/config.td' or 'typedown.toml'
            # Here we default to typedown.toml standard
            self.config = TypedownConfig.load(self.project_root / "typedown.toml")

    def resolve(self, import_name: str) -> Path:
        """
        Resolves a python import string to a physical file path.
        e.g. "lib.math" -> /path/to/project/lib/math.py
        
        Supports dependency aliases from config.
        """
        # 1. Check direct config mapping
        # "my_lib" -> "libs/my_lib"
        path = self.config.get_dependency_path(import_name, self.project_root)
        if path:
            # It's a directory package or file?
            if path.is_dir():
                # mapping to dir, check for __init__
                return path / "__init__.py"
            return path
            
        # 2. Check prefix mapping
        # "my_lib.utils" -> resolve("my_lib") / "utils.py"
        parts = import_name.split(".")
        if len(parts) > 1:
            root_pkg = parts[0]
            root_path = self.config.get_dependency_path(root_pkg, self.project_root)
            if root_path:
                # Append remainder
                sub_path = root_path.joinpath(*parts[1:])
                # Check .py
                py_file = sub_path.with_suffix(".py")
                if py_file.exists():
                    return py_file
                # Check dir package
                if sub_path.is_dir() and (sub_path / "__init__.py").exists():
                    return sub_path / "__init__.py"

        # 3. Default internal resolution (relative to root)
        # "models.user" -> root/models/user.py
        local_path = self.project_root.joinpath(*parts)
        py_file = local_path.with_suffix(".py")
        if py_file.exists():
            return py_file
        
        if local_path.is_dir() and (local_path / "__init__.py").exists():
            return local_path / "__init__.py"
            
        raise FileNotFoundError(f"Could not resolve import '{import_name}'")

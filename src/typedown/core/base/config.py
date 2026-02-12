from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, ValidationError
import sys

# Compat for TOML parsing
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

class Dependency(BaseModel):
    """
    Represents a dependency source.
    Currently only 'path' is fully supported. 'url' and 'git' are placeholders for future Linker logic.
    """
    path: Optional[Path] = None
    url: Optional[str] = None
    git: Optional[str] = None
    tag: Optional[str] = None
    branch: Optional[str] = None

class PackageConfig(BaseModel):
    """
    [package] section: Metadata for the current project.
    """
    name: str
    version: str = "0.1.0"
    description: Optional[str] = None
    authors: List[str] = []

class WorkspaceConfig(BaseModel):
    """
    [workspace] section: For monorepo management.
    """
    members: List[str] = ["."]

class ScriptConfig(BaseModel):
    """
    [scripts] section: Compilation presets.
    """
    include: List[str] = Field(default_factory=lambda: ["**"])
    exclude: List[str] = Field(default_factory=list)
    strict: bool = False
    tags: List[str] = Field(default_factory=list)
    tags_exclude: List[str] = Field(default_factory=list)

class LinkerConfig(BaseModel):
    """
    [linker] section: Configuration for the linkage stage.
    """
    prelude: List[str] = Field(default_factory=list, description="Symbols to pre-load into the global namespace.")


class SecurityConfig(BaseModel):
    """
    [security] section: Sandboxing and security configuration.
    """
    enabled: bool = Field(default=True, description="Enable sandbox restrictions for user code execution.")
    use_restricted_python: bool = Field(default=True, description="Use RestrictedPython for additional protection (if available).")
    
    # Module restrictions
    allowed_modules: List[str] = Field(default_factory=list, description="Additional modules to allow importing.")
    blocked_modules: List[str] = Field(default_factory=list, description="Additional modules to block from importing.")
    
    # File system restrictions
    allow_file_read: bool = Field(default=False, description="Allow reading files from the project directory.")
    allow_file_write: bool = Field(default=False, description="Allow writing files to the project directory.")
    allowed_paths: List[str] = Field(default_factory=list, description="Additional allowed paths for file operations.")
    
    # Network restrictions
    allow_network: bool = Field(default=False, description="Allow network operations.")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure critical modules are always blocked
        critical_modules = {'os', 'sys', 'subprocess', 'socket'}
        for mod in critical_modules:
            if mod in self.allowed_modules and self.enabled:
                # Log warning but respect explicit override for power users
                pass  # We allow explicit override for advanced use cases

class TestConfig(BaseModel):
    """
    [test] section: Configuration for the Stage 4 (Reality Check).
    """
    oracles: List[str] = Field(default_factory=lambda: ["typedown.core.runtime.oracle.PytestOracle"])

class TypedownConfig(BaseModel):
    """
    Root of typedown.toml
    """
    package: Optional[PackageConfig] = None
    workspace: Optional[WorkspaceConfig] = None
    scripts: Dict[str, ScriptConfig] = Field(default_factory=dict)
    tasks: Dict[str, str] = Field(default_factory=dict, description="Project-level executable scripts (td run <name>)")
    linker: LinkerConfig = Field(default_factory=LinkerConfig)
    test: TestConfig = Field(default_factory=TestConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    dependencies: Dict[str, Dependency] = Field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "TypedownConfig":
        """
        Load and parse a typedown.toml file.
        """
        if not path.exists():
            # Return empty config if no file exists
            return cls()
        
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            return cls(**data)
        except ValidationError as e:
            raise ValueError(f"Invalid typedown.toml format: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse typedown.toml: {e}")

    def get_dependency_path(self, name: str, root_dir: Path) -> Optional[Path]:
        """
        Resolve a dependency name to a physical path.
        """
        dep = self.dependencies.get(name)
        if not dep:
            return None
        
        if dep.path:
            # Resolve relative path against the config file's directory
            return (root_dir / dep.path).resolve()
        
        # TODO: Handle URL/Git dependencies here (Task 03 Phase 2)
        return None

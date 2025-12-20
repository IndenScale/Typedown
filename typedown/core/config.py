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

class TypedownConfig(BaseModel):
    """
    Root of typedown.toml
    """
    package: Optional[PackageConfig] = None
    workspace: Optional[WorkspaceConfig] = None
    scripts: Dict[str, ScriptConfig] = Field(default_factory=dict)
    linker: LinkerConfig = Field(default_factory=LinkerConfig)
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

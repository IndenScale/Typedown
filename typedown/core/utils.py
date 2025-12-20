import os
import fnmatch
from pathlib import Path
from typing import List, Optional

class IgnoreMatcher:
    """
    Handles file ignoring logic supporting .tdignore and .gitignore patterns.
    Uses fnmatch for glob matching.
    """
    
    DEFAULT_IGNORES = [
        ".git", ".svn", ".hg", 
        ".venv", "venv", "env", 
        "__pycache__", 
        "dist", "build", "target",
        ".DS_Store",
        "*.egg-info",
        ".pytest_cache",
        ".mypy_cache"
    ]

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> List[str]:
        patterns = self.DEFAULT_IGNORES.copy()
        
        # Priority 1: .tdignore
        tdignore = self.root_dir / ".tdignore"
        if tdignore.exists():
            patterns.extend(self._read_file(tdignore))
            return patterns # If .tdignore exists, ignore .gitignore? 
                            # Design choice: Usually specialized overrides generic. 
                            # But often we want strict superset.
                            # User said: "If specialized .tdignore exists use this, otherwise respect .gitignore"
                            # This implies exclusive choice.
        
        # Priority 2: .gitignore
        gitignore = self.root_dir / ".gitignore"
        if gitignore.exists():
            patterns.extend(self._read_file(gitignore))
            
        return patterns

    def _read_file(self, path: Path) -> List[str]:
        lines = []
        try:
            content = path.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                lines.append(line)
        except Exception:
            pass
        return lines

    def is_ignored(self, path: Path) -> bool:
        """
        Check if a path should be ignored.
        Path should be absolute or relative to CWD.
        """
        try:
            # Get relative path to root for matching
            rel_path = path.relative_to(self.root_dir)
        except ValueError:
            # Path is not inside root, ignore safe
            return True
            
        path_str = str(rel_path)
        name = path.name
        
        for pattern in self.patterns:
            # Handle directory markers in pattern
            if pattern.endswith("/"):
                # Pattern "dist/" matches directory "dist"
                clean_pattern = pattern.rstrip("/")
                if fnmatch.fnmatch(name, clean_pattern) and path.is_dir():
                    return True
                # Also match paths starting with dist/
                if path_str.startswith(pattern) or (os.sep + pattern) in path_str:
                     return True
            else:
                # Standard match
                if fnmatch.fnmatch(name, pattern):
                    return True
                if fnmatch.fnmatch(path_str, pattern):
                    return True
                    
        return False

def find_project_root(path: Path) -> Path:
    """
    Ascend from path to find the project root.
    Markers: .tdignore, pyproject.toml, .git, GEMINI.md
    """
    path = path.resolve()
    if path.is_file():
        path = path.parent
        
    current = path
    # Stop at system root
    while current != current.parent:
        if (current / "typedown.toml").exists():
            return current
        if (current / ".tdignore").exists():
            return current
        if (current / "pyproject.toml").exists():
            return current
        if (current / ".git").exists():
            return current
        if (current / "GEMINI.md").exists():
            return current
            
        current = current.parent
        
    # Fallback: Just use the initial path
    return path

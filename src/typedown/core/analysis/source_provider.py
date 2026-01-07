from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set
import os

class SourceProvider(ABC):
    """
    Abstract interface for file I/O and discovery.
    Allows injecting a memory overlay for LSP support.
    """

    @abstractmethod
    def get_content(self, path: Path) -> str:
        """Reads content of the file."""
        pass

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Checks if file exists."""
        pass

    @abstractmethod
    def list_files(self, root: Path, extensions: Set[str], ignore_matcher=None) -> Iterator[Path]:
        """
        Recursively finds all matching files in root.
        Args:
            root: Root directory to search.
            extensions: Set of file extensions to include (e.g. {'.td', '.md'}).
            ignore_matcher: Optional object with .is_ignored(path) method.
        """
        pass


class DiskProvider(SourceProvider):
    """Standard provider reading from the physical filesystem."""

    def get_content(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def exists(self, path: Path) -> bool:
        return path.exists()

    def list_files(self, root: Path, extensions: Set[str], ignore_matcher=None) -> Iterator[Path]:
        if root.is_file():
            if root.suffix in extensions:
                 if not ignore_matcher or not ignore_matcher.is_ignored(root):
                     yield root
            return

        for dirpath, dirnames, filenames in os.walk(root):
            # Prune ignored directories in-place
            if ignore_matcher:
                # We need to reconstruct full path for checking ignores
                # os.walk yields dirnames as list of strings.
                # We want to remove ignored ones.
                # Note: modifying dirnames in-place affects subsequent recursion.
                current_root = Path(dirpath)
                
                # Filter dirnames
                # We iterate copy to safe modify original
                to_remove = []
                for d in dirnames:
                    d_path = current_root / d
                    if ignore_matcher.is_ignored(d_path):
                        to_remove.append(d)
                
                for d in to_remove:
                    dirnames.remove(d)

            current_root = Path(dirpath)
            for f in filenames:
                file_path = current_root / f
                if file_path.suffix in extensions:
                    if not ignore_matcher or not ignore_matcher.is_ignored(file_path):
                        yield file_path


class OverlayProvider(SourceProvider):
    """
    Decorator provider that prioritizes in-memory content.
    Used for LSP 'dirty files' support.
    """

    def __init__(self, base: SourceProvider, memory_only: bool = False):
        self.base = base
        self.memory_only = memory_only
        # Stores content of dirty files overlay
        self.overlay: Dict[Path, str] = {}
        # Stores explicitly deleted files (if we want to support 'deleted in memory but exists on disk')
        # For Typedown LSP, we focus on content updates.

    def update_overlay(self, path: Path, content: str):
        self.overlay[path] = content

    def remove_overlay(self, path: Path):
        if path in self.overlay:
            del self.overlay[path]

    def get_content(self, path: Path) -> str:
        if path in self.overlay:
            return self.overlay[path]
        
        if self.memory_only:
            # In memory-only mode, we strictly deny access to base provider
            raise FileNotFoundError(f"File not found in memory overlay: {path}")
            
        return self.base.get_content(path)

    def exists(self, path: Path) -> bool:
        if path in self.overlay:
            return True
            
        if self.memory_only:
            return False
            
        return self.base.exists(path)

    def list_files(self, root: Path, extensions: Set[str], ignore_matcher=None) -> Iterator[Path]:
        seen = set()
        
        # 1. Get files from base (Skip if memory_only)
        if not self.memory_only:
            try:
                for path in self.base.list_files(root, extensions, ignore_matcher):
                    seen.add(path)
                    yield path
            except Exception:
                # Base provider might fail if root doesn't exist on disk, 
                # but we might have overlay files 'inside' it virtually.
                pass

        # 2. Add files from overlay that match criteria and haven't been seen
        for path in self.overlay.keys():
            if path in seen:
                continue
            
            # Check if path is under root
            try:
                # This checks if root is a parent of path
                path.relative_to(root)
            except ValueError:
                continue # Not under root
            
            # Check extension
            if path.suffix not in extensions:
                continue
                
            # Check ignore
            if ignore_matcher and ignore_matcher.is_ignored(path):
                continue
                
            seen.add(path)
            yield path

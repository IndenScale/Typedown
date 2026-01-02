import os
import fnmatch
from pathlib import Path
from typing import Dict, Set, Optional, List, Tuple
from rich.console import Console

from typedown.core.ast import Document, SourceLocation, EntityBlock
from typedown.core.parser import TypedownParser
from typedown.core.base.utils import IgnoreMatcher
from typedown.core.base.config import ScriptConfig
from typedown.core.base.errors import TypedownError

class Scanner:
    def __init__(self, project_root: Path, console: Console):
        self.project_root = project_root
        self.console = console
        self.parser = TypedownParser()
        self.ignore_matcher = IgnoreMatcher(project_root)
        self.diagnostics: List[TypedownError] = []

    def scan(self, target: Path, script: Optional[ScriptConfig] = None) -> Tuple[Dict[Path, Document], Set[Path]]:
        """
        Scans values files in target (or file itself) and returns parsed Documents.
        Filters based on script configuration if provided.
        Returns: (documents_map, set_of_target_files)
        """
        documents: Dict[Path, Document] = {}
        target_files: Set[Path] = set()
        
        strict = script.strict if script else False
        
        self.console.print("  [dim]Stage 1: Scanning content...[/dim]")

        if target.is_file():
            self._process_file(target, documents)
            target_files.add(target)
        else:
            extensions = {".md", ".td"}
            for root, dirs, files in os.walk(target):
                root_path = Path(root)
                
                # Prune ignored dirs
                dirs[:] = [d for d in dirs if not self.ignore_matcher.is_ignored(root_path / d)]
                
                for file in files:
                    file_path = root_path / file
                    if file_path.suffix in extensions:
                        if not self.ignore_matcher.is_ignored(file_path):
                            # Script Logic
                            is_match = True
                            if script:
                                is_match = self._matches_script(file_path, script)
                            
                            # In strict mode, only find files matching the script
                            if strict and not is_match:
                                continue 
                            
                            self._process_file(file_path, documents)
                            
                            if is_match:
                                target_files.add(file_path)

        # ---------------------------------------------------------
        # Critical Fix: Ancestry Config Loading
        # Ensure that config.td files from the target directory up to
        # the project root are loaded, even if they were not explicitly
        # targeted. This ensures "Context as Field" works for leaf files.
        # ---------------------------------------------------------
        
        # Determine the starting directory for upward traversal
        start_dir = target.parent if target.is_file() else target
        try:
            start_dir = start_dir.resolve()
            # Ensure we are within the project
            start_dir.relative_to(self.project_root)
            
            current = start_dir
            while True:
                config_path = current / "config.td"
                
                # Check if exists and not already loaded (to avoid double parsing)
                if config_path.exists() and config_path not in documents:
                    # Note: We do NOT add it to 'target_files' because it's
                    # context infrastructure, not the user's focus target.
                    self._process_file(config_path, documents)
                
                if current == self.project_root:
                    break
                
                # Move up
                if current.parent == current: # System root safety
                    break
                current = current.parent
                
                # Stop if we leave the project root (should be covered by loop condition, but safe)
                if not current.is_relative_to(self.project_root):
                    break
                    
        except (ValueError, RuntimeError):
            # Target might be outside project root, skip auto-loading
            pass

        self.console.print(f"    [green]✓[/green] Found {len(documents)} documents.")
        return documents, target_files

    def _process_file(self, path: Path, documents: Dict[Path, Document]):
        try:
            doc = self.parser.parse(path)
            documents[path] = doc
        except Exception as e:
            self.console.print(f"[yellow]Warning:[/yellow] Failed to parse {path}: {e}")
            self.diagnostics.append(TypedownError(f"Parse Error: {e}", location=SourceLocation(file_path=str(path), line_start=0, line_end=0, col_start=0, col_end=0)))

    def _matches_script(self, path: Path, script: ScriptConfig) -> bool:
        try:
            rel_path = path.relative_to(self.project_root).as_posix()
        except ValueError:
            return False # Path outside project root
            
        # Check Exclude first
        for pat in script.exclude:
            if fnmatch.fnmatch(rel_path, pat):
                return False
                
        # Check Include
        for pat in script.include:
            if fnmatch.fnmatch(rel_path, pat):
                return True
                
        return False

    def lint(self, documents: Dict[Path, Document]) -> bool:
        """
        L1: Syntax & Format Check.
        Validates:
        1. No nested lists in Entity bodies (anti-pattern)
        2. Config blocks only in config.td
        """
        self.console.print("  [dim]L1: Linting...[/dim]")
        
        has_errors = False
        
        for path, doc in documents.items():
            # Check 1: Nested Lists
            for entity in doc.entities:
                if self._check_nested_lists(entity.raw_data):
                    error = TypedownError(
                        f"Nested list detected in entity '{entity.id}'. "
                        f"This is an anti-pattern. Consider extracting to a separate Model.",
                        location=entity.location
                    )
                    self.diagnostics.append(error)
                    has_errors = True

            # Check 2: Config Placement
            if doc.configs:
                if path.name != "config.td":
                    error = TypedownError(
                        f"Config blocks detected in '{path.name}'. "
                        f"Config blocks should only appear in 'config.td' files. "
                        f"Please move this logic to the directory scope.",
                        location=doc.configs[0].location,
                        severity="error"
                    )
                    self.diagnostics.append(error)
                    has_errors = True
        
        if has_errors:
            self.console.print(f"    [red]✗[/red] Lint failed with {len(self.diagnostics)} error(s).")
            return False
        else:
            self.console.print(f"    [green]✓[/green] Lint passed.")
            return True
    
    def _check_nested_lists(self, data: any) -> bool:
        """
        Recursively check if data contains nested lists (list of lists).
        Returns True if nested lists are found.
        """
        if isinstance(data, list):
            for item in data:
                if isinstance(item, list):
                    # Exception 1: Allow Single-Element List of Strings (Reference Sugar)
                    # e.g. [[target]] parses as [['target']]
                    if len(item) == 1 and isinstance(item[0], str):
                        continue
                    
                    # Exception 2: Allow Block-Style List of References
                    # e.g. - [[target]] parses as [['target']] inside the outer list
                    # So item is [['target']]
                    if (len(item) == 1 and isinstance(item[0], list) and 
                        len(item[0]) == 1 and isinstance(item[0][0], str)):
                        continue
                        
                    return True  # Found nested list
                elif isinstance(item, dict):
                    if self._check_nested_lists(item):
                        return True
        elif isinstance(data, dict):
            for value in data.values():
                if self._check_nested_lists(value):
                    return True
        
        return False

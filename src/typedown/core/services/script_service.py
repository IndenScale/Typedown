"""
ScriptService: Script system execution with scope resolution.

Responsibilities:
- Script lookup (File → Directory → Project scope)
- Environment variable injection
- Script execution
"""

from pathlib import Path
from typing import Dict, Optional, TYPE_CHECKING
from rich.console import Console

from typedown.core.ast import Document
from typedown.core.base.config import TypedownConfig
from typedown.core.analysis.script_runner import ScriptRunner
from typedown.core.analysis.source_provider import SourceProvider
from typedown.core.parser import TypedownParser

if TYPE_CHECKING:
    from typedown.core.compiler import Compiler


class ScriptService:
    """
    Service for script execution with scope-based resolution.
    
    Script Resolution (Nearest Winner):
    1. File Scope: Target file's Front Matter
    2. Directory Scope: Directory's config.td (walk up to project root)
    3. Project Scope: typedown.toml tasks
    """
    
    def __init__(
        self,
        project_root: Path,
        config: TypedownConfig,
        source_provider: SourceProvider,
        console: Optional[Console] = None
    ):
        self.project_root = project_root
        self.config = config
        self.source_provider = source_provider
        self.console = console or Console()
        self._parser = TypedownParser()
        self._runner = ScriptRunner(project_root, console)
    
    def run_script(
        self,
        script_name: str,
        target_file: Optional[Path] = None,
        documents: Optional[Dict[Path, Document]] = None,
        dry_run: bool = False
    ) -> int:
        """
        Execute a script with scope-based resolution.
        
        Args:
            script_name: Name of the script to run
            target_file: Target file path (defaults to project root)
            documents: Current documents dictionary (for caching)
            dry_run: If True, only print command without executing
            
        Returns:
            Exit code (0 for success)
        """
        target = target_file or self.project_root
        documents = documents or {}
        
        # Collect scripts from different scopes
        file_scripts = self._get_file_scripts(target, documents)
        dir_scripts = self._get_directory_scripts(target, documents)
        project_scripts = self.config.tasks
        
        # Execute via ScriptRunner
        return self._runner.run_script(
            script_name,
            target_file=target if target.suffix in {'.td', '.md'} else None,
            file_scripts=file_scripts,
            dir_scripts=dir_scripts,
            project_scripts=project_scripts,
            dry_run=dry_run
        )
    
    def find_script(
        self,
        script_name: str,
        target_file: Optional[Path] = None,
        documents: Optional[Dict[Path, Document]] = None
    ) -> Optional[str]:
        """
        Find a script command without executing it.
        
        Args:
            script_name: Name of the script to find
            target_file: Target file path
            documents: Current documents dictionary
            
        Returns:
            Script command string or None if not found
        """
        target = target_file or self.project_root
        documents = documents or {}
        
        file_scripts = self._get_file_scripts(target, documents)
        dir_scripts = self._get_directory_scripts(target, documents)
        project_scripts = self.config.tasks
        
        return self._runner.find_script(
            script_name,
            target_file=target if target.suffix in {'.td', '.md'} else None,
            file_scripts=file_scripts,
            dir_scripts=dir_scripts,
            project_scripts=project_scripts
        )
    
    def _get_file_scripts(
        self,
        target: Path,
        documents: Dict[Path, Document]
    ) -> Optional[Dict[str, str]]:
        """Get scripts from file scope (Front Matter)."""
        # Try to get from cached documents
        if target in documents:
            doc = documents[target]
            if doc.scripts:
                return doc.scripts
            return None
        
        # Try parsing on demand
        try:
            if self.source_provider.exists(target):
                content = self.source_provider.get_content(target)
                doc = self._parser.parse_text(content, str(target))
                documents[target] = doc  # Cache it
                return doc.scripts
        except Exception:
            pass
        
        return None
    
    def _get_directory_scripts(
        self,
        target: Path,
        documents: Dict[Path, Document]
    ) -> Optional[Dict[str, str]]:
        """
        Get scripts from directory scope (config.td).
        Walks up from target directory to project root.
        """
        # Determine start directory
        if target.suffix in {'.td', '.md'}:
            start_dir = target.parent
        else:
            start_dir = target
        
        try:
            start_dir = start_dir.resolve()
        except Exception:
            pass
        
        # Walk up to find the nearest config.td
        current = start_dir
        while True:
            # Check for project root escape
            try:
                if not current.is_relative_to(self.project_root):
                    break
            except ValueError:
                break
            
            config_path = current / "config.td"
            if self.source_provider.exists(config_path):
                # Try cached first
                if config_path in documents:
                    doc = documents[config_path]
                else:
                    # Parse on demand
                    try:
                        content = self.source_provider.get_content(config_path)
                        doc = self._parser.parse_text(content, str(config_path))
                        documents[config_path] = doc
                    except Exception:
                        doc = None
                
                if doc and doc.scripts:
                    return doc.scripts
                # Continue searching up if no scripts found
            
            # Stop conditions
            if current == self.project_root:
                break
            if current.parent == current:
                break
            current = current.parent
        
        return None

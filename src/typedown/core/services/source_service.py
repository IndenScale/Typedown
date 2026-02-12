"""
SourceService: Manages source file operations with overlay support.

Responsibilities:
- Source file updates (in-memory overlay)
- Incremental document parsing
- Recompilation triggering
"""

from pathlib import Path
from typing import Dict, Set, Optional, TYPE_CHECKING
from rich.console import Console

from typedown.core.ast import Document
from typedown.core.parser import TypedownParser
from typedown.core.analysis.source_provider import SourceProvider, OverlayProvider

if TYPE_CHECKING:
    pass


class SourceService:
    """
    Service for managing source files and in-memory overlays.
    
    This service handles:
    1. Overlay updates for LSP integration
    2. Incremental document parsing
    3. Document state management
    """
    
    def __init__(
        self,
        source_provider: SourceProvider,
        console: Optional[Console] = None
    ):
        self.source_provider = source_provider
        self.console = console or Console()
        self._parser = TypedownParser()
    
    def update_source(
        self,
        path: Path,
        content: str,
        documents: Dict[Path, Document],
        target_files: Set[Path]
    ) -> bool:
        """
        Lightweight incremental update:
        1. Update Overlay.
        2. Parse new content.
        3. Update Documents State.
        
        Args:
            path: Path to the source file
            content: New content of the file
            documents: Current documents dictionary (modified in-place)
            target_files: Current target files set (modified in-place)
            
        Returns:
            True if successful, False if parse failed (but overlay updated)
        """
        try:
            # 1. Update Overlay
            if isinstance(self.source_provider, OverlayProvider):
                self.source_provider.update_overlay(path, content)
            
            try:
                # Parse in-memory
                new_doc = self._parser.parse_text(content, str(path))
                # Update State
                documents[path] = new_doc
                target_files.add(path)
                return True
            except Exception:
                # Parse error: We still updated overlay (important for text access)
                # But we can't update the Document AST.
                return False
                
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Source Update Failed for {path}: {e}[/yellow]")
            return False
    
    def update_document(
        self,
        path: Path,
        content: str,
        documents: Dict[Path, Document],
        target_files: Set[Path],
        recompile_callback: Optional[callable] = None
    ) -> bool:
        """
        Legacy combined method that updates source and triggers recompile.
        
        Args:
            path: Path to the source file
            content: New content of the file
            documents: Current documents dictionary
            target_files: Current target files set
            recompile_callback: Optional callback to trigger recompilation
            
        Returns:
            True if successful
        """
        success = self.update_source(path, content, documents, target_files)
        if success and recompile_callback:
            recompile_callback()
        return success
    
    def parse_document_on_demand(
        self,
        target: Path,
        documents: Dict[Path, Document]
    ) -> Optional[Document]:
        """
        Parse a document on demand if not already in documents.
        
        Args:
            target: Path to the document
            documents: Current documents dictionary (caches result)
            
        Returns:
            Parsed Document or None if parsing failed
        """
        if target in documents:
            return documents[target]
        
        try:
            if self.source_provider.exists(target):
                content = self.source_provider.get_content(target)
                doc = self._parser.parse_text(content, str(target))
                documents[target] = doc  # Cache it
                return doc
        except Exception:
            pass
        
        return None

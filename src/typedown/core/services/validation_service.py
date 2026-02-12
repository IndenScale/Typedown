"""
ValidationService: Handles L1, L2, and L3 validation levels.

Responsibilities:
- L1: Syntax checking (lint)
- L2: Schema compliance checking
- L3: Reference resolution and graph validation
"""

from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING
from rich.console import Console

from typedown.core.ast import Document
from typedown.core.base.config import TypedownConfig
from typedown.core.base.errors import DiagnosticReport
from typedown.core.base.symbol_table import SymbolTable
from typedown.core.analysis.scanner import Scanner
from typedown.core.analysis.linker import Linker
from typedown.core.analysis.validator import Validator
from typedown.core.analysis.source_provider import SourceProvider

if TYPE_CHECKING:
    pass


class ValidationService:
    """
    Service for validation operations at different levels.
    
    Validation Levels:
    - L1 (lint): Syntax checking via Scanner
    - L2 (check): Schema compliance via Linker + Validator.check_schema
    - L3 (validate): Full validation including reference resolution
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
    
    def lint(
        self,
        target: Path,
        script: Optional[Any] = None
    ) -> tuple[bool, DiagnosticReport, Dict[Path, Document]]:
        """
        L1: Syntax Check (Scanner only).
        
        Args:
            target: Target path to lint
            script: Deprecated, ignored
            
        Returns:
            Tuple of (passed, diagnostics, documents)
        """
        if script:
            self.console.print("  [yellow]Scripts are deprecated, ignoring script filter[/yellow]")
        
        diagnostics = DiagnosticReport()
        
        scanner = Scanner(
            self.project_root,
            self.console,
            provider=self.source_provider
        )
        documents, _ = scanner.scan(target)
        diagnostics.extend(scanner.diagnostics.errors)
        
        # Run lint checks
        lint_passed = scanner.lint(documents)
        diagnostics.extend(scanner.diagnostics.errors)
        
        return lint_passed and not diagnostics.has_errors(), diagnostics, documents
    
    def check(
        self,
        target: Path,
        script: Optional[Any] = None
    ) -> tuple[bool, DiagnosticReport, Dict[Path, Document], SymbolTable, Dict[str, Any]]:
        """
        L2: Schema Compliance (Scanner + Linker + Pydantic instantiation + validators).
        
        Args:
            target: Target path to check
            script: Deprecated, ignored
            
        Returns:
            Tuple of (passed, diagnostics, documents, symbol_table, model_registry)
        """
        # First run L1
        lint_passed, diagnostics, documents = self.lint(target, script)
        if not lint_passed:
            return False, diagnostics, documents, SymbolTable(), {}
        
        # Stage 2 + 3: Linker + Validation (structure + local)
        return self._run_validation(documents, diagnostics, run_validators=True)
    
    def check_structure(
        self,
        target: Path,
        script: Optional[Any] = None,
        documents: Optional[Dict[Path, Document]] = None
    ) -> tuple[bool, DiagnosticReport, Dict[Path, Document], SymbolTable, Dict[str, Any]]:
        """
        Stage 2: Structure Check (Pydantic instantiation only, no validators).
        
        Args:
            target: Target path (used if documents not provided)
            script: Deprecated, ignored
            documents: Pre-scanned documents (optional)
            
        Returns:
            Tuple of (passed, diagnostics, documents, symbol_table, model_registry)
        """
        if documents is None:
            # First run L1
            lint_passed, diagnostics, documents = self.lint(target, script)
            if not lint_passed:
                return False, diagnostics, documents, SymbolTable(), {}
        else:
            diagnostics = DiagnosticReport()
        
        # Stage 2 only: Linker + Structure (no validators)
        return self._run_validation(documents, diagnostics, run_validators=False)
    
    def check_local(
        self,
        documents: Dict[Path, Document],
        symbol_table: SymbolTable,
        model_registry: Dict[str, Any],
        existing_diagnostics: DiagnosticReport
    ) -> tuple[bool, DiagnosticReport]:
        """
        Stage 3: Local Check - Run Pydantic validators.
        
        Args:
            documents: Scanned and linked documents
            symbol_table: Linked symbol table
            model_registry: Model registry
            existing_diagnostics: Existing diagnostics to extend
            
        Returns:
            Tuple of (passed, diagnostics)
        """
        diagnostics = existing_diagnostics
        
        # Run validators on already-instantiated entities
        validator = Validator(self.console)
        validator.run_validators_only(documents, symbol_table, model_registry)
        diagnostics.extend(validator.diagnostics.errors)
        
        passed = not diagnostics.has_errors()
        return passed, diagnostics
    
    def _run_validation(
        self,
        documents: Dict[Path, Document],
        diagnostics: DiagnosticReport,
        run_validators: bool = True
    ) -> tuple[bool, DiagnosticReport, Dict[Path, Document], SymbolTable, Dict[str, Any]]:
        """Internal: Run linker and validation."""
        # Linker
        linker = Linker(self.project_root, self.config, self.console)
        linker.link(documents)
        symbol_table = linker.symbol_table
        model_registry = linker.model_registry
        diagnostics.extend(linker.diagnostics.errors)
        
        if diagnostics.has_errors():
            return False, diagnostics, documents, symbol_table, model_registry
        
        # Validation
        validator = Validator(self.console)
        if run_validators:
            validator.check_schema(documents, symbol_table, model_registry)
        else:
            validator.check_structure_only(documents, symbol_table, model_registry)
        diagnostics.extend(validator.diagnostics.errors)
        
        passed = not diagnostics.has_errors()
        return passed, diagnostics, documents, symbol_table, model_registry
    
    def validate_in_memory(
        self,
        documents: Dict[Path, Document],
        symbol_table: SymbolTable,
        model_registry: Dict[str, Any]
    ) -> tuple[bool, DiagnosticReport, SymbolTable, Dict[str, Any], Any]:
        """
        L2 + L3: Full validation on in-memory documents.
        
        This is used for recompilation without file IO.
        
        Args:
            documents: Current documents dictionary
            symbol_table: Current symbol table (will be replaced)
            model_registry: Current model registry (will be replaced)
            
        Returns:
            Tuple of (passed, diagnostics, symbol_table, model_registry, dependency_graph)
        """
        diagnostics = DiagnosticReport()
        
        # Linker
        linker = Linker(self.project_root, self.config, self.console)
        linker.link(documents)
        symbol_table = linker.symbol_table
        model_registry = linker.model_registry
        diagnostics.extend(linker.diagnostics.errors)
        
        # Validator
        validator = Validator(self.console)
        # L2: Schema Check (Pydantic) - Ensure mandatory fields exist
        validator.check_schema(documents, symbol_table, model_registry)
        
        # L3: Reference Resolution
        validator.validate(documents, symbol_table, model_registry)
        diagnostics.extend(validator.diagnostics.errors)
        dependency_graph = validator.dependency_graph
        
        passed = not diagnostics.has_errors()
        return passed, diagnostics, symbol_table, model_registry, dependency_graph

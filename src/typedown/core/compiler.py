"""
Compiler: Facade/Coordinator for the Typedown compilation pipeline.

The Compiler class has been refactored from a God Class into a Facade that
coordinates multiple specialized services:

    Compiler (Facade)
    ├── ValidationService    # L1/L2/L3 validation
    ├── ScriptService        # Script system
    ├── TestService          # L4 Specs + Oracles
    ├── QueryService         # Query interface
    └── SourceService        # Source file management
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from rich.console import Console

from typedown.core.ast import Document, EntityBlock
from typedown.core.base.utils import find_project_root, AttributeWrapper
from typedown.core.base.config import TypedownConfig, ScriptConfig
from typedown.core.base.errors import TypedownError, DiagnosticReport
from typedown.core.base.symbol_table import SymbolTable

from typedown.core.analysis.scanner import Scanner
from typedown.core.analysis.linker import Linker
from typedown.core.analysis.validator import Validator
from typedown.core.analysis.source_provider import DiskProvider, OverlayProvider

from typedown.core.services import (
    SourceService,
    ValidationService,
    ScriptService,
    TestService,
    QueryService,
)


class Compiler:
    """Facade for the Typedown compilation pipeline."""
    
    def __init__(self, target: Path, console: Optional[Console] = None, memory_only: bool = False):
        self.target = target.resolve()
        self.console = console or Console()
        self.project_root = find_project_root(self.target)
        self.config = TypedownConfig.load(self.project_root / "typedown.toml")
        
        # IO Interface (Overlay Support for LSP)
        self.base_provider = DiskProvider()
        self.source_provider = OverlayProvider(self.base_provider, memory_only=memory_only)
        
        # State
        self.documents: Dict[Path, Document] = {}
        self.target_files: Set[Path] = set()
        self.symbol_table: SymbolTable = SymbolTable()
        self.model_registry: Dict[str, Any] = {}
        self.active_script: Optional[ScriptConfig] = None
        self.diagnostics: DiagnosticReport = DiagnosticReport()
        self.dependency_graph: Optional[Any] = None
        self.resources: Dict[str, Any] = {}
        
        # Services
        self.source_svc = SourceService(self.source_provider, self.console)
        self.validation_svc = ValidationService(
            self.project_root, self.config, self.source_provider, self.console
        )
        self.script_svc = ScriptService(
            self.project_root, self.config, self.source_provider, self.console
        )
        self.test_svc = TestService(self.project_root, self.config, self.console)
        self._query_svc: Optional[QueryService] = None
    
    def _query_service(self) -> QueryService:
        """Lazy init/update QueryService (requires symbol_table)."""
        if self._query_svc is None:
            self._query_svc = QueryService(self.project_root, self.symbol_table, self.console)
        return self._query_svc
    
    # ==================== Pipeline Operations ====================
    
    def compile(self, script_name: Optional[str] = None, run_specs: bool = True) -> bool:
        """Runs the full compilation pipeline."""
        self.diagnostics = DiagnosticReport()
        self.active_script = self._resolve_script(script_name)
        if self.active_script is None and script_name:
            return False
        
        try:
            # Stage 1: Scanner
            scanner = Scanner(self.project_root, self.console, provider=self.source_provider)
            self.documents, self.target_files = scanner.scan(self.target, self.active_script)
            self.diagnostics.extend(scanner.diagnostics.errors)
            
            # Stage 2: Linker
            linker = Linker(self.project_root, self.config, self.console)
            linker.link(self.documents)
            self.symbol_table = linker.symbol_table
            self.model_registry = linker.model_registry
            self.diagnostics.extend(linker.diagnostics.errors)
            
            # Stage 2.5 & 3: Validator
            validator = Validator(self.console)
            validator.check_schema(self.documents, self.symbol_table, self.model_registry)
            validator.validate(self.documents, self.symbol_table, self.model_registry)
            self.diagnostics.extend(validator.diagnostics.errors)
            self.dependency_graph = validator.dependency_graph
            
            # Update QueryService and run specs
            self._query_svc = None  # Will be recreated on next access
            if run_specs and not self.diagnostics.has_errors():
                self.verify_specs()
            
            self._print_diagnostics()
            return not self.diagnostics.has_errors()
            
        except Exception as e:
            self.console.print(f"[bold red]Compiler Crash:[/bold red] {e}")
            import traceback
            self.console.print(traceback.format_exc())
            return False
    
    def _resolve_script(self, script_name: Optional[str]) -> Optional[ScriptConfig]:
        """Resolve script name to ScriptConfig or handle error."""
        if not script_name:
            self.console.print(f"[bold blue]Typedown Compiler:[/bold blue] Starting pipeline for [cyan]{self.target}[/cyan]")
            return None
        
        if script_name not in self.config.scripts:
            from typedown.core.base.errors import ErrorCode, ErrorLevel
            self.diagnostics.add(TypedownError(
                f"Script '{script_name}' not found",
                code=ErrorCode.E0903,
                level=ErrorLevel.ERROR,
                details={"script": script_name}
            ))
            self._print_diagnostics()
            return None
        
        script = self.config.scripts[script_name]
        self.console.print(f"[bold blue]Typedown Compiler:[/bold blue] Starting pipeline for script [cyan]:{script_name}[/cyan]")
        return script
    
    def recompile(self):
        """Run the full compilation pipeline in-memory."""
        passed, self.diagnostics, self.symbol_table, self.model_registry, self.dependency_graph = \
            self.validation_svc.validate_in_memory(self.documents, self.symbol_table, self.model_registry)
        self._query_svc = None
        if passed:
            self.verify_specs()
    
    def update_document(self, path: Path, content: str):
        """Update source and recompile."""
        if self.update_source(path, content):
            self.recompile()
    
    # ==================== Validation Operations ====================
    
    def lint(self, target: Optional[Path] = None, script: Optional[str] = None) -> bool:
        """Stage 1: Syntax Check (Scanner only)."""
        from typedown.core.base.config import ScriptConfig
        script_config: Optional[ScriptConfig] = None
        if script:
            script_config = self.config.scripts.get(script)
            if not script_config:
                self.console.print(f"[red]Script '{script}' not found[/red]")
                return False
        passed, self.diagnostics, self.documents = \
            self.validation_svc.lint(target or self.target, script_config)
        self._print_diagnostics()
        return passed
    
    def check_structure(self, target: Optional[Path] = None, script: Optional[str] = None) -> bool:
        """Stage 2: Structure Check (Scanner + Linker + Pydantic instantiation only)."""
        from typedown.core.base.config import ScriptConfig
        script_config: Optional[ScriptConfig] = None
        if script:
            script_config = self.config.scripts.get(script)
            if not script_config:
                self.console.print(f"[red]Script '{script}' not found[/red]")
                return False
        
        # L1 first
        passed, self.diagnostics, self.documents = \
            self.validation_svc.lint(target or self.target, script_config)
        if not passed:
            self._print_diagnostics()
            return False
        
        # Stage 2: Linker + Structure (Pydantic instantiation without validators)
        passed, self.diagnostics, self.documents, self.symbol_table, self.model_registry = \
            self.validation_svc.check_structure(target or self.target, script_config, self.documents)
        if passed:
            self._query_svc = None
        self._print_diagnostics()
        return passed
    
    def check_local(self, target: Optional[Path] = None, script: Optional[str] = None) -> bool:
        """Stage 3: Local Check (all above + Pydantic validators)."""
        from typedown.core.base.config import ScriptConfig
        script_config: Optional[ScriptConfig] = None
        if script:
            script_config = self.config.scripts.get(script)
            if not script_config:
                self.console.print(f"[red]Script '{script}' not found[/red]")
                return False
        
        # L1 + L2 first
        passed, self.diagnostics, self.documents, self.symbol_table, self.model_registry = \
            self.validation_svc.check(target or self.target, script_config)
        if not passed:
            self._print_diagnostics()
            return False
        
        # Stage 3: Run Pydantic validators (field validators, model validators)
        passed, self.diagnostics = \
            self.validation_svc.check_local(self.documents, self.symbol_table, self.model_registry, self.diagnostics)
        if passed:
            self._query_svc = None
        self._print_diagnostics()
        return passed
    
    def check_global(self, target: Optional[Path] = None, script: Optional[str] = None) -> bool:
        """Stage 4: Global Check (all above + Reference resolution + Specs)."""
        # Full compile (L1 + L2 + L3 reference resolution + specs)
        passed = self.compile(script_name=script, run_specs=True)
        return passed
    
    def check(self, target: Optional[Path] = None, script: Optional[str] = None) -> bool:
        """Legacy: L2 Schema Compliance (defaults to local stage)."""
        return self.check_local(target, script)
    
    # ==================== Source Management ====================
    
    def update_source(self, path: Path, content: str) -> bool:
        """Lightweight incremental update."""
        return self.source_svc.update_source(path, content, self.documents, self.target_files)
    
    # ==================== Script Operations ====================
    
    def run_script(self, script_name: str, target_file: Optional[Path] = None, dry_run: bool = False) -> int:
        """Execute a script with scope-based resolution."""
        return self.script_svc.run_script(script_name, target_file, self.documents, dry_run)
    
    # ==================== Test Operations ====================
    
    def verify_specs(self, spec_filter: Optional[str] = None, console: Optional[Console] = None) -> bool:
        """Public API to trigger L4 Spec Validation."""
        specs_passed, self.diagnostics = self.test_svc.run_specs(
            self.documents, self.symbol_table, self.model_registry,
            spec_filter=spec_filter, existing_diagnostics=self.diagnostics
        )
        return specs_passed
    
    def run_tests(self, tags: List[str] = []) -> int:
        """Stage 4: External Verification (Oracles)."""
        return self.test_svc.run_oracles(self, tags)
    
    # ==================== Query Operations ====================
    
    def query(self, query_string: str, context_path: Optional[Path] = None) -> Any:
        """GraphQL-like query interface for the symbol table."""
        return self._query_service().query(query_string, context_path)
    
    def get_entities_by_type(self, type_name: str) -> List[Any]:
        """Compatibility method for existing specs."""
        return self._query_service().get_entities_by_type(type_name)
    
    def get_entity(self, entity_id: str) -> Optional[Any]:
        """Compatibility method for existing specs."""
        return self._query_service().get_entity(entity_id)
    
    # ==================== Utility Methods ====================
    
    def _print_diagnostics(self):
        """Print diagnostics report to console."""
        if not self.diagnostics.errors:
            return
        from typedown.core.base.errors import print_diagnostic_report
        self.console.print(f"\n[bold]Diagnostics ({len(self.diagnostics.errors)}):[/bold]")
        print_diagnostic_report(self.console, self.diagnostics)

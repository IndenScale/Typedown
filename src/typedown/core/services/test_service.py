"""
TestService: Test execution for specs and oracles.

Responsibilities:
- L4 Spec validation execution
- Oracle test execution
"""

import importlib
from pathlib import Path
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from rich.console import Console

from typedown.core.ast import Document
from typedown.core.base.config import TypedownConfig
from typedown.core.base.errors import DiagnosticReport
from typedown.core.base.symbol_table import SymbolTable
from typedown.core.analysis.spec_executor import SpecExecutor

if TYPE_CHECKING:
    from typedown.core.compiler import Compiler


class TestService:
    """
    Service for test execution including specs and oracles.
    
    Test Levels:
    - L4 Specs: Internal self-validation using SpecExecutor
    - Oracles: External verification tests
    """
    
    def __init__(
        self,
        project_root: Path,
        config: TypedownConfig,
        console: Optional[Console] = None
    ):
        self.project_root = project_root
        self.config = config
        self.console = console or Console()
    
    def run_specs(
        self,
        documents: Dict[Path, Document],
        symbol_table: SymbolTable,
        model_registry: Dict[str, Any],
        spec_filter: Optional[str] = None,
        existing_diagnostics: Optional[DiagnosticReport] = None
    ) -> tuple[bool, DiagnosticReport]:
        """
        Execute internal specs with @target binding.
        
        Args:
            documents: Current documents dictionary
            symbol_table: Current symbol table
            model_registry: Current model registry
            spec_filter: Optional filter to run specific spec
            existing_diagnostics: Optional existing diagnostics to extend
            
        Returns:
            Tuple of (all_passed, diagnostics)
        """
        spec_executor = SpecExecutor(self.console)
        specs_passed = spec_executor.execute_specs(
            documents,
            symbol_table,
            model_registry,
            project_root=self.project_root,
            spec_filter=spec_filter
        )
        
        # Return or extend diagnostics
        if existing_diagnostics is not None:
            existing_diagnostics.extend(spec_executor.diagnostics.errors)
            return specs_passed, existing_diagnostics
        
        return specs_passed, spec_executor.diagnostics
    
    def run_oracles(
        self,
        compiler: "Compiler",
        tags: List[str] = []
    ) -> int:
        """
        Stage 4: External Verification (Oracles).
        
        Args:
            compiler: Compiler instance to pass to oracles
            tags: Optional tags to filter oracles
            
        Returns:
            Overall exit code (0 for success)
        """
        if self.console:
            self.console.print("  [dim]Stage 4: Executing reality checks (Oracles)...[/dim]")
        
        overall_exit_code = 0
        
        for oracle_path in self.config.test.oracles:
            try:
                # Load oracle class
                if "." not in oracle_path:
                    continue
                
                module_name, class_name = oracle_path.rsplit(".", 1)
                module = importlib.import_module(module_name)
                oracle_cls = getattr(module, class_name)
                oracle = oracle_cls()
                
                if self.console:
                    self.console.print(f"    [blue]Running Oracle: {oracle_path}[/blue]")
                
                exit_code = oracle.run(compiler, tags)
                if exit_code != 0:
                    overall_exit_code = exit_code
                    
            except Exception as e:
                if self.console:
                    self.console.print(f"    [bold red]Oracle Error ({oracle_path}): {e}[/bold red]")
                overall_exit_code = 1
        
        return overall_exit_code
    
    def run_all_tests(
        self,
        compiler: "Compiler",
        documents: Dict[Path, Document],
        symbol_table: SymbolTable,
        model_registry: Dict[str, Any],
        tags: List[str] = []
    ) -> int:
        """
        Run both specs and oracles.
        
        Args:
            compiler: Compiler instance
            documents: Current documents dictionary
            symbol_table: Current symbol table
            model_registry: Current model registry
            tags: Optional tags for oracles
            
        Returns:
            Overall exit code (0 for success)
        """
        # Run specs first
        specs_passed, _ = self.run_specs(
            documents, symbol_table, model_registry
        )
        
        if not specs_passed:
            return 1
        
        # Then run oracles
        return self.run_oracles(compiler, tags)

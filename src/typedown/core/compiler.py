from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from rich.console import Console

from typedown.core.ast import Document, EntityBlock
from typedown.core.base.utils import find_project_root, AttributeWrapper
from typedown.core.base.config import TypedownConfig, ScriptConfig
from typedown.core.base.errors import TypedownError, print_diagnostic

from typedown.core.analysis.scanner import Scanner
from typedown.core.analysis.linker import Linker
from typedown.core.analysis.validator import Validator
from typedown.core.analysis.script_runner import ScriptRunner

class Compiler:
    def __init__(self, target: Path, console: Optional[Console] = None):
        self.target = target.resolve()
        self.console = console or Console()
        self.project_root = find_project_root(self.target)
        self.config = TypedownConfig.load(self.project_root / "typedown.toml")
        
        # State
        self.documents: Dict[Path, Document] = {}
        self.target_files: Set[Path] = set()
        self.symbol_table: Dict[str, EntityBlock] = {}
        self.model_registry: Dict[str, Any] = {}
        self.active_script: Optional[ScriptConfig] = None
        self.diagnostics: List[TypedownError] = []
        self.dependency_graph: Optional[Any] = None # Graph
        self.resources: Dict[str, Any] = {} # Path -> Resource
        
    def compile(self, script_name: Optional[str] = None) -> bool:
        """Runs the full compilation pipeline."""
        self.diagnostics.clear()
        
        self.active_script = None
        if script_name:
            if script_name not in self.config.scripts:
                self.diagnostics.append(TypedownError(f"Script '{script_name}' not found", severity="error"))
                self._print_diagnostics()
                return False
            self.active_script = self.config.scripts[script_name]
            self.console.print(f"[bold blue]Typedown Compiler:[/bold blue] Starting pipeline for script [cyan]:{script_name}[/cyan]")
        else:
            self.console.print(f"[bold blue]Typedown Compiler:[/bold blue] Starting pipeline for [cyan]{self.target}[/cyan]")
        
        try:
            # Stage 1: Scanner
            scanner = Scanner(self.project_root, self.console)
            self.documents, self.target_files = scanner.scan(self.target, self.active_script)
            self.diagnostics.extend(scanner.diagnostics)
            
            # Stage 2: Linker
            linker = Linker(self.project_root, self.config, self.console)
            linker.link(self.documents)
            self.symbol_table = linker.symbol_table
            self.model_registry = linker.model_registry
            self.diagnostics.extend(linker.diagnostics)
            
            # Stage 3: Validator (L3)
            validator = Validator(self.console)
            validator.validate(self.documents, self.symbol_table, self.model_registry)
            self.diagnostics.extend(validator.diagnostics)
            self.dependency_graph = validator.dependency_graph
            
            # Stage 3.5: Specs (Internal Self-Validation)
            # REMOVED: Specs are now L4 and should be triggered on-demand (CLI/LSP), 
            # not during standard compilation/startup.
            # if not any(d.severity == "error" for d in self.diagnostics):
            #     specs_passed = self._run_specs() 


            # Check for Errors
            has_error = False
            for d in self.diagnostics:
                if d.severity == "error":
                    has_error = True
            
            self._print_diagnostics()
            return not has_error
            
        except Exception as e:
            self.console.print(f"[bold red]Compiler Crash:[/bold red] {e}")
            import traceback
            self.console.print(traceback.format_exc())
            return False

    def _run_specs(self) -> bool:
        """Execute internal specs with @target binding."""
        return self.verify_specs()

    def verify_specs(self, spec_filter: Optional[str] = None) -> bool:
        """
        Public API to trigger L4 Spec Validation.
        Can run all specs or filter by ID.
        """
        from typedown.core.analysis.spec_executor import SpecExecutor
        
        spec_executor = SpecExecutor(self.console)
        specs_passed = spec_executor.execute_specs(
            self.documents,
            self.symbol_table,
            self.model_registry,
            project_root=self.project_root,
            spec_filter=spec_filter
        )
        # Extend diagnostics with L4 errors
        # Note: We might want to clear previous Spec-related diagnostics first?
        # For now, append is fine as compile() clears all diagnostics usually.
        # BUT if we run this ad-hoc (CodeLens), currently diagnostics are NOT cleared before this call 
        # unless compile() was called.
        self.diagnostics.extend(spec_executor.diagnostics)
        return specs_passed

    def _print_diagnostics(self):
        if not self.diagnostics:
            return
        self.console.print(f"\n[bold]Diagnostics ({len(self.diagnostics)}):[/bold]")
        for d in self.diagnostics:
            print_diagnostic(self.console, d)
        self.console.print("")

    def query(self, query_string: str, context_path: Optional[Path] = None) -> Any:
        """
        GraphQL-like query interface for the symbol table.
        Example: compiler.query("User.profile.email")
        """
        from typedown.core.analysis.query import QueryEngine
        # Default context to target directory if not specified
        ctx = context_path or self.target
        
        # Return all matches (List[Any])
        return QueryEngine.resolve_query(
            query_string, 
            self.symbol_table, 
            root_dir=self.project_root,
            context_path=ctx
        )

    def run_tests(self, tags: List[str] = []) -> int:
        """
        Stage 4: External Verification (Oracles).
        Internal specs are now run during compile().
        """
        overall_exit_code = 0
        
        # Step 2: Execute Oracles (External Verification)
        self.console.print("  [dim]Stage 4: Executing reality checks (Oracles)...[/dim]")
        
        import importlib
        
        for oracle_path in self.config.test.oracles:
            try:
                # Load oracle class
                if "." not in oracle_path:
                    continue
                
                module_name, class_name = oracle_path.rsplit(".", 1)
                module = importlib.import_module(module_name)
                oracle_cls = getattr(module, class_name)
                oracle = oracle_cls()
                
                self.console.print(f"    [blue]Running Oracle: {oracle_path}[/blue]")
                exit_code = oracle.run(self, tags)
                if exit_code != 0:
                    overall_exit_code = exit_code
            except Exception as e:
                self.console.print(f"    [bold red]Oracle Error ({oracle_path}): {e}[/bold red]")
                overall_exit_code = 1
        
        return overall_exit_code

    def get_entities_by_type(self, type_name: str) -> List[Any]:
        """Compatibility method for existing specs."""
        results = []
        for node in self.symbol_table.values():
            if isinstance(node, EntityBlock) and node.class_name == type_name:
                # Use AttributeWrapper to allow dot notation
                results.append(AttributeWrapper(node.resolved_data))
        return results

    def get_entity(self, entity_id: str) -> Optional[Any]:
        """Compatibility method for existing specs."""
        entity = self.symbol_table.get(entity_id)
        if entity:
            return AttributeWrapper(entity.resolved_data)
        return None

    def lint(self, target: Optional[Path] = None, script_name: Optional[str] = None) -> bool:
        """L1: Syntax Check (Scanner only)."""
        self.diagnostics.clear()
        target = target or self.target
        script = self.config.scripts.get(script_name) if script_name else None
        
        scanner = Scanner(self.project_root, self.console)
        self.documents, _ = scanner.scan(target, script)
        self.diagnostics.extend(scanner.diagnostics)
        
        # Run lint checks
        lint_passed = scanner.lint(self.documents)
        self.diagnostics.extend(scanner.diagnostics)
        
        self._print_diagnostics()
        return lint_passed and not any(d.severity == "error" for d in self.diagnostics)

    def check(self, target: Optional[Path] = None, script_name: Optional[str] = None) -> bool:
        """L2: Schema Compliance (Scanner + Linker + Pydantic)."""
        if not self.lint(target, script_name):
            return False
            
        # Linker (Stage 2)
        linker = Linker(self.project_root, self.config, self.console)
        linker.link(self.documents)
        self.symbol_table = linker.symbol_table
        self.model_registry = linker.model_registry
        self.diagnostics.extend(linker.diagnostics)

        # Validation (Pydantic-only part of Phase 3)
        # L2 check: Now strictly structure compliance only.
        validator = Validator(self.console)
        validator.check_schema(self.documents, self.model_registry)
        self.diagnostics.extend(validator.diagnostics)
        
        self._print_diagnostics()
        return not any(d.severity == "error" for d in self.diagnostics)

    def update_document(self, path: Path, content: str):
        """
        Incremental Update:
        1. Parse new content into Document.
        2. Diff with existing Document (using Block Hashes) -> optimizations possible here.
        3. For MVP: Replace Document and Re-Link/Re-Validate (In-Memory).
        """
        try:
            from typedown.core.parser import TypedownParser
            parser = TypedownParser()
            # Parse in-memory
            new_doc = parser.parse_text(content, path_str=str(path))
            
            # TODO: Advanced Diffing using content_hash to skip invalidation
            # old_doc = self.documents.get(path)
            
            # Update State
            self.documents[path] = new_doc
            self.target_files.add(path) # Ensure it's tracked
            
            # Trigger Fast Recompile (Link + Validate)
            self._recompile_in_memory()
            
        except Exception as e:
            self.console.print(f"[yellow]Incremental Update Failed for {path}: {e}[/yellow]")
            # If parse fails, we might want to keep old doc or mark as error state (?)
            # For now, we just log.
            pass

    def _recompile_in_memory(self):
        """
        Runs Linker and Validator on current in-memory documents.
        Skips Scanner (File IO).
        """
        self.diagnostics.clear()
        
        # Linker
        linker = Linker(self.project_root, self.config, self.console)
        linker.link(self.documents)
        self.symbol_table = linker.symbol_table
        self.model_registry = linker.model_registry
        self.diagnostics.extend(linker.diagnostics)
        
        # Validator
        validator = Validator(self.console)
        validator.validate(self.documents, self.symbol_table, self.model_registry)
        self.diagnostics.extend(validator.diagnostics)
        self.dependency_graph = validator.dependency_graph
        
        # Stage 3.5: Specs (Internal Self-Validation)
        # REMOVED: On-demand only.
        # if not any(d.severity == "error" for d in self.diagnostics):
        #     self._run_specs()
    
    def run_script(
        self,
        script_name: str,
        target_file: Optional[Path] = None,
        dry_run: bool = False
    ) -> int:
        """
        执行脚本（Script System）
        
        查找顺序（就近原则）：
        1. File Scope: 目标文件的 Front Matter
        2. Directory Scope: 目录的 config.td
        3. Project Scope: typedown.yaml
        
        Args:
            script_name: 脚本名称（如 "validate", "verify-business"）
            target_file: 目标文件路径（如果为 None，使用 self.target）
            dry_run: 是否仅打印命令而不执行
        
        Returns:
            退出码（0 表示成功）
        """
        target = target_file or self.target
        
        # 收集脚本定义
        file_scripts: Optional[Dict[str, str]] = None
        dir_scripts: Optional[Dict[str, str]] = None
        project_scripts: Optional[Dict[str, str]] = None
        
        from typedown.core.parser import TypedownParser
        parser = TypedownParser()

        # L1: File Scope - Get from parsed documents or parse on demand
        if target.is_file():
            if target in self.documents:
                doc = self.documents[target]
            else:
                try:
                    doc = parser.parse(target)
                    self.documents[target] = doc # Cache it
                except Exception:
                    doc = None
            
            if doc and doc.scripts:
                file_scripts = doc.scripts
        
        # L2: Directory Scope - Get from config.td (need to parse)
        
        start_dir = target.parent if target.is_file() else target
        start_dir = start_dir.resolve()
        
        # Walk up to find the NEAREST config.td
        for parent in [start_dir] + list(start_dir.parents):
            try:
                # Stop if we leave the project root
                if not parent.is_relative_to(self.project_root):
                    break
            except ValueError:
                break
                
            config_path = parent / "config.td"
            if config_path.exists():
                # Check if already parsed
                if config_path in self.documents:
                    doc = self.documents[config_path]
                else:
                    # On-demand parse
                    try:
                        doc = parser.parse(config_path)
                        # Optionally cache it back
                        self.documents[config_path] = doc
                    except Exception:
                        continue
                
                if doc.scripts:
                    dir_scripts = doc.scripts
                    # Found the nearest config with scripts? 
                    # If we believe in shadowing, we stop here.
                    # Or do we want to merge? 
                    # Spec says "Lexical Scoping", usually means shadowing. 
                    # ScriptRunner treats "Directory Scope" as a single layer.
                    # So we pick the nearest one.
                    break
        
        # L3: Project Scope - 从 typedown.toml 获取
        project_scripts = self.config.tasks
        
        # 执行脚本
        runner = ScriptRunner(self.project_root, self.console)
        return runner.run_script(
            script_name,
            target_file=target if target.is_file() else None,
            file_scripts=file_scripts,
            dir_scripts=dir_scripts,
            project_scripts=project_scripts,
            dry_run=dry_run
        )


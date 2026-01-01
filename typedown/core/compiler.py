from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import sys
import os
import fnmatch
from rich.console import Console
from rich.table import Table

from typedown.core.mistune_parser import TypedownParser
from typedown.core.compiler_context import CompilerContext
from typedown.core.ir import Document, EntityDef, SourceLocation
from typedown.core.utils import find_project_root, IgnoreMatcher
from typedown.core.config import TypedownConfig, ScriptConfig
from typedown.core.graph import DependencyGraph

console = Console()

from typedown.core.errors import TypedownError, CycleError, ReferenceError, print_diagnostic

class Compiler:
    def __init__(self, target: Path, console: Optional[Console] = None):
        self.target = target.resolve()
        self.console = console or Console() # Default to stdout for CLI
        self.project_root = find_project_root(self.target)
        self.config = TypedownConfig.load(self.project_root / "typedown.toml")
        self.parser = TypedownParser()
        self.documents: Dict[Path, Document] = {}
        self.symbol_table: Dict[str, EntityDef] = {}
        self.ignore_matcher = IgnoreMatcher(self.project_root)
        self.target_files: Set[Path] = set()
        self.active_script: Optional[ScriptConfig] = None
        self.diagnostics: List[TypedownError] = []
        self.dependency_graph: Optional[DependencyGraph] = None
        self.model_registry: Dict[str, Any] = {}
        
    def compile(self, script_name: Optional[str] = None) -> bool:
        """Runs the full compilation pipeline."""
        self.diagnostics.clear()
        
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
            # Stage 1: Scanner (Symbols)
            self._scan(self.active_script)
            
            # Stage 2: Linker (Context & Types)
            self._link()
            
            # Stage 3: Validator (Entities & Refs)
            # This populates diagnostics
            self._validate()
            
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

    def _print_diagnostics(self):
        if not self.diagnostics:
            return
        self.console.print(f"\n[bold]Diagnostics ({len(self.diagnostics)}):[/bold]")
        for d in self.diagnostics:
            print_diagnostic(self.console, d)
        self.console.print("")

    def _scan(self, script: Optional[ScriptConfig] = None):
        """Recursively scan and parse files into IR."""
        self.console.print("  [dim]Stage 1: Scanning symbols...[/dim]")
        
        # Determine strict mode
        strict = script.strict if script else False
        
        if self.target.is_file():
            self._parse_file(self.target)
            self.target_files.add(self.target)
        else:
            extensions = {".md", ".td"}
            for root, dirs, files in os.walk(self.target):
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
                            
                            # In strict mode, only parse if it matches script scope
                            if strict and not is_match:
                                continue 
                            
                            self._parse_file(file_path)
                            
                            if is_match:
                                self.target_files.add(file_path)

        self.console.print(f"    [green]✓[/green] Found {len(self.documents)} documents ({len(self.target_files)} in target scope).")

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

    def _parse_file(self, path: Path):
        try:
            doc = self.parser.parse(path)
            self.documents[path] = doc
            
            # Unified Symbol Table population
            for collection in [doc.entities, doc.specs, doc.models]:
                for node in collection:
                    if node.id:
                        if node.id in self.symbol_table:
                            # Duplicate ID across types is also a conflict
                            existing = self.symbol_table[node.id]
                            self.console.print(f"    [bold yellow]Conflict:[/bold yellow] Duplicate ID [cyan]{node.id}[/cyan] found in {path} (previously in {existing.location.file_path})")
                        self.symbol_table[node.id] = node
        except Exception as e:
            self.console.print(f"[yellow]Warning:[/yellow] Failed to parse {path}: {e}")
            self.diagnostics.append(TypedownError(f"Parse Error: {e}", location=SourceLocation(str(path), 0, 0)))

    
    def _link(self):
        """Execute Python blocks and link symbols."""
        self.console.print("  [dim]Stage 2: Linking and type resolution...[/dim]")
        
        from pydantic import BaseModel, Field
        import typing
        import importlib
        import sys
        
        # Ensure project root is in sys.path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))

        from typedown.core.types import Ref
        
        # Base namespace for all model executions
        base_globals = {
            "BaseModel": BaseModel,
            "Field": Field,
            "Ref": Ref,
            "typing": typing,
            "List": typing.List,
            "Optional": typing.Optional,
            "Dict": typing.Dict,
            "Any": typing.Any,
            "Union": typing.Union
        }

        with CompilerContext(self.project_root) as ctx:
            # 1. Load Prelude Symbols
            if self.config.linker and self.config.linker.prelude:
                for symbol_path in self.config.linker.prelude:
                    try:
                        if "." not in symbol_path:
                            # Direct module import
                            base_globals[symbol_path] = importlib.import_module(symbol_path)
                        else:
                            # Path to a specific class/symbol
                            module_path, symbol_name = symbol_path.rsplit(".", 1)
                            module = importlib.import_module(module_path)
                            base_globals[symbol_name] = getattr(module, symbol_name)
                        self.console.print(f"    [dim]✓ Loaded prelude symbol: {symbol_path}[/dim]")
                    except Exception as e:
                        self.console.print(f"    [bold yellow]Warning:[/bold yellow] Failed to load prelude symbol '{symbol_path}': {e}")

            # 1.5 Execute Cascading Configs
            all_configs = []
            for doc in self.documents.values():
                for cfg in doc.configs:
                    all_configs.append((doc.path, cfg))
            
            # Sort by path length (depth) to ensure parent configs run first
            # Also sort by path string for determinism
            all_configs.sort(key=lambda x: (len(x[0].parts), str(x[0])))
            
            for path, cfg in all_configs:
                try:
                    base_globals["__file__"] = str(path)
                    exec(cfg.code, base_globals)
                    self.console.print(f"    [dim]✓ Executed config in {path}[/dim]")
                except Exception as e:
                     self.diagnostics.append(TypedownError(f"Config execution failed in {path}: {e}", location=cfg.location))

            # 2. Execute all model blocks
            for doc in self.documents.values():
                for model in doc.models:
                    try:
                        exec(model.code, base_globals) 
                    except Exception as e:
                        self.diagnostics.append(TypedownError(f"Model execution failed: {e}", location=model.location))

            # 3. Capture Models into Registry
            self.model_registry = {}
            for name, val in base_globals.items():
                # Check if it's a Pydantic Model (but not BaseModel itself)
                if isinstance(val, type) and issubclass(val, BaseModel) and val is not BaseModel:
                    self.model_registry[name] = val
            
            self.console.print(f"    [green]✓[/green] Registered {len(self.model_registry)} active models: {list(self.model_registry.keys())}")

    def _validate(self):
        """Materialize data and resolve references using topological sort to support cross-entity refs."""
        self.console.print("  [dim]Stage 3: Entity validation and linkage...[/dim]")
        
        from typedown.core.evaluator import Evaluator, EvaluationError
        # from typedown.core.graph import DependencyGraph

        # 1. Build Reference Graph
        # 1. Build Reference Graph
        self.dependency_graph = DependencyGraph()
        entities_by_id = {}
        
        for doc in self.documents.values():
            for entity in doc.entities:
                entities_by_id[entity.id] = entity
                # ... (former logic) ...
                if "former" in entity.data:
                    former_id = entity.data["former"]
                    if former_id in self.symbol_table:
                        self.dependency_graph.add_dependency(entity.id, former_id)

                # Scan for references in entity data
                refs = self._find_refs_in_data(entity.data)
                for ref in refs:
                    dep_id = ref.split('.')[0]
                    if dep_id in self.symbol_table:
                        self.dependency_graph.add_dependency(entity.id, dep_id)
                
                if entity.id not in self.dependency_graph.adj:
                    self.dependency_graph.adj[entity.id] = set()

        # 2. Topological Sort for evaluation order
        try:
            order = self.dependency_graph.topological_sort()
        except CycleError as e:
            self.diagnostics.append(e)
            return # Critical failure

        # 3. Resolve in order
        total_resolved = 0
        for node_id in order:
            if node_id in entities_by_id:
                entity = entities_by_id[node_id]
                
                # ... (Evolution logic omitted for brevity, assume keeps working) ...
                if "former" in entity.data:
                     former_id = entity.data["former"]
                     if former_id in self.symbol_table:
                         former_node = self.symbol_table[former_id]
                         if isinstance(former_node, EntityDef):
                             merged_data = former_node.data.copy()
                             merged_data.update(entity.data)
                             entity.data = merged_data

                try:
                    # In-place reference resolution
                    entity.data = Evaluator.evaluate_data(entity.data, self.symbol_table)
                    
                    # 4. Semantic Type Check (Ref[T])
                    self._check_semantic_types(entity)
                    
                    total_resolved += 1
                except (EvaluationError, ReferenceError) as e:
                    # Convert to TypedownError if needed, or use ReferenceError directly
                    err = ReferenceError(str(e), location=entity.location)
                    self.diagnostics.append(err)
        
        self.console.print(f"    [green]✓[/green] Resolved references for {total_resolved} entities.")

    def _check_semantic_types(self, entity: EntityDef):
        """
        Validate that Ref[T] fields actually point to entities of type T.
        """
        from typing import get_origin, get_args, Annotated
        from typedown.core.types import ReferenceMeta

        if entity.type_name not in self.model_registry:
            # We can't check types if we don't know the model
            # This might be an error or just a schemaless entity
            return

        model_cls = self.model_registry[entity.type_name]
        
        for field_name, field_info in model_cls.model_fields.items():
            # Check if field has value in data
            if field_name not in entity.data:
                continue
                
            value = entity.data[field_name]
            if not value: 
                continue

            # Inspect Type Annotation
            # Ref[T] is Annotated[str, ReferenceMeta(T)]
            # We need to look at field_info.annotation
            
            # Helper to check one annotation
            def check_annotation(annotation, val):
                if get_origin(annotation) is Annotated:
                    args = get_args(annotation)
                    # args[0] is the type (str), args[1:] are metadata
                    for meta in args[1:]:
                        if isinstance(meta, ReferenceMeta):
                            target_type = meta.target_type
                            # val should be an ID string
                            if isinstance(val, str):
                                target_entity = self.symbol_table.get(val)
                                if not target_entity:
                                    # ReferenceError would have caught this in Evaluator, but double check
                                    pass 
                                elif hasattr(target_entity, 'type_name') and target_entity.type_name != target_type:
                                    self.diagnostics.append(TypedownError(
                                        f"Type Mismatch: Field '{field_name}' expects Ref[{target_type}], but '{val}' is type '{target_entity.type_name}'",
                                        location=entity.location,
                                        severity="error"
                                    ))
                
                # Recursion for Lists: List[Ref[T]]
                # This is a bit complex with Pydantic's generic structure
                origin = get_origin(annotation)
                if origin is list or origin is List:
                    arg = get_args(annotation)[0]
                    if isinstance(val, list):
                        for item in val:
                            check_annotation(arg, item)

            check_annotation(field_info.annotation, value)


    def _find_refs_in_data(self, data: Any) -> Set[str]:
        """Helper to find all [[...]] content in a data structure."""
        from typedown.core.evaluator import REF_PATTERN
        refs = set()
        if isinstance(data, dict):
            for v in data.values():
                refs.update(self._find_refs_in_data(v))
        elif isinstance(data, list):
            for v in data:
                refs.update(self._find_refs_in_data(v))
        elif isinstance(data, str):
            for m in REF_PATTERN.finditer(data):
                refs.add(m.group(1))
        return refs

    def query(self, query_string: str) -> Any:
        """
        GraphQL-like query interface for the symbol table.
        Example: compiler.query("User.profile.email")
        """
        from typedown.core.evaluator import Evaluator
        return Evaluator.resolve_query(query_string, self.symbol_table)

    def run_tests(self, tags: List[str] = []) -> int:
        """Stage 4: Pytest Backend execution."""
        console.print("  [dim]Stage 4: Executing specs...[/dim]")
        # This will move logic from test.py here
        return 0

    def get_entities_by_type(self, type_name: str) -> List[Any]:
        """Compatibility method for existing specs."""
        results = []
        for node in self.symbol_table.values():
            if isinstance(node, EntityDef) and node.type_name == type_name:
                # Use AttributeWrapper to allow dot notation
                results.append(AttributeWrapper(node.data))
        return results

    def get_entity(self, entity_id: str) -> Optional[Any]:
        """Compatibility method for existing specs."""
        entity = self.symbol_table.get(entity_id)
        if entity:
            return AttributeWrapper(entity.data)
        return None

    def get_stats(self):
        return {
            "documents": len(self.documents),
            "target_documents": len(self.target_files),
            "symbols": len(self.symbol_table),
            "entities": sum(len(doc.entities) for doc in self.documents.values()),
            "models": sum(len(doc.models) for doc in self.documents.values()),
            "specs": sum(len(doc.specs) for doc in self.documents.values()),
            "root": str(self.project_root)
        }

class AttributeWrapper:
    """Helper to allow accessing dictionary keys as attributes."""
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def __getattr__(self, item):
        if item == "resolved_data":
            return self
        if item in self._data:
            val = self._data[item]
            if isinstance(val, list):
                 # Fixed list recursion
                 return [AttributeWrapper(x) if isinstance(x, dict) else x for x in val]
            if isinstance(val, dict):
                return AttributeWrapper(val)
            return val
        raise AttributeError(f"'AttributeWrapper' object has no attribute '{item}'")
        
    def __repr__(self):
        return repr(self._data)

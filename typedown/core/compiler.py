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

console = Console()

class Compiler:
    """
    Typedown Compiler Implementation (LLVM-style Pipeline).
    Stages:
    1. Symbols (Scanner): Extract skeletons from all files.
    2. Linkage (Linker): Execute python configs and resolve types.
    3. Entities (Validator): Materialize data and check constraints.
    4. Execution (Backend): Run specs/tests.
    """
    
    def __init__(self, target: Path):
        self.target = target.resolve()
        self.project_root = find_project_root(self.target)
        self.config = TypedownConfig.load(self.project_root / "typedown.toml")
        self.parser = TypedownParser()
        self.documents: Dict[Path, Document] = {}
        self.symbol_table: Dict[str, EntityDef] = {}
        self.ignore_matcher = IgnoreMatcher(self.project_root)
        self.target_files: Set[Path] = set()
        self.active_script: Optional[ScriptConfig] = None
        
    def compile(self, script_name: Optional[str] = None) -> bool:
        """Runs the full compilation pipeline."""
        if script_name:
            if script_name not in self.config.scripts:
                console.print(f"[bold red]Error:[/bold red] Script '{script_name}' not found in typedown.toml")
                return False
            self.active_script = self.config.scripts[script_name]
            console.print(f"[bold blue]Typedown Compiler:[/bold blue] Starting pipeline for script [cyan]:{script_name}[/cyan]")
        else:
            console.print(f"[bold blue]Typedown Compiler:[/bold blue] Starting pipeline for [cyan]{self.target}[/cyan]")
        
        try:
            # Stage 1: Scanner (Symbols)
            self._scan(self.active_script)
            
            # Stage 2: Linker (Context & Types)
            # We need to execute python blocks in a managed environment
            self._link()
            
            # Stage 3: Validator (Entities & Refs)
            self._validate()
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]Compilation Failed:[/bold red] {e}")
            import traceback
            console.print(traceback.format_exc())
            return False

    def _scan(self, script: Optional[ScriptConfig] = None):
        """Recursively scan and parse files into IR."""
        console.print("  [dim]Stage 1: Scanning symbols...[/dim]")
        
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

        console.print(f"    [green]✓[/green] Found {len(self.documents)} documents ({len(self.target_files)} in target scope).")

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
        doc = self.parser.parse(path)
        self.documents[path] = doc
        
        # Unified Symbol Table population
        for collection in [doc.entities, doc.specs, doc.models]:
            for node in collection:
                if node.id:
                    if node.id in self.symbol_table:
                        # Duplicate ID across types is also a conflict
                        existing = self.symbol_table[node.id]
                        console.print(f"    [bold yellow]Conflict:[/bold yellow] Duplicate ID [cyan]{node.id}[/cyan] found in {path} (previously in {existing.location.file_path})")
                    self.symbol_table[node.id] = node

    def _link(self):
        """Execute Python blocks and link symbols."""
        console.print("  [dim]Stage 2: Linking and type resolution...[/dim]")
        
        from pydantic import BaseModel, Field
        import typing
        import importlib
        
        # Base namespace for all model executions
        base_globals = {
            "BaseModel": BaseModel,
            "Field": Field,
            "typing": typing,
            "List": typing.List,
            "Optional": typing.Optional,
            "Dict": typing.Dict,
            "Any": typing.Any
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
                        console.print(f"    [dim]✓ Loaded prelude symbol: {symbol_path}[/dim]")
                    except Exception as e:
                        console.print(f"    [bold yellow]Warning:[/bold yellow] Failed to load prelude symbol '{symbol_path}': {e}")

            # 2. Execute all model blocks
            for doc in self.documents.values():
                for model in doc.models:
                    try:
                        # We execute in a per-project scope for now
                        # Ideally per-directory cascading like Workspace did
                        # But let's start with project-wide.
                        exec(model.code, base_globals) 
                    except Exception as e:
                        console.print(f"    [yellow]Warning:[/yellow] Model execution failed in {doc.path}: {e}")
            
            # 2. Match entities to Pydantic classes 
            # (Stage 2 of LLVM: Linkage)
            # This requires the registries built during execution.
            pass

    def _validate(self):
        """Materialize data and resolve references using topological sort to support cross-entity refs."""
        console.print("  [dim]Stage 3: Entity validation and linkage...[/dim]")
        
        from typedown.core.evaluator import Evaluator, EvaluationError, REF_PATTERN
        from typedown.core.graph import DependencyGraph

        # 1. Build Reference Graph
        graph = DependencyGraph()
        entities_by_id = {}
        
        for doc in self.documents.values():
            for entity in doc.entities:
                entities_by_id[entity.id] = entity
                # Check for inheritance/evolution (former)
                if "former" in entity.data:
                    former_id = entity.data["former"]
                    if former_id in self.symbol_table:
                        graph.add_dependency(entity.id, former_id)

                # Scan for references in entity data
                refs = self._find_refs_in_data(entity.data)
                for ref in refs:
                    # ref might be 'ID.attr', we only care about 'ID' for graph dependencies
                    dep_id = ref.split('.')[0]
                    if dep_id in self.symbol_table:
                        graph.add_dependency(entity.id, dep_id)
                
                # Ensure all entities are in the graph even if they have no dependencies
                if entity.id not in graph.adj:
                    graph.adj[entity.id] = set()

        # 2. Topological Sort for evaluation order
        order = graph.topological_sort()

        # 3. Resolve in order
        total_resolved = 0
        for node_id in order:
            if node_id in entities_by_id:
                entity = entities_by_id[node_id]
                
                # Handle evolution (former)
                if "former" in entity.data:
                    former_id = entity.data["former"]
                    if former_id in self.symbol_table:
                        former_node = self.symbol_table[former_id]
                        if isinstance(former_node, EntityDef):
                            # Merge data: current fields override former fields
                            # Note: We do this BEFORE resolution because former_node should 
                            # already be resolved (due to topological order).
                            merged_data = former_node.data.copy()
                            merged_data.update(entity.data)
                            entity.data = merged_data

                try:
                    # In-place reference resolution
                    entity.data = Evaluator.evaluate_data(entity.data, self.symbol_table)
                    total_resolved += 1
                except EvaluationError as e:
                    console.print(f"    [bold red]Linkage Error:[/bold red] {e} in {node_id}")
        
        console.print(f"    [green]✓[/green] Resolved references for {total_resolved} entities in dependency order.")

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

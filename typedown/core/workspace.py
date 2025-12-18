from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import sys
import os
from rich.console import Console
from pydantic import ValidationError
import typer

from typedown.core.ast import Project, Document, EntityBlock
from typedown.core.parser import Parser
from typedown.core.resolver import Resolver, CircularDependencyError
from typedown.core.merger import Merger
from typedown.core.evaluator import Evaluator, EvaluationError
from typedown.core.validator import Validator
from typedown.core.errors import TypedownError, print_diagnostic
from typedown.core.spec_runner import SpecRunner
from typedown.core.utils import find_project_root, IgnoreMatcher
from typedown.core.context_manager import ContextManager, ClassRegistry # Import new components

# Use stderr for console output only in LSP mode to avoid breaking protocol
use_stderr = os.getenv("TYPEDOWN_LSP_MODE") == "1"
console = Console(stderr=use_stderr)

class Workspace:
    def __init__(self, root: Path = Path(".")):
        self.target_path = root.resolve()
        
        # 1. Detect Project Root (for Ignoring and Sys Path)
        self.project_root = find_project_root(self.target_path)
        
        # 2. Set Workspace Root
        # We generally treat the target_path as the root for relative paths in documents
        # UNLESS target_path is a file, then it's the parent.
        if self.target_path.is_file():
            self.root = self.target_path.parent
        else:
            self.root = self.target_path

        self.project = Project(root_dir=self.root)
        self.parser = Parser()
        
        # 3. Initialize ContextManager
        self.context_manager = ContextManager(self.project_root)
        
        # Ensure the Workspace root is also in sys.path if it differs from Project Root
        # This fixes the case where we run 'td validate use_cases/xxx' and that subfolder is self-contained
        if self.root != self.project_root and str(self.root) not in sys.path:
            sys.path.insert(0, str(self.root))
        
        self.resolver = Resolver(self.project)
        # Validator will be initialized per entity with its specific registry

        # 4. Ignore Matcher
        self.ignore_matcher = IgnoreMatcher(self.project_root)
        
        # Store a mapping from document path to its ClassRegistry
        self.document_registries: Dict[Path, ClassRegistry] = {}

        # Legacy Loader (kept for compatibility if needed, though largely superseded by ContextManager)
        from typedown.core.loader import Loader
        self.loader = Loader(self.project_root)

    def load(self, target: Path):
        """
        Load a file or directory into the workspace.
        """
        target = target.resolve()
        
        # 1. Scan and Parse Files
        if target.is_file():
            self._parse_single_file(target)
        elif target.is_dir():
            self._scan_directory(target)
        else:
            raise ValueError(f"Target path does not exist: {target}")
            
        # 2. Build Class Contexts for all loaded documents
        self._build_all_document_contexts()

    def _build_all_document_contexts(self):
        """
        Builds the ClassRegistry for every loaded document.
        """
        # First, gather all config.td documents to pass to ContextManager
        # We need a dict mapping Path -> Document (where Document contains python_scripts)
        config_td_docs = {}
        for rel_path_str, doc in self.project.documents.items():
            # rel_path_str is string relative to self.root
            abs_path = (self.root / rel_path_str).resolve()
            if abs_path.name == "config.td":
                config_td_docs[abs_path] = doc
        
        # Now iterate over all documents and build their context
        for rel_path_str, doc in self.project.documents.items():
            abs_path = (self.root / rel_path_str).resolve()
            registry = self.context_manager.get_document_registry(abs_path, config_td_docs, current_doc=doc)
            self.document_registries[abs_path] = registry


    def reindex_file(self, file_path: Path, content: str = None):
        """
        Re-parse a single file and update the project symbol tables.
        Used for incremental updates (LSP).
        """
        # 1. Remove existing symbols belonging to this file
        self._remove_symbols_for_file(file_path)
        
        # 2. Re-parse
        try:
            # We must handle new files that might not be in self.project.documents yet
            self._parse_single_file(file_path, content_override=content)
            
            # 3. Update Registry if needed (ContextManager handles cache, but we might need to refresh)
            # For now, just re-building for this document is safe enough
            abs_path = file_path.resolve()
            # We need to re-scan for config.td docs just in case, or assume they haven't changed much?
            # For strict correctness we re-build context.
            # Reuse the existing config_td logic from _build_all_document_contexts would be costly?
            # Let's simple try to get registry again.
            # NOTE: If this file IS a config.td, we should ideally reload context for its directory.
            # This is complex. MVP: simple re-parse.
            
            # Since _parse_single_file adds symbols to the table, we are good.
            
        except Exception as e:
            # If parsing fails (e.g. syntax error), we should probably record that as a diagnostic
            # But _parse_single_file currently catches some and prints warnings.
            # We might want to let it propagate or catch here.
            # modifying _parse_single_file to raise might be better for LSP.
            # For now, let's rely on it completing or raising.
            raise e

    def _remove_symbols_for_file(self, file_path: Path):
        """
        Remove all entities and specs defined in the given file from the global tables.
        """
        str_path = str(file_path)
        rel_path = str(file_path.relative_to(self.root))
        
        # Remove Document
        if rel_path in self.project.documents:
            del self.project.documents[rel_path]
            
        # Remove Entities
        ids_to_remove = []
        for entity_id, entity in self.project.symbol_table.items():
            if Path(entity.location.file_path).resolve() == file_path.resolve():
                ids_to_remove.append(entity_id)
        
        for eid in ids_to_remove:
            del self.project.symbol_table[eid]
            
        # Remove Specs
        spec_ids_to_remove = []
        for spec_id, spec in self.project.spec_table.items():
            if Path(spec.location.file_path).resolve() == file_path.resolve():
                spec_ids_to_remove.append(spec_id)
                
        for sid in spec_ids_to_remove:
            del self.project.spec_table[sid]

    def validate_project(self, tags: List[str] = []) -> List[TypedownError]:
        """
        Run the full validation pipeline and return a list of errors/diagnostics.
        Does NOT exit the process.
        """
        diagnostics: List[TypedownError] = []
        
        try:
            # 1. Build Dependency Graph
            self.resolver.build_graph()
            
            # 2. Topological Sort
            sorted_ids = self.resolver.topological_sort()
            
            # 3. Materialize Entities
            for entity_id in sorted_ids:
                try:
                    self._materialize_entity(entity_id)
                except TypedownError as e:
                    diagnostics.append(e)
                except EvaluationError as e:
                    loc = self.project.symbol_table[entity_id].location if entity_id in self.project.symbol_table else None
                    diagnostics.append(TypedownError(str(e), location=loc))
                except ValidationError as e:
                    # Convert Pydantic error to TypedownError (simplified for now)
                    loc = self.project.symbol_table[entity_id].location
                    diagnostics.append(TypedownError(str(e), location=loc))
                except Exception as e:
                     loc = self.project.symbol_table[entity_id].location
                     diagnostics.append(TypedownError(f"Unexpected error: {e}", location=loc))

            # 4. Run Specs
            if self.project.spec_table:
                # Runner prints to console currently, we need to adapt checking logic
                # For LSP, maybe we skip specs if they rely on pytest runner output?
                # Or we wrap runner to capture failures?
                # MVP: Skip spec runner in LSP fast-path or just catch global errors?
                # The prompt asks for "Code Lens (Run Specs)" in P2.
                # In P0 Diagnostics: "syntax error, validation error, invalid reference". 
                # Specs are P2. So we can skip SpecRunner for now in this function used by LSP.
                pass

        except CircularDependencyError as e:
             # This is a global error
             diagnostics.append(TypedownError(f"Circular Dependency: {e}", severity="error"))
        except Exception as e:
            diagnostics.append(TypedownError(f"Global Validation Error: {e}", severity="error"))
            
        return diagnostics

    def resolve(self, tags: List[str] = []):
        """
        CLI Entry point: Run validation and exit on error.
        """
        console.print("[blue]Building dependency graph...[/blue]")
        
        diagnostics = self.validate_project(tags)
        
        # Check for errors
        has_error = False
        for diag in diagnostics:
            print_diagnostic(console, diag)
            if diag.severity == "error":
                has_error = True
        
        if has_error:
            raise typer.Exit(code=1)
            
        console.print(f"[green]Successfully processed entities.[/green]")
        
        # Run specs only in CLI mode for now
        if self.project.spec_table:
            console.print(f"[blue]Running specs (tags={tags})...[/blue]")
            runner = SpecRunner(self.project, self.root)
            specs_passed = runner.run(tags=tags)
            if not specs_passed:
                console.print(f"[bold red]Spec validation failed.[/bold red]")
                raise typer.Exit(code=1)
            else:
                console.print(f"[green]All specs passed.[/green]")

    def _materialize_entity(self, entity_id: str):
        """
        Pipeline: Merge Parent -> Resolve References -> Validate Schema
        """
        entity = self.project.symbol_table[entity_id]
        parent_id = None
        
        # Determine Parent
        if entity.former_ref:
            parent_id = entity.former_ref.target_query
        elif entity.derived_from_ref:
            parent_id = entity.derived_from_ref.target_query
            
        parent_data = {}
        if parent_id:
            if parent_id in self.project.symbol_table:
                # Parent MUST be processed already due to topological sort
                parent_data = self.project.symbol_table[parent_id].resolved_data
            else:
                # This should be caught by resolver validation, but just in case
                raise TypedownError(f"Entity refers to missing parent '{parent_id}'", location=entity.location)
        
        # 1. Execute Merge
        merged = Merger.merge(parent_data, entity.raw_data)
        
        # 2. Resolve References (Evaluator)
        # Replaces [[query]] strings with actual values from symbol_table
        # EvaluationError will be caught above
        resolved_refs = Evaluator.evaluate_data(merged, self.project.symbol_table)
        
        # 3. Validate Data (Validator)
        # Checks against Pydantic models loaded from imports
        # validated = self.validator.validate(entity.id, entity.class_name, resolved_refs)
        
        # New Logic: Use per-document registry
        entity_path = Path(entity.location.file_path).resolve()
        registry = self.document_registries.get(entity_path)
        
        if not registry:
            # Should not happen if _build_all_document_contexts worked correctly
            # But let's handle graceful fallback or empty registry
            # console.print(f"[warning] No registry found for {entity_path}, using empty.")
            registry = ClassRegistry()

        validator = Validator(registry)
        validated = validator.validate(entity.id, entity.class_name, resolved_refs)
        
        # 4. Store Result
        entity.resolved_data = validated

    def get_entities_by_type(self, class_name: str) -> List[Any]:
        """
        Retrieves all entities of a specific type (class name).
        Returns a list of objects allowing dot-notation access to fields.
        """
        results = []
        for entity in self.project.symbol_table.values():
            # Simple matching: exact match or suffix match (e.g. "Monster" matches "models.Monster")
            if entity.class_name == class_name or entity.class_name.endswith(f".{class_name}"):
                # Wrap the dictionary to allow dot access (e.g. entity.hp)
                results.append(AttributeWrapper(entity.resolved_data))
        return results

    def _scan_directory(self, dir_path: Path):
        """
        Recursively scan directory for markdown files, respecting ignore patterns.
        """
        # Supports .md and .td extensions
        extensions = {".md", ".td"}
        
        # Use os.walk for better control over ignoring directories
        for root, dirs, files in os.walk(dir_path):
            root_path = Path(root)
            
            # Check if current directory should be ignored
            if self.ignore_matcher.is_ignored(root_path):
                # Empty dirs to prevent recursion
                dirs[:] = []
                continue
                
            # Filter subdirectories in-place to prevent os.walk from entering them
            # We iterate backwards to safely remove items
            for i in range(len(dirs) - 1, -1, -1):
                d = dirs[i]
                d_path = root_path / d
                if self.ignore_matcher.is_ignored(d_path):
                    del dirs[i]
            
            for file in files:
                file_path = root_path / file
                if file_path.suffix in extensions:
                    if not self.ignore_matcher.is_ignored(file_path):
                        # console.print(f"[debug] Parsing {file_path}")
                        self._parse_single_file(file_path)
                    else:
                        pass
                        # console.print(f"[debug] Ignored {file_path}")

    def _parse_single_file(self, file_path: Path, content_override: str = None):
        """
        Parse a file and register it in the project.
        """
        try:
            doc = self.parser.parse_file(file_path, content_override=content_override)
            
            # Store Document
            rel_path = str(file_path.relative_to(self.root))
            self.project.documents[rel_path] = doc
            rel_path = str(file_path.relative_to(self.root))
            self.project.documents[rel_path] = doc
            
            # Register Symbols
            for entity in doc.entities:
                if entity.id in self.project.symbol_table:
                    # Duplicate ID Conflict
                    existing = self.project.symbol_table[entity.id]
                    msg = f"Duplicate Entity ID '{entity.id}' found."
                    # Provide context on where the duplicate is
                    existing_loc = f"{existing.location.file_path}:{existing.location.line_start}"
                    msg += f" (First defined in {existing_loc})"
                    raise TypedownError(msg, location=entity.location)
                else:
                    self.project.symbol_table[entity.id] = entity
            
            # Register Specs
            for spec in doc.specs:
                if spec.id in self.project.spec_table:
                     existing = self.project.spec_table[spec.id]
                     msg = f"Duplicate Spec ID '{spec.id}' found."
                     raise TypedownError(msg, location=spec.location)
                else:
                     self.project.spec_table[spec.id] = spec
                    
        except TypedownError:
            raise
        except Exception as e:
            console.print(f"[bold yellow]Warning:[/bold yellow] Failed to parse {file_path}: {e}")

    def _process_imports(self):
        """
        Collect imports from all loaded documents and register them.
        """
        for doc in self.project.documents.values():
            if "imports" in doc.config:
                self.loader.load_imports(doc.config["imports"])

    def get_stats(self):
        return {
            "documents": len(self.project.documents),
            "entities": len(self.project.symbol_table),
            "specs": len(self.project.spec_table),
            "root": str(self.project.root_dir)
        }
class AttributeWrapper:
    """Helper to allow accessing dictionary keys as attributes."""
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def __getattr__(self, item):
        if item in self._data:
            val = self._data[item]
            if isinstance(val, dict):
                return AttributeWrapper(val)
            if isinstance(val, list):
                return [AttributeWrapper(x) if isinstance(x, dict) else x for x in val]
            return val
        raise AttributeError(f"'AttributeWrapper' object has no attribute '{item}'")
        
    def __getitem__(self, item):
        return self._data[item]
        
    def __repr__(self):
        return repr(self._data)

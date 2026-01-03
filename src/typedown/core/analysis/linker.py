import sys
import importlib
import typing
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

from typedown.core.ast.document import Document
from typedown.core.ast.base import SourceLocation
from typedown.core.base.errors import TypedownError
from typedown.core.analysis.compiler_context import CompilerContext
from typedown.core.base.config import TypedownConfig
from typedown.core.base.types import Ref
from typedown.core.base.utils import AttributeWrapper
from typedown.core.base.symbol_table import SymbolTable


class Linker:
    """
    Stage 2: Linking & Resolution.
    - Builds the SymbolTable (Path-Aware).
    - Executes 'config' blocks to populate Scoped Handles.
    - Executes 'model' blocks to register Pydantic Models.
    """
    def __init__(self, project_root: Path, config: TypedownConfig, console):
        self.project_root = project_root
        self.config = config
        self.console = console
        self.diagnostics: List[TypedownError] = []
        
        # New Symbol Table
        self.symbol_table = SymbolTable()
        
        # Global Model Registry (still flat for now, as Models are usually types)
        # We could move this into Symbol Table global index too, but kept separate for clarity logic
        self.model_registry: Dict[str, Any] = {}
        
        # Context Cache: Path (Directory) -> Globals Dict
        self.dir_contexts: Dict[Path, Dict[str, Any]] = {}
        
        self.base_globals: Dict[str, Any] = {}

    def link(self, documents: Dict[Path, Document]):
        """
        Builds the symbol table and executes Python blocks (configs/models) to build the runtime environment.
        """
        self.console.print("  [dim]Stage 2: Linking and type resolution...[/dim]")
        
        # 1. Populate Symbol Table with static AST nodes (Entity, Specs)
        self._build_static_symbols(documents)

        # 2. Setup Base Environment
        self._setup_globals()

        # 3. Execute Configs (Scoped Execution)
        self._execute_configs(documents)

        # 4. Execute Models (Global Execution or Per-File?)
        # Models are usually global definitions.
        self._execute_models(documents)
        
        # 5. Finalize Pydantic Models (Resolve Forward Refs)
        self._finalize_models()

    def _finalize_models(self):
        """Call model_rebuild() on all registered models to resolve forward references."""
        for name, model_cls in self.model_registry.items():
            if hasattr(model_cls, "model_rebuild"):
                try:
                    # Provide the registry as the namespace for resolution
                    model_cls.model_rebuild(_types_namespace=self.model_registry)
                except Exception as e:
                    self.diagnostics.append(TypedownError(
                        f"Failed to rebuild model '{name}': {e}", 
                        severity="warning"
                    ))

    def _build_static_symbols(self, documents: Dict[Path, Document]):
        """Register Entity/Spec nodes into SymbolTable."""
        for path, doc in documents.items():
            # Unified Symbol Table population
            # We add Entities and Specs. Models are executed, not just linked by ID (usually).
            for collection in [doc.entities, doc.specs, doc.models]:
                for node in collection:
                    if node.id:
                        try:
                            self.symbol_table.add(node, path)
                        except ValueError as e:
                            # Handle duplicate error
                            self.diagnostics.append(TypedownError(
                                str(e), location=node.location, severity="error"
                            ))

    def _setup_globals(self):
        # Ensure project root is in sys.path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))

        self.base_globals = {
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

        # Load Prelude Symbols
        if self.config.linker and self.config.linker.prelude:
            with CompilerContext(self.project_root):
                for symbol_path in self.config.linker.prelude:
                    try:
                        if "." not in symbol_path:
                            # Direct module import
                            self.base_globals[symbol_path] = importlib.import_module(symbol_path)
                        else:
                            # Path to a specific class/symbol
                            module_path, symbol_name = symbol_path.rsplit(".", 1)
                            module = importlib.import_module(module_path)
                            self.base_globals[symbol_name] = getattr(module, symbol_name)
                        self.console.print(f"    [dim]✓ Loaded prelude symbol: {symbol_path}[/dim]")
                    except Exception as e:
                        msg = f"Failed to load prelude symbol '{symbol_path}': {e}"
                        self.console.print(f"    [bold yellow]Warning:[/bold yellow] {msg}")
                        self.diagnostics.append(TypedownError(msg, severity="warning"))

    def _execute_configs(self, documents: Dict[Path, Document]):
        """
        Execute configs hierarchically.
        Resulting variables are registered as Handles in the SymbolTable Scope.
        """
        all_configs = []
        for doc in documents.values():
            for cfg in doc.configs:
                all_configs.append((doc.path, cfg))
        
        # Sort by path length to ensure parent configs run first
        all_configs.sort(key=lambda x: (len(x[0].parts), str(x[0])))
        
        # Cache of Contexts: Path -> Globals Dict
        # Key is the DIRECTORY of the config file
        # We reuse self.dir_contexts populated here for later stages.
        self.dir_contexts.clear()
        
        with CompilerContext(self.project_root):
            for path, cfg in all_configs:
                config_dir = path.parent
                
                # 1. Determine Base Context
                # Find the nearest parent directory that had a config
                parent_context = self.base_globals
                # Walk up from config_dir.parent
                for parent in config_dir.parents:
                     if parent in self.dir_contexts:
                         parent_context = self.dir_contexts[parent]
                         break
                if config_dir in self.dir_contexts:
                     # Multiple configs in same dir? Merge/Chain.
                     parent_context = self.dir_contexts[config_dir]

                # 2. Create Isolated Scope
                current_locals = parent_context.copy()
                current_locals["__file__"] = str(path)
                
                try:
                    exec(cfg.code, current_locals)
                    self.console.print(f"    [dim]✓ Executed config in {path}[/dim]")
                except Exception as e:
                     self.diagnostics.append(TypedownError(f"Config execution failed in {path}: {e}", location=cfg.location))
                     continue

                # 3. Store Context for Children
                self.dir_contexts[config_dir] = current_locals
                
                # 4. Extract Exports -> SymbolTable & ModelRegistry
                self._harvest_exports(current_locals, path, cfg.location)

    def _execute_models(self, documents: Dict[Path, Document]):
        """
        Execute model blocks. These are typically global schema definitions.
        """
        # We share a common context for models or use the per-file context?
        # Ideally, models should be robust and self-contained or import what they need.
        # But we want them to benefit from 'config:python' injections (sys.path, etc).
        
        with CompilerContext(self.project_root):
             for doc in documents.values():
                # 1. Determine Context for this file
                doc_dir = doc.path.parent
                context = None
                
                # Check exact dir
                if doc_dir in self.dir_contexts:
                    context = self.dir_contexts[doc_dir]
                else:
                    # Walk up
                    for parent in doc_dir.parents:
                        if parent in self.dir_contexts:
                            context = self.dir_contexts[parent]
                            break
                
                # If no config context found, start from base
                if context is None:
                    context = self.base_globals


                for model in doc.models:
                    # Capture locals
                    # Mixin global model registry to allow cross-references? 
                    # Generally Pydantic models referencing each other need to be in scope.
                    # We inject them.
                    local_scope = context.copy()
                    local_scope.update(self.model_registry)
                    
                    local_scope["__file__"] = str(doc.path)
                    try:
                        exec(model.code, local_scope)
                        
                        # L2 Check: Strict Class Name Consistency
                        # The model block ID MUST match the defined Pydantic class name
                        if model.id:
                            if model.id not in local_scope:
                                self.diagnostics.append(TypedownError(
                                    f"Model block ID '{model.id}' does not match any class defined in the block. "
                                    f"The class name must exactly match the block ID.",
                                    location=model.location,
                                    severity="error"
                                ))
                                continue
                            
                            defined_class = local_scope[model.id]
                            
                            # Verify it's a Pydantic model OR an Enum
                            is_model = isinstance(defined_class, type) and issubclass(defined_class, BaseModel)
                            is_enum = isinstance(defined_class, type) and issubclass(defined_class, Enum)
                            
                            if not (is_model or is_enum):
                                self.diagnostics.append(TypedownError(
                                    f"Model block ID '{model.id}' refers to '{type(defined_class).__name__}', "
                                    f"which is not a Pydantic BaseModel or Enum class.",
                                    location=model.location,
                                    severity="error"
                                ))
                                continue
                            
                            # Register the model
                            self.model_registry[model.id] = defined_class
                        
                        # Also harvest any other BaseModel classes defined in the block
                            for name, val in local_scope.items():
                                 is_valid_type = isinstance(val, type) and (issubclass(val, BaseModel) or issubclass(val, Enum))
                                 if is_valid_type and val is not BaseModel and val is not Enum:
                                     if name not in self.model_registry:
                                         self.model_registry[name] = val
                        
                    except Exception as e:
                        self.diagnostics.append(TypedownError(f"Model execution failed: {e}", location=model.location))

    def _harvest_exports(self, scope: Dict[str, Any], source_path: Path, location: Optional[SourceLocation] = None):
        """
        Extract variables from a scope and register them into SymbolTable and ModelRegistry.
        """
        for name, val in scope.items():
            if name.startswith("_"):
                continue
                
            # 1. Register Pydantic Models & Enums globally
            is_valid_type = isinstance(val, type) and (issubclass(val, BaseModel) or issubclass(val, Enum))
            if is_valid_type and val is not BaseModel and val is not Enum:
                self.model_registry[name] = val
            
            # 2. Register Everything as a Handle in the current scope
            # Use a wrapper instance with basic Node-like attributes
            wrapper = AttributeWrapper({
                "id": name, 
                "value": val, 
                "type": "variable",
                "location": location
            })
            self.symbol_table.add(wrapper, source_path)

from typing import Dict, Any, List, Set, get_origin, get_args, Annotated
from pathlib import Path
from rich.console import Console

from typedown.core.ast import Document, EntityBlock, SourceLocation
from typedown.core.base.errors import (
    TypedownError, CycleError, ReferenceError,
    ErrorCode, ErrorLevel,
    validator_error, DiagnosticReport
)
from typedown.core.graph import DependencyGraph
from typedown.core.analysis.query import QueryEngine, QueryError, REF_PATTERN
from typedown.core.base.types import ReferenceMeta
from typedown.core.base.identifiers import Identifier
from typedown.core.base.symbol_table import SymbolTable
from typedown.core.base.utils import AttributeWrapper
from pydantic import BaseModel


class Validator:
    def __init__(self, console: Console):
        self.console = console
        self.diagnostics = DiagnosticReport()
        self.dependency_graph: DependencyGraph = DependencyGraph()

    def _resolve_model_class(self, entity: EntityBlock, symbol_table: SymbolTable, model_registry: Dict[str, Any]) -> Any:
        """
        Resolve the Pydantic model class for an entity, prioritizing local scope.
        """
        # 1. Try Scoped Lookup via SymbolTable (lexical scoping)
        if entity.location and entity.location.file_path:
            context_path = Path(entity.location.file_path)
            # Linker registers models as AttributeWrapper in SymbolTable
            wrapper = symbol_table.resolve_handle(entity.class_name, context_path)
            
            if wrapper and isinstance(wrapper, AttributeWrapper):
                val = wrapper.value
                # Verify it is a Pydantic Model
                if isinstance(val, type) and issubclass(val, BaseModel):
                    return val
            elif wrapper and isinstance(wrapper, type) and issubclass(wrapper, BaseModel):
                # Direct registration (future proofing)
                return wrapper

        # 2. Fallback to Global Registry
        return model_registry.get(entity.class_name)

    def validate(self, documents: Dict[Path, Document], symbol_table: SymbolTable, model_registry: Dict[str, Any]):
        """
        L3: Materialize data and resolve references using topological sort to support cross-entity refs.
        """
        self.console.print("  [dim]Stage 3: Entity validation and linkage...[/dim]")
        
        # ... (implementation of validate as before but updated below if needed)
        # 2. Topological Sort for evaluation order
        # We need to build the graph first.
        self.dependency_graph = DependencyGraph()
        entities_by_id = {}
        
        from typedown.core.parser.desugar import Desugarer

        for doc in documents.values():
            for entity in doc.entities:
                if not entity.id: continue
                entities_by_id[entity.id] = entity
                
                if entity.former_ids:
                    # former_ids are stored in AST, but might still contain [[ ]] brackets if they were raw strings
                    # We should handle them.
                    for f_id in entity.former_ids:
                        target_id = f_id
                        match = REF_PATTERN.match(f_id)
                        if match:
                            target_id = match.group(1)
                        
                        if target_id in symbol_table:
                            self.dependency_graph.add_dependency(entity.id, target_id)

                # Relaxed Validation:
                # We NO LONGER add dependencies for standard references (lines 50-54 removed).
                # This enables circular references (e.g. OrgUnit <-> Head) which are handled via Late Binding.
                # The dependency graph now ONLY constrains Evolution (former) time-travel.
                
                if entity.id not in self.dependency_graph.adj:
                    self.dependency_graph.adj[entity.id] = set()

        # 2. Topological Sort for evaluation order
        try:
            order = self.dependency_graph.topological_sort()
        except CycleError as e:
            # Attempt to attach location if possible
            cycle_msg = str(e)
            # Message format: "Circular dependency detected: a -> b -> a"
            if ": " in cycle_msg:
                 parts = cycle_msg.split(": ")[1].split(" -> ")
                 if parts and parts[0] in entities_by_id:
                     e.location = entities_by_id[parts[0]].location
            
            self.diagnostics.add(e)
            return

        # 3. Resolve in order
        total_resolved = 0
        for node_id in order:
            if node_id in entities_by_id:
                entity = entities_by_id[node_id]
                self._resolve_entity(entity, symbol_table, model_registry)
                total_resolved += 1
        
        self.console.print(f"    [green]✓[/green] Resolved references for {total_resolved} entities.")

    def check_schema(self, documents: Dict[Path, Document], symbol_table: SymbolTable, model_registry: Dict[str, Any]):
        """
        L2: Schema Compliance Check. 
        Validates structure without resolving the graph.
        """
        self.console.print("  [dim]Stage 2.5: Running L2 Schema Check (Pydantic)...[/dim]")
        from pydantic import ValidationError
        
        total_checked = 0
        for doc in documents.values():
            for entity in doc.entities:
                model_cls = self._resolve_model_class(entity, symbol_table, model_registry)
                
                if not model_cls:
                    # Missing model is handled by Linker usually, but we can log error here too if helpful
                    continue
                
                from typedown.core.parser.desugar import Desugarer
                
                # Pre-process: Desugar YAML artifacts (e.g. [['ref']] -> "[[ref]]")
                data = Desugarer.desugar(entity.raw_data)
                
                # Auto-inject ID from Signature if missing in Body (Signature as Identity)
                if "id" in data:
                    self.diagnostics.add(validator_error(
                        ErrorCode.E0363,
                        entity_id=entity.id,
                        location=entity.location
                    ))
                    # Fallthrough to validation to catch other errors, but using the user-provided ID
                elif entity.id:
                    data["id"] = entity.id

                try:
                    # Fuzzy validate: We use model_cls.model_construct if we want to skip validation
                    # but for L2 we WANT validation. 
                    # To avoid [[ref]] failing int check, we'd need a custom Validator in Pydantic.
                    # For now, let's just attempt instantiation and report real errors.
                    
                    model_cls(**data)
                    total_checked += 1
                except ValidationError as e:
                    # Filter out errors that are likely caused by references
                    # (e.g. expected int, got string "[[...]]")
                    real_errors = []
                    for error in e.errors():
                        # If the value is a string and looks like a reference, ignore it for L2
                        # This is a bit hacky but fits the "Fuzzy L2" requirement.
                        loc = error['loc']
                        # Find the value in raw_data (desugared) using loc
                        val = data
                        try:
                            for part in loc:
                                val = val[part]
                        except (KeyError, IndexError, TypeError):
                            val = None
                        
                        if isinstance(val, str) and REF_PATTERN.match(val):
                            continue
                        
                        # Otherwise it's a real schema violation (e.g. missing field)
                        real_errors.append(error)
                    
                    if real_errors:
                        self.diagnostics.add(validator_error(
                            ErrorCode.E0361,
                            entity=entity.id or 'anonymous',
                            details=str(e),
                            location=entity.location
                        ))
                    else:
                        total_checked += 1

        self.console.print(f"    [green]✓[/green] Checked schema for {total_checked} entities.")

    def check_structure_only(self, documents: Dict[Path, Document], symbol_table: SymbolTable, model_registry: Dict[str, Any]):
        """
        Stage 2: Structure Check - Pydantic instantiation only, skipping validators.
        
        This is faster than check_schema as it avoids running field/model validators.
        """
        from pydantic import ValidationError
        
        total_checked = 0
        for doc in documents.values():
            for entity in doc.entities:
                model_cls = self._resolve_model_class(entity, symbol_table, model_registry)
                
                if not model_cls:
                    continue
                
                from typedown.core.parser.desugar import Desugarer
                
                # Pre-process: Desugar YAML artifacts
                data = Desugarer.desugar(entity.raw_data)
                
                # Auto-inject ID from Signature if missing in Body
                if "id" not in data and entity.id:
                    data["id"] = entity.id
                
                try:
                    # Use model_construct to skip validation, only check structure
                    # Note: model_construct requires all required fields
                    # If validation fails due to missing fields, we fall back to normal instantiation
                    try:
                        instance = model_cls.model_construct(**data)
                    except (TypeError, ValueError):
                        # model_construct failed (e.g., missing required fields)
                        # Fall back to normal instantiation but ignore validation errors
                        instance = model_cls(**data)
                    
                    # Store instance for later use
                    entity.resolved_data = instance
                    total_checked += 1
                    
                except ValidationError:
                    # Structure-level errors only (missing required fields)
                    # Ignore type validation errors for references
                    pass
                except Exception as e:
                    # Other errors during instantiation
                    self.diagnostics.add(validator_error(
                        ErrorCode.E0361,
                        entity=entity.id or 'anonymous',
                        details=f"Structure error: {str(e)}",
                        location=entity.location
                    ))

    def run_validators_only(self, documents: Dict[Path, Document], symbol_table: SymbolTable, model_registry: Dict[str, Any]):
        """
        Stage 3: Run Pydantic validators on already-instantiated entities.
        
        Assumes entities have been instantiated via check_structure_only.
        """
        from pydantic import ValidationError
        
        total_validated = 0
        for doc in documents.values():
            for entity in doc.entities:
                model_cls = self._resolve_model_class(entity, symbol_table, model_registry)
                
                if not model_cls:
                    continue
                
                from typedown.core.parser.desugar import Desugarer
                
                # Re-instantiate to trigger validators
                data = Desugarer.desugar(entity.raw_data)
                
                if "id" not in data and entity.id:
                    data["id"] = entity.id
                
                try:
                    model_cls(**data)
                    total_validated += 1
                except ValidationError as e:
                    # Filter out reference-related errors
                    real_errors = []
                    for error in e.errors():
                        loc = error['loc']
                        val = data
                        try:
                            for part in loc:
                                val = val[part]
                        except (KeyError, IndexError, TypeError):
                            val = None
                        
                        if isinstance(val, str) and REF_PATTERN.match(val):
                            continue
                        
                        real_errors.append(error)
                    
                    if real_errors:
                        self.diagnostics.add(validator_error(
                            ErrorCode.E0361,
                            entity=entity.id or 'anonymous',
                            details=str(e),
                            location=entity.location
                        ))

    def _resolve_entity(self, entity: EntityBlock, symbol_table: SymbolTable, model_registry: Dict[str, Any]):
        from typedown.core.parser.desugar import Desugarer
        
        # Start resolution from raw data
        # Desugar standard YAML artifacts like [['ref']] back to "[[ref]]"
        current_data = Desugarer.desugar(entity.raw_data)

        # Determine context path for Triple Resolution / Evolution
        context_path = Path(entity.location.file_path) if entity.location else None

        # Handle Evolution (former only)
        # derived_from is explicitly disabled for now.
        if "former" in current_data:
            former_val = current_data["former"]
            # Must extract ID from [[...]] reference
            target_id_str = former_val
            match = REF_PATTERN.match(former_val)
            if match:
                target_id_str = match.group(1)

            # Enforce Global Addressing (L0/L2/L3) -> REMOVED
            # Philosophy Shift: "We cannot judge validity from format alone. Only resolution failure counts."
            # identifier = Identifier.parse(target_id_str)
            # if not identifier.is_global(): ...


            if hasattr(symbol_table, "resolve"):
                parent_node = symbol_table.resolve(target_id_str, context_path=context_path)
            else:
                parent_node = symbol_table.get(target_id_str)
            
            if isinstance(parent_node, EntityBlock):
                # Pure Pointer Logic:
                # We validate that the former entity exists and is resolved.
                # But we do NOT merge its data.
                # 'former' remains a metadata link.
                pass
            else:
                # Resolution Failed
                self.diagnostics.add(validator_error(
                    ErrorCode.E0343,
                    target=target_id_str,
                    location=entity.location
                ))

        try:
            # In-place reference resolution
            engine = QueryEngine(symbol_table)
            resolved = engine.evaluate_data(current_data, context_path=context_path)
            entity.resolved_data = resolved
            
            # 4. Semantic Type Check (Ref[T])
            self._check_semantic_types(entity, symbol_table, model_registry)
            
        except (QueryError, ReferenceError) as e:
            err = validator_error(
                ErrorCode.E0341,
                details=str(e),
                location=entity.location
            )
            self.diagnostics.add(err)
            # FALLBACK: Preserve data to avoid total loss
            entity.resolved_data = current_data

    def _check_semantic_types(self, entity: EntityBlock, symbol_table: SymbolTable, model_registry: Dict[str, Any]):
        """
        Validate that Ref[T] fields actually point to entities of type T.
        """
        model_cls = self._resolve_model_class(entity, symbol_table, model_registry)
        if not model_cls:
            return
        
        for field_name, field_info in model_cls.model_fields.items():
            if field_name not in entity.resolved_data:
                continue
                
            value = entity.resolved_data[field_name]
            if not value: 
                continue

            self._check_field_annotation(field_name, field_info.annotation, value, entity, symbol_table)

    def _check_field_annotation(self, field_name: str, annotation: Any, value: Any, entity: EntityBlock, symbol_table: SymbolTable):
        # Ref[T] is Annotated[str, ReferenceMeta(T)]
        if get_origin(annotation) is Annotated:
            args = get_args(annotation)
            for meta in args[1:]:
                if isinstance(meta, ReferenceMeta):
                    target_type = meta.target_type
                    if isinstance(value, str):
                        target_entity = symbol_table.get(value)
                        if target_entity and hasattr(target_entity, 'class_name') and target_entity.class_name != target_type:
                            self.diagnostics.add(validator_error(
                                ErrorCode.E0362,
                                field=field_name,
                                expected=target_type,
                                value=value,
                                actual=target_entity.class_name,
                                location=entity.location
                            ))
        
        # Recursion for Lists
        origin = get_origin(annotation)
        if origin is list or origin is List:
            arg = get_args(annotation)[0]
            if isinstance(value, list):
                for item in value:
                    self._check_field_annotation(field_name, arg, item, entity, symbol_table)

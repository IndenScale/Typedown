from typing import Dict, Any, List, Set, get_origin, get_args, Annotated
from pathlib import Path
from rich.console import Console

from typedown.core.ast import Document, EntityBlock, SourceLocation
from typedown.core.base.errors import TypedownError, CycleError, ReferenceError
from typedown.core.graph import DependencyGraph
from typedown.core.analysis.query import QueryEngine, QueryError, REF_PATTERN
from typedown.core.base.types import ReferenceMeta
from typedown.core.base.identifiers import Identifier

class Validator:
    def __init__(self, console: Console):
        self.console = console
        self.diagnostics: List[TypedownError] = []
        self.dependency_graph: DependencyGraph = DependencyGraph()

    def validate(self, documents: Dict[Path, Document], symbol_table: Any, model_registry: Dict[str, Any]):
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
            
            self.diagnostics.append(e)
            return

        # 3. Resolve in order
        total_resolved = 0
        for node_id in order:
            if node_id in entities_by_id:
                entity = entities_by_id[node_id]
                self._resolve_entity(entity, symbol_table, model_registry)
                total_resolved += 1
        
        self.console.print(f"    [green]✓[/green] Resolved references for {total_resolved} entities.")

    def check_schema(self, documents: Dict[Path, Document], model_registry: Dict[str, Any]):
        """
        L2: Schema Compliance Check. 
        Validates structure without resolving the graph.
        """
        self.console.print("  [dim]Stage 2.5: Running L2 Schema Check (Pydantic)...[/dim]")
        from pydantic import ValidationError
        
        total_checked = 0
        for doc in documents.values():
            for entity in doc.entities:
                if entity.class_name not in model_registry:
                    # Missing model is handled by Linker usually, but we can log error here too if helpful
                    continue
                
                from typedown.core.parser.desugar import Desugarer
                
                model_cls = model_registry[entity.class_name]
                
                # Pre-process: Desugar YAML artifacts (e.g. [['ref']] -> "[[ref]]")
                data = Desugarer.desugar(entity.raw_data)
                
                # Auto-inject ID from Signature if missing in Body (Signature as Identity)
                if "id" in data:
                    self.diagnostics.append(TypedownError(
                        "Conflict: System ID must be defined in Block Signature, not in Body.",
                        location=entity.location,
                        severity="error"
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
                         self.diagnostics.append(TypedownError(
                             f"Schema Violation in {entity.id or 'anonymous'}: {e}", 
                             location=entity.location,
                             severity="warning"
                         ))
                    else:
                        total_checked += 1

        self.console.print(f"    [green]✓[/green] Checked schema for {total_checked} entities.")

    def _resolve_entity(self, entity: EntityBlock, symbol_table: Dict[str, EntityBlock], model_registry: Dict[str, Any]):
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
                self.diagnostics.append(TypedownError(
                    f"Evolution Error: 'former' target '{target_id_str}' not found.",
                    location=entity.location,
                    severity="error"
                ))

        try:
            # In-place reference resolution
            resolved = QueryEngine.evaluate_data(current_data, symbol_table, context_path=context_path)
            entity.resolved_data = resolved
            
            # 4. Semantic Type Check (Ref[T])
            self._check_semantic_types(entity, symbol_table, model_registry)
            
        except (QueryError, ReferenceError) as e:
            err = ReferenceError(str(e), location=entity.location)
            self.diagnostics.append(err)

    def _check_semantic_types(self, entity: EntityBlock, symbol_table: Dict[str, EntityBlock], model_registry: Dict[str, Any]):
        """
        Validate that Ref[T] fields actually point to entities of type T.
        """
        if entity.class_name not in model_registry:
            return

        model_cls = model_registry[entity.class_name]
        
        for field_name, field_info in model_cls.model_fields.items():
            if field_name not in entity.resolved_data:
                continue
                
            value = entity.resolved_data[field_name]
            if not value: 
                continue

            self._check_field_annotation(field_name, field_info.annotation, value, entity, symbol_table)

    def _check_field_annotation(self, field_name: str, annotation: Any, value: Any, entity: EntityBlock, symbol_table: Dict[str, EntityBlock]):
        # Ref[T] is Annotated[str, ReferenceMeta(T)]
        if get_origin(annotation) is Annotated:
            args = get_args(annotation)
            for meta in args[1:]:
                if isinstance(meta, ReferenceMeta):
                    target_type = meta.target_type
                    if isinstance(value, str):
                        target_entity = symbol_table.get(value)
                        if target_entity and hasattr(target_entity, 'class_name') and target_entity.class_name != target_type:
                            self.diagnostics.append(TypedownError(
                                f"Type Mismatch: Field '{field_name}' expects Ref[{target_type}], but '{value}' is type '{target_entity.class_name}'",
                                location=entity.location,
                                severity="error"
                            ))
        
        # Recursion for Lists
        origin = get_origin(annotation)
        if origin is list or origin is List:
            arg = get_args(annotation)[0]
            if isinstance(value, list):
                for item in value:
                    self._check_field_annotation(field_name, arg, item, entity, symbol_table)



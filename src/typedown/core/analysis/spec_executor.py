"""
Spec Executor: Implements @target selector binding and spec execution.

This module enables Typedown's "self-validation" capability by:
1. Parsing @target decorators to identify which entities a spec applies to
2. Automatically injecting matching entities as the 'subject' parameter
3. Executing spec blocks against their targets
"""

import re
import ast
import sys
import types
import tempfile
import pytest
import contextvars
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from rich.console import Console

from typedown.core.ast import Document, SpecBlock, EntityBlock
from typedown.core.base.errors import TypedownError
from typedown.core.base.utils import AttributeWrapper
from typedown.core.analysis.query import QueryEngine
from typedown.core.base.symbol_table import SymbolTable

# ContextVar to track the current test ID safely across async/threaded contexts
current_test_id_var = contextvars.ContextVar("current_test_id", default=None)


class TargetSelector:
    """
    Parses and evaluates @target decorator expressions.
    
    Supported syntax:
    - @target(type="UserAccount")  # Match by entity type
    - @target(type="Item", scope="global") # Match globally (run once)
    - @target(tag="critical")       # Match by entity tag (future)
    - @target(id="users/alice")     # Match specific entity (future)
    """
    
    def __init__(self, decorator_str: str):
        self.raw = decorator_str
        self.type_filter: Optional[str] = None
        self.tag_filter: Optional[str] = None
        self.id_filter: Optional[str] = None
        self.scope: str = "local"  # local (default) | global
        
        self._parse()
    
    def _parse(self):
        """Parse @target(...) decorator string."""
        # Pattern: @target(key="value", ...)
        pattern = r'@target\((.*?)\)'
        match = re.search(pattern, self.raw)
        
        if not match:
            return
        
        args_str = match.group(1)
        
        # Parse key="value" pairs
        for pair in args_str.split(','):
            pair = pair.strip()
            if '=' in pair:
                key, value = pair.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                if key == 'type':
                    self.type_filter = value
                elif key == 'tag':
                    self.tag_filter = value
                elif key == 'id':
                    self.id_filter = value
                elif key == 'scope':
                    self.scope = value.lower()
    
    def matches(self, entity: EntityBlock) -> bool:
        """Check if an entity matches this selector."""
        if self.type_filter:
            # Handle potential module prefixes or exact match
            # entity.class_name might be "Item", "models.rpg.Item"
            # self.type_filter might be "Item"
            
            e_type = entity.class_name
            t_filter = self.type_filter
            
            # Simple suffix match if filter doesn't contain dots
            if '.' not in t_filter and '.' in e_type:
                match = e_type.endswith(f".{t_filter}") or e_type == t_filter
            else:
                match = e_type == t_filter
                
            if not match:
                return False
        
        if self.id_filter:
            if entity.id != self.id_filter:
                return False
        
        # Tag filtering would require entity tags (future enhancement)
        if self.tag_filter:
            # For now, skip tag filtering
            pass
        
        return True


class DiagnosticCollector:
    """Pytest plugin to capture results and map them to Typedown errors."""
    def __init__(self, mapping: Dict[str, Tuple[SpecBlock, EntityBlock]]):
        self.mapping = mapping
        self.failures = []

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == 'call' and report.failed:
            # nodeid looks like: test_session.py::test_spec_123_alice
            test_id = item.nodeid.split("::")[-1]
            if test_id in self.mapping:
                spec, entity = self.mapping[test_id]
                msg = str(call.excinfo.value)
                
                # Enhance error message for missing attributes (AttributeWrapper)
                if "'AttributeWrapper' object has no attribute" in msg:
                    match = re.search(r"attribute '([^']+)'", msg)
                    if match:
                        attr_name = match.group(1)
                        msg = f"Spec Error: Entity '{entity.id}' is missing required field '{attr_name}' (accessed via subject.{attr_name})"

                # Capture the full pytest failure representation (assertion diffs etc)
                longrepr = str(report.longrepr)
                self.failures.append({
                    "spec": spec,
                    "entity": entity,
                    "message": msg,
                    "detail": longrepr,
                    "test_id": test_id
                })

class BlameRegistry:
    """Stores explicit blame calls from specs."""
    def __init__(self):
        # Mapping: test_id -> List[{entity_id, reason}]
        self.records: Dict[str, List[Dict[str, str]]] = {}

    def blame(self, target: Any, reason: str):
        test_id = current_test_id_var.get()
        if not test_id:
            return
            
        entity_id = None
        if hasattr(target, "_entity_id"):
            entity_id = target._entity_id
        elif isinstance(target, str):
            entity_id = target
            
        if entity_id:
            if test_id not in self.records:
                self.records[test_id] = []
            self.records[test_id].append({
                "entity_id": entity_id,
                "reason": reason
            })

class SpecExecutor:
    """
    Executes spec blocks with @target selector binding using Pytest as the engine.
    """
    
    def __init__(self, console: Console):
        self.console = console
        self.diagnostics: List[TypedownError] = []
    
    def execute_specs(
        self, 
        documents: Dict[Path, Document],
        symbol_table: SymbolTable,
        model_registry: Dict[str, Any],
        project_root: Optional[Path] = None,
        spec_filter: Optional[str] = None
    ) -> bool:
        self.console.print("  [dim]L3: Executing Specs (Pytest Driven)...[/dim]")
        
        # Report Statistics
        spec_count = sum(len(d.specs) for d in documents.values())
        doc_count = len(documents)
        entity_count = len(symbol_table.values())
        self.console.print(f"    [dim]ℹ Statistics: Found {spec_count} spec blocks across {doc_count} files. Symbol Table: {entity_count} entities.[/dim]")

        # 1. Collect all test tasks
        if spec_filter:
            self.console.print(f"    [dim]Filter Active: '{spec_filter}'[/dim]")

        tasks: List[Tuple[SpecBlock, EntityBlock]] = []
        for doc in documents.values():
            for spec in doc.specs:
                if spec_filter and spec.id != spec_filter:
                    self.console.print(f"    [dim]Skip '{spec.id}' != '{spec_filter}'[/dim]")
                    self.console.print(f"    [dim]Debug Repr: {repr(spec.id)} vs {repr(spec_filter)}[/dim]")
                    continue

                selector = self._extract_selector(spec)
                # self.console.print(f"[dim]Debug: Spec {spec.id}: selector={selector}[/dim]")
                
                if not selector:
                    self.console.print(f"    [yellow]⚠[/yellow] Spec '{spec.id or spec.name}' has no @target decorator. Skipping.")
                    continue

                matches = self._find_matching_entities(selector, symbol_table)
                if not matches:
                    # Debug Info
                    self.console.print(f"[dim]Debug: Selector type={selector.type_filter}, raw={selector.raw}[/dim]")
                    for node in symbol_table.values():
                        if isinstance(node, EntityBlock):
                            # Handle case where class_name might be missing or None
                            class_name_str = node.class_name if hasattr(node, "class_name") else "unknown"
                            self.console.print(f"[dim] - Entity: {class_name_str} ({node.id})[/dim]")
                    
                    self.console.print(f"    [yellow]⚠[/yellow] Spec '{spec.id or spec.name}' has no matching entities for selector: {selector.raw}")
                    continue

                # Handle scope="global": Run ONCE with the first entity as representative
                if selector.scope == "global":
                    # Use the first match as representative subject
                    representative = matches[0]
                    tasks.append((spec, representative))
                else:
                    # Default: Run for ALL matches
                    for entity in matches:
                        tasks.append((spec, entity))
        
        if not tasks:
            self.console.print("    [dim]ℹ[/dim] No matching spec/entity pairs found in the project.")
            return True

        # 2. Setup Runtime Context (Module Bridge)
        ctx_name = "typedown_context"
        ctx = types.ModuleType(ctx_name)
        setattr(ctx, "AttributeWrapper", AttributeWrapper)
        setattr(ctx, "models", model_registry)
        setattr(ctx, "subjects", {id(entity): entity.resolved_data for _, entity in tasks})
        
        # Inject Query Function
        def query_wrapper(query_str: str) -> Any:
            results = QueryEngine.resolve_query(
                query_str, 
                symbol_table, 
                root_dir=project_root
            )
            wrapped_results = []
            for res in results:
                if isinstance(res, EntityBlock):
                    wrapped_results.append(AttributeWrapper(res.resolved_data, entity_id=res.id))
                elif isinstance(res, dict):
                    wrapped_results.append(AttributeWrapper(res))
                else:
                    wrapped_results.append(res)
            
            # Auto-unwrap single result for convenience
            if len(wrapped_results) == 1:
                return wrapped_results[0]
            return wrapped_results

        setattr(ctx, "query", query_wrapper)

        # Inject SQL Function
        def sql_wrapper(query_str: str) -> Any:
            # symbol_table is expected to be SymbolTable instance with get_duckdb_connection
            results = QueryEngine.execute_sql(query_str, symbol_table)
            # Wrap results for dot notation access, preserving _id for blame()
            return [AttributeWrapper(row, entity_id=row.get("_id")) for row in results]

        setattr(ctx, "sql", sql_wrapper)

        # Inject Blame API
        blame_registry = BlameRegistry()
        setattr(ctx, "blame_registry", blame_registry)
        setattr(ctx, "blame", blame_registry.blame)
        setattr(ctx, "current_test_id_var", current_test_id_var)
        
        sys.modules[ctx_name] = ctx
        
        # 3. Generate Test File
        mapping = {} 
        test_id_tracker = []
        test_file_content = [
            "import pytest",
            f"from {ctx_name} import models, subjects, AttributeWrapper, query, sql, blame, blame_registry, current_test_id_var",
            "",
            "# Setup test hooks to track current test_id for blame attribution",
            "@pytest.fixture(autouse=True)",
            "def track_test_id(request):",
            "    token = current_test_id_var.set(request.node.name)",
            "    yield",
            "    current_test_id_var.reset(token)",
            "",
            "# Inject models into global scope",
            "globals().update(models)",
            "# Inject query into global scope",
            "globals()['query'] = query",
            "# Inject sql into global scope",
            "globals()['sql'] = sql",
            "# Inject blame into global scope",
            "globals()['blame'] = blame",
            "",
            "# Dummy target decorator",
            "# (we also replace it in code, but good as fallback)",
            "def target(**kwargs): return lambda f: f",
            ""
        ]
        
        for idx, (spec, entity) in enumerate(tasks):
            s_id = spec.id or f"anon_spec_{idx}"
            e_id = entity.id or f"anon_entity_{idx}"
            test_id = f"test_{s_id.replace('-', '_')}_{e_id.replace('-', '_')}_{idx}"
            mapping[test_id] = (spec, entity)
            
            # Clean spec code (remove @target)
            code_lines = spec.code.split('\n')
            filtered_lines = [line for line in code_lines if not line.strip().startswith('@target')]
            clean_code = '\n'.join(filtered_lines)
            
            # Find the function name defined in the spec
            # Find the SPECIFIC function name defined in the spec matching the ID (Guaranteed by Parser)
            # We strictly look for def <spec.id>(
            func_name = spec.id
            
            # double check existence (Parser ensures this, but safe to check)
            if re.search(rf'def\s+{func_name}\s*\(', clean_code):
                unique_spec_func = f"spec_impl_{idx}"
                # Replace ONLY the specific definition
                clean_code = re.sub(rf'def\s+{func_name}\s*\(', f'def {unique_spec_func}(', clean_code, count=1)
                
                test_file_content.append(f"# Spec Architecture: {spec.id}")
                test_file_content.append(clean_code)
                test_file_content.append(f"def {test_id}():")
                test_file_content.append(f"    subject = AttributeWrapper(subjects[{id(entity)}], entity_id='{entity.id}')")
                test_file_content.append(f"    {unique_spec_func}(subject)")
                test_file_content.append("")
            else:
                 self.console.print(f"    [red]⚠[/red] Spec '{spec.id}' code mismatch. Could not find 'def {func_name}(' despite parser validation.")
                 continue

        # 4. Execute Pytest
        collector = DiagnosticCollector(mapping)
        
        with tempfile.NamedTemporaryFile(suffix="_test.py", mode="w", delete=False) as f:
            f.write("\n".join(test_file_content))
            test_file_path = f.name
            
        try:
            # Patch sys.stderr AND sys.stdout to avoid AttributeError in LSP environment
            # Pytest TerminalReporter uses sys.stdout by default, but checks isatty
            original_stderr = sys.stderr
            original_stdout = sys.stdout
            
            patched_streams = []

            for stream in [original_stderr, original_stdout]:
                if stream and not hasattr(stream, 'isatty'):
                    try:
                        setattr(stream, 'isatty', lambda: False)
                        patched_streams.append(stream)
                    except AttributeError:
                        pass
                    
            try:
                ret = pytest.main(
                    [test_file_path, "-q", "--tb=short", "-p", "no:cacheprovider", "--color=no"],
                    plugins=[collector]
                )
            finally:
                # Cleanup patch
                for stream in patched_streams:
                    if hasattr(stream, 'isatty') and getattr(stream, 'isatty').__name__ == '<lambda>':
                         try:
                             delattr(stream, 'isatty')
                         except AttributeError:
                             pass
            
            # 5. Process Results
            for fail in collector.failures:
                spec = fail["spec"]
                default_entity = fail["entity"]
                reason = fail["message"]
                test_id = fail["test_id"]
                
                # Check for explicit blame
                blamed_records = blame_registry.records.get(test_id, [])
                
                # 1. Spec-side diagnostic (Rule perspective)
                # Always show the error on the spec itself
                self.diagnostics.append(TypedownError(
                    f"Spec '{spec.id}' failed: {reason}",
                    location=spec.location,
                    severity="error"
                ))
                
                if blamed_records:
                    # Explicit blame: only highlight blamed entities
                    for record in blamed_records:
                        target_id = record["entity_id"]
                        blame_reason = record["reason"]
                        
                        # Find the entity object for location
                        target_entity = symbol_table.get(target_id)
                        if target_entity and target_entity.location:
                            self.diagnostics.append(TypedownError(
                                f"Violates spec '{spec.id}': {blame_reason}",
                                location=target_entity.location,
                                severity="error"
                            ))
                        else:
                            # Fallback if entity not found in symbol table (might be dynamic)
                            self.console.print(f"    [yellow]⚠[/yellow] Blamed entity '{target_id}' not found in symbol table.")
                else:
                    # No explicit blame: broadcast to default subject (legacy behavior)
                    if default_entity.location:
                         self.diagnostics.append(TypedownError(
                            f"Violates spec '{spec.id}': {reason}",
                            location=default_entity.location,
                            severity="error"
                        ))

                self.console.print(
                    f"    [red]✗[/red] Spec '{spec.id}' failed (attributed to {len(blamed_records) or 1} entities): {reason}"
                )

            if ret == 0:
                self.console.print(
                    f"    [green]✓[/green] All specs passed ({len(tasks)} tests)."
                )
                return True
            else:
                self.console.print(
                    f"    [red]✗[/red] {len(collector.failures)} tests failed."
                )
                return False
                
        finally:
            if Path(test_file_path).exists():
                Path(test_file_path).unlink()
            if ctx_name in sys.modules:
                del sys.modules[ctx_name]

    def _extract_selector(self, spec: SpecBlock) -> Optional[TargetSelector]:
        """Extract @target decorator from spec code."""
        target_pattern = r'@target\([^)]+\)'
        match = re.search(target_pattern, spec.code)
        
        if match:
            return TargetSelector(match.group(0))
        
        return None
    
    def _find_matching_entities(
        self, 
        selector: TargetSelector,
        symbol_table: SymbolTable
    ) -> List[EntityBlock]:
        """Find all entities matching the selector."""
        matches = []
        nodes = symbol_table.values() if hasattr(symbol_table, 'values') else symbol_table
        
        for node in nodes:
            if isinstance(node, EntityBlock):
                if selector.matches(node):
                    matches.append(node)
        
        return matches



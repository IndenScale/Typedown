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
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from rich.console import Console

from typedown.core.ast import Document, SpecBlock, EntityBlock
from typedown.core.base.errors import TypedownError
from typedown.core.base.utils import AttributeWrapper


class TargetSelector:
    """
    Parses and evaluates @target decorator expressions.
    
    Supported syntax:
    - @target(type="UserAccount")  # Match by entity type
    - @target(tag="critical")       # Match by entity tag (future)
    - @target(id="users/alice")     # Match specific entity (future)
    """
    
    def __init__(self, decorator_str: str):
        self.raw = decorator_str
        self.type_filter: Optional[str] = None
        self.tag_filter: Optional[str] = None
        self.id_filter: Optional[str] = None
        
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
    
    def matches(self, entity: EntityBlock) -> bool:
        """Check if an entity matches this selector."""
        if self.type_filter:
            if entity.class_name != self.type_filter:
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
                # Capture the full pytest failure representation (assertion diffs etc)
                longrepr = str(report.longrepr)
                self.failures.append({
                    "spec": spec,
                    "entity": entity,
                    "message": msg,
                    "detail": longrepr
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
        symbol_table: Dict[str, EntityBlock],
        model_registry: Dict[str, Any]
    ) -> bool:
        self.console.print("  [dim]L4: Executing Specs (Pytest Driven)...[/dim]")
        
        # 1. Collect all test tasks
        tasks: List[Tuple[SpecBlock, EntityBlock]] = []
        for doc in documents.values():
            for spec in doc.specs:
                selector = self._extract_selector(spec)
                if not selector:
                    if self._is_legacy_yaml_spec(spec):
                         # Legacy YAML specs are skipped without warning
                         pass
                    else:
                        self.console.print(f"    [yellow]⚠[/yellow] Spec '{spec.id or spec.name}' has no @target decorator. Skipping.")
                    continue

                matches = self._find_matching_entities(selector, symbol_table)
                if not matches:
                    self.console.print(f"    [yellow]⚠[/yellow] Spec '{spec.id or spec.name}' has no matching entities for selector: {selector.raw}")
                    continue

                    
                for entity in matches:
                    tasks.append((spec, entity))
        
        if not tasks:
            self.console.print("    [dim]ℹ[/dim] No matching spec/entity pairs found in the project.")
            return True

        # 2. Setup Runtime Context (Module Bridge)
        ctx_name = "typedown_context"
        ctx = types.ModuleType(ctx_name)
        ctx.AttributeWrapper = AttributeWrapper
        ctx.models = model_registry
        ctx.subjects = {id(entity): entity.resolved_data for _, entity in tasks}
        
        sys.modules[ctx_name] = ctx
        
        # 3. Generate Test File
        mapping = {} 
        test_file_content = [
            "import pytest",
            f"from {ctx_name} import models, subjects, AttributeWrapper",
            "",
            "# Inject models into global scope",
            "globals().update(models)",
            "",
            "# Dummy target decorator",
            "# (we also replace it in code, but good as fallback)",
            "def target(**kwargs): return lambda f: f",
            ""
        ]
        
        for idx, (spec, entity) in enumerate(tasks):
            test_id = f"test_{spec.id.replace('-', '_')}_{entity.id.replace('-', '_')}_{idx}"
            mapping[test_id] = (spec, entity)
            
            # Clean spec code (remove @target)
            code_lines = spec.code.split('\n')
            filtered_lines = [line for line in code_lines if not line.strip().startswith('@target')]
            clean_code = '\n'.join(filtered_lines)
            
            # Find the function name defined in the spec
            match = re.search(r'def\s+(\w+)\s*\(', clean_code)
            func_name = match.group(1) if match else None
            
            if func_name:
                unique_spec_func = f"spec_impl_{idx}"
                # Replace ONLY the definition to avoid collisions at module level
                clean_code = re.sub(rf'def\s+{func_name}\s*\(', f'def {unique_spec_func}(', clean_code, count=1)
                
                test_file_content.append(f"# Spec Architecture: {spec.id}")
                test_file_content.append(clean_code)
                test_file_content.append(f"def {test_id}():")
                test_file_content.append(f"    subject = AttributeWrapper(subjects[{id(entity)}])")
                test_file_content.append(f"    {unique_spec_func}(subject)")
                test_file_content.append("")

        # 4. Execute Pytest
        collector = DiagnosticCollector(mapping)
        
        with tempfile.NamedTemporaryFile(suffix="_test.py", mode="w", delete=False) as f:
            f.write("\n".join(test_file_content))
            test_file_path = f.name
            
        try:
            ret = pytest.main(
                [test_file_path, "-q", "--tb=short", "-p", "no:cacheprovider"],
                plugins=[collector]
            )
            
            # 5. Process Results
            for fail in collector.failures:
                spec = fail["spec"]
                entity = fail["entity"]
                reason = fail["message"]
                
                self.diagnostics.append(TypedownError(
                    f"Spec '{spec.id}' failed for entity '{entity.id}': {reason}",
                    location=spec.location,
                    severity="error"
                ))
                self.console.print(
                    f"    [red]✗[/red] Spec '{spec.id}' failed for entity '{entity.id}': {reason}"
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
        symbol_table: Any
    ) -> List[EntityBlock]:
        """Find all entities matching the selector."""
        matches = []
        nodes = symbol_table.values() if hasattr(symbol_table, 'values') else symbol_table
        
        for node in nodes:
            if isinstance(node, EntityBlock):
                if selector.matches(node):
                    matches.append(node)
        
        return matches

    def _is_legacy_yaml_spec(self, spec: SpecBlock) -> bool:
        """Heuristic to check if a spec is a legacy YAML definition."""
        # Check for typical YAML fields in the spec code
        # Older specs (spec:Rule) defined 'target:' and 'check:' in YAML
        code_strip = spec.code.strip()
        lines = code_strip.splitlines()
        has_target_field = any(line.strip().startswith("target:") for line in lines)
        has_check_field = any(line.strip().startswith("check:") for line in lines)
        
        return has_target_field or has_check_field

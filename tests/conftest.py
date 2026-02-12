"""
Pytest configuration and shared fixtures for aligned test suite.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console

from typedown.core.parser import TypedownParser
from typedown.core.analysis import Scanner, Linker, Validator
from typedown.core.analysis.spec_executor import SpecExecutor
from typedown.core.base.config import TypedownConfig
from typedown.core.base.errors import ErrorCode, DiagnosticReport


class TestProjectBuilder:
    """Helper to build temporary Typedown projects for testing."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="typedown_test_"))
        self.files: Dict[Path, str] = {}
    
    def add_file(self, path: str, content: str) -> "TestProjectBuilder":
        """Add a file to the test project."""
        file_path = self.temp_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        self.files[file_path] = content
        return self
    
    def add_config(self, content: str = "") -> "TestProjectBuilder":
        """Add a config.td file."""
        default = '''---
title: Test Config
---

```config python
# Default test config
```
'''
        return self.add_file("config.td", content or default)
    
    def add_model(self, name: str, class_def: str) -> "TestProjectBuilder":
        """Add a model definition file."""
        content = f'''---
title: Model {name}
---

```model:{name}
{class_def}
```
'''
        return self.add_file(f"models/{name.lower()}.td", content)
    
    def add_entity(self, type_name: str, entity_id: str, data: Dict[str, Any]) -> "TestProjectBuilder":
        """Add an entity definition file."""
        import yaml
        yaml_data = yaml.dump(data, allow_unicode=True, sort_keys=False)
        content = f'''---
title: Entity {entity_id}
---

```entity {type_name}: {entity_id}
{yaml_data}
```
'''
        return self.add_file(f"entities/{entity_id}.td", content)
    
    def add_spec(self, spec_id: str, target: str, code: str, scope: str = "local") -> "TestProjectBuilder":
        """Add a spec definition file."""
        content = f'''---
title: Spec {spec_id}
---

```spec:{spec_id}
@target(type="{target}", scope="{scope}")
def {spec_id}(subject):
{code}
```
'''
        return self.add_file(f"specs/{spec_id}.td", content)
    
    def get_path(self) -> Path:
        """Get the temporary project path."""
        return self.temp_dir
    
    def compile(self) -> tuple[DiagnosticReport, DiagnosticReport, DiagnosticReport]:
        """Run full compilation and return diagnostics from each stage."""
        console = Console(quiet=True)
        config = TypedownConfig()
        
        # Stage 1: Scan
        scanner = Scanner(self.temp_dir, console)
        documents, target_files = scanner.scan(self.temp_dir)
        scanner.lint(documents)
        
        # Stage 2: Link
        linker = Linker(self.temp_dir, config, console)
        linker.link(documents)
        
        # Stage 3: Validate
        validator = Validator(console)
        validator.check_schema(documents, linker.symbol_table, linker.model_registry)
        validator.validate(documents, linker.symbol_table, linker.model_registry)
        
        return scanner.diagnostics, linker.diagnostics, validator.diagnostics
    
    def cleanup(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


@pytest.fixture
def project():
    """Fixture providing a TestProjectBuilder."""
    builder = TestProjectBuilder()
    yield builder
    builder.cleanup()


@pytest.fixture
def parser():
    """Fixture providing a TypedownParser."""
    return TypedownParser()


@pytest.fixture
def console():
    """Fixture providing a quiet console for testing."""
    return Console(quiet=True)


def assert_error_exists(diagnostics: DiagnosticReport, code: ErrorCode, message_contains: Optional[str] = None):
    """Assert that a specific error code exists in diagnostics."""
    matching = [e for e in diagnostics.errors if e.code == code]
    assert len(matching) > 0, f"Expected error {code} not found. Got: {[e.code for e in diagnostics.errors]}"
    
    if message_contains:
        found = any(message_contains.lower() in e.message.lower() for e in matching)
        assert found, f"Error {code} found but message doesn't contain '{message_contains}'. Messages: {[e.message for e in matching]}"


def assert_no_errors(diagnostics: DiagnosticReport):
    """Assert that no ERROR level diagnostics exist."""
    errors = [e for e in diagnostics.errors if e.level.value == "error"]
    assert len(errors) == 0, f"Expected no errors, got: {[(e.code, e.message) for e in errors]}"


def assert_error_count(diagnostics: DiagnosticReport, code: ErrorCode, expected_count: int):
    """Assert exact count of a specific error code."""
    matching = [e for e in diagnostics.errors if e.code == code]
    assert len(matching) == expected_count, f"Expected {expected_count} occurrences of {code}, got {len(matching)}"


import pytest
from typedown.core.analysis.validator import Validator
from typedown.core.base.symbol_table import SymbolTable
from typedown.core.ast import Document, EntityBlock
from rich.console import Console
from pathlib import Path

def test_circular_reference_allowed():
    """
    Test that A -> B -> A reference cycle is ALLOWED (Late Binding).
    This was previously disallowed by strict topological sort.
    """
    # 1. Setup Data
    # Entity A refers to B
    entity_a = EntityBlock(
        header_type="entity",
        header_args="TypeA: users/a",
        body_lines=[],
        raw_data={"ref_to_b": "[[users/b]]"},
        class_name="TypeA"
    )
    entity_a.id = "users/a"
    
    # Entity B refers to A
    entity_b = EntityBlock(
        header_type="entity", 
        header_args="TypeB: users/b", 
        body_lines=[],
        raw_data={"ref_to_a": "[[users/a]]"},
        class_name="TypeB"
    )
    entity_b.id = "users/b"
    
    doc = Document(path=Path("test.td"))
    doc.entities = [entity_a, entity_b]
    documents = {Path("test.td"): doc}
    
    sym_table = SymbolTable()
    # Adding nodes properly
    sym_table.add(entity_a, scope_path=doc.path)
    sym_table.add(entity_b, scope_path=doc.path)
    
    # 2. Run Validator
    validator = Validator(Console(quiet=True))
    model_registry = {} 
    
    # This should NOT start loop or raise CycleError
    validator.validate(documents, sym_table, model_registry)
    
    # 3. Assertions
    # Should resolve successfully
    assert len(validator.diagnostics) == 0
    assert entity_a.resolved_data is not None
    assert entity_b.resolved_data is not None


def test_former_cycle_disallowed():
    """
    Test that A(former=B) -> B(former=A) IS a cycle error.
    Timeline must be acyclic.
    """
    entity_a = EntityBlock(
        header_type="entity", header_args="TypeA: users/a", body_lines=[],
        raw_data={"former": "[[users/b]]"},
        class_name="TypeA"
    )
    entity_a.id = "users/a"
    entity_a.former_ids = ["[[users/b]]"] 
    
    entity_b = EntityBlock(
        header_type="entity", header_args="TypeB: users/b", body_lines=[],
        raw_data={"former": "[[users/a]]"},
        class_name="TypeB"
    )
    entity_b.id = "users/b"

    entity_b.former_ids = ["[[users/a]]"]
    
    doc = Document(path=Path("test_former.td"))
    doc.entities = [entity_a, entity_b]
    documents = {Path("test_former.td"): doc}
    
    sym_table = SymbolTable()
    sym_table.add(entity_a, scope_path=doc.path)
    sym_table.add(entity_b, scope_path=doc.path)
    
    validator = Validator(Console(quiet=True))
    validator.validate(documents, sym_table, {})
    
    # Should have CycleError
    assert len(validator.diagnostics) > 0
    cycle_error = next((e for e in validator.diagnostics if "Circular dependency" in str(e)), None)
    assert cycle_error is not None

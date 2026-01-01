import pytest
from pathlib import Path
from rich.console import Console
from typedown.core.ast.blocks import EntityBlock
from typedown.core.analysis.validator import Validator

def test_validator_with_sugar():
    console = Console()
    validator = Validator(console)
    
    # Simulate YAML artifact: friend: [['alice']]
    entity = EntityBlock(
        id="bob",
        class_name="User",
        raw_data={"friend": [["alice"]]}
    )
    
    # Needed for resolution
    alice = EntityBlock(id="alice", class_name="User", raw_data={"name": "Alice"})
    symbol_table = {"alice": alice, "bob": entity}
    
    # Model Registry (optional for basic resolution)
    model_registry = {}
    
    # We call _resolve_entity directly for testing
    validator._resolve_entity(entity, symbol_table, model_registry)
    
    # Check if desugared and resolved
    # [['alice']] -> "[[alice]]" -> alice object
    assert entity.resolved_data["friend"] is alice

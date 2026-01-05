import pytest
from pathlib import Path
from typedown.core.ast import EntityBlock, SpecBlock, Document
from typedown.core.analysis.spec_executor import SpecExecutor
from typedown.core.base.symbol_table import SymbolTable
from rich.console import Console

def test_spec_sql_execution():
    console = Console(quiet=True)
    executor = SpecExecutor(console)
    
    # Setup Symbol Table
    user = EntityBlock(
        id="alice",
        class_name="User",
        raw_data={"age": 30},
        resolved_data={"age": 30}
    )
    
    real_st = SymbolTable()
    real_st.add(user, Path("alice.td"))
    
    # Create Spec
    spec_code = """
@target(type="User")
def check_avg_age(user):
    # This runs for every user, but we can aggregate
    # sql() returns list of AttributeWrapper, which behave like dicts but also objects
    users = sql("SELECT * FROM User")
    assert len(users) == 1
    assert users[0].age == 30
    assert users[0]['age'] == 30
"""
    spec = SpecBlock(
        name="check_avg_age",
        code=spec_code,
        target="User"
    )
    spec.id = "check_avg_age" # ID is needed
    
    doc = Document(path=Path("test.td"))
    doc.specs.append(spec)
    # doc.entities.append(user) # Not strictly needed if ST is pre-filled, but good for consistency
    
    passed = executor.execute_specs(
        {Path("test.td"): doc},
        real_st,
        {},
        project_root=Path(".")
    )
    
    # Print diagnostics if failed
    if not passed:
        for d in executor.diagnostics:
            print(d.message)
            
    assert passed

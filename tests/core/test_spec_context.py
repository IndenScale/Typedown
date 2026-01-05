import pytest
from typedown.core.compiler import Compiler
from typedown.core.ast import EntityBlock

def test_spec_query_injection(tmp_path):
    # Setup a minimal project
    (tmp_path / "typedown.toml").write_text('[project]\nname="test-proj"')
    
    # 1. Create a User model
    (tmp_path / "models.td").write_text("""
```model:User
class User(BaseModel):
    name: str
    manager: str
```
    """)
    
    # 2. Create Entities (Alice -> Bob)
    (tmp_path / "users.td").write_text("""
```entity User: alice
name: "Alice"
manager: "bob"
```

```entity User: bob
name: "Bob"
manager: "charlie"
```
    """)

    # 3. Create a Spec using Query to look up manager
    (tmp_path / "specs.td").write_text("""
```spec: check_manager
@target(type="User")
def check_manager(subject):
    # This query uses the injected 'query' function
    # It resolves the manager string (e.g. "bob") to an entity
    if subject.name == "Alice":
        manager = query(subject.manager)
        assert manager is not None
        assert manager.name == "Bob"
```
    """)
    
    compiler = Compiler(tmp_path)
    success = compiler.compile()
    assert success
    
    # Run Spec
    specs_passed = compiler.verify_specs()
    
    # Debug: Print diagnostics if failed
    for d in compiler.diagnostics:
        print(d)
        
    assert specs_passed
    assert len(compiler.diagnostics) == 0

def test_spec_query_complex(tmp_path):
    # Test complex query "User where ..." style? 
    # Currently QueryEngine only supports ID lookup and property access.
    # So we simulate logic that *uses* query.
    
    (tmp_path / "typedown.toml").write_text('[project]\nname="test-proj"')
    (tmp_path / "data.td").write_text("""
```entity Map: config
items: ["a", "b"]
```

```spec: check_config
@target(id="config")
def check_config(subject):
    # Helper function check
    assert len(subject.items) == 2
```
    """)
    
    compiler = Compiler(tmp_path)
    compiler.compile()
    assert compiler.verify_specs()

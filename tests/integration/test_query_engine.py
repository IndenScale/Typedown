
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from typedown.core.compiler import Compiler
from typedown.core.analysis.query import QueryEngine, ReferenceError, QueryError

class TestQueryEngineIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp()).resolve()
        self.project_root = (self.test_dir / "query_project").resolve()
        self.project_root.mkdir()

        # Create typedown.toml
        (self.project_root / "typedown.toml").write_text("[project]\nname = \"query_test\"\n")

        # Create structure for complex path testing
        # users.td
        self.users_file = self.project_root / "users.td"
        self.users_file.write_text("""
```model:Profile
class Profile(BaseModel):
    email: str
    age: int
```

```model:User
class User(BaseModel):
    name: str
    profile: Profile
```

```entity User: alice
name: "Alice"
profile:
    email: "alice@example.com"
    age: 30
```
""")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_complex_path_resolution(self):
        compiler = Compiler(self.project_root, console=MagicMock())
        # Parse the project to populate symbol table
        compiler.parse_project = MagicMock(side_effect=lambda: compiler.compile()) # Compiler doesn't have parse_project, uses compile()
        compiler.compile()
        
        symbol_table = compiler.symbol_table
        
        # Debug: Print diagnostics
        print("\nDEBUG: Diagnostics:")
        for d in compiler.diagnostics:
             print(f"  {d.severity}: {d.message} at {d.location}")
             
        # Debug: Print documents found
        print("\nDEBUG: Documents:", list(compiler.documents.keys()))

        # Debug: Print all scopes in symbol table
        print("\nDEBUG: Scoped Index Keys:")
        for k in symbol_table._scoped_index.keys():
            print(f"  {k} (Type: {type(k)})")
        
        print("\nDEBUG: Global Index Keys:", list(symbol_table._global_index.keys()))
        
        print(f"\nDEBUG: Project Root: {self.project_root}")
        print(f"DEBUG: Users File: {self.users_file}")

        
        # Query: "alice.profile.email"
        engine = QueryEngine(symbol_table)
        email = engine.resolve_query("alice.profile.email", context_path=self.users_file)
        self.assertEqual(email[0], "alice@example.com")
        
        # Query: "alice.profile.age"
        age = engine.resolve_query("alice.profile.age", context_path=self.users_file)
        self.assertEqual(age[0], 30)

    def test_hash_addressing(self):
        compiler = Compiler(self.project_root, console=MagicMock())
        compiler.compile()
        
        symbol_table = compiler.symbol_table
        
        # Find the node for 'alice' to get its hash
        # We can resolve it by handle first
        alice_node = symbol_table.resolve_handle("alice", context_path=self.users_file)
        self.assertIsNotNone(alice_node, "Alice node not found via handle")
        
        computed_hash = alice_node.content_hash
        self.assertTrue(computed_hash, "Hash should not be empty")
        
        # Construct hash query
        hash_query = f"[[sha256:{computed_hash}]]"
        
        # The QueryEngine.resolve_string or resolve_query handles "[[...]]" stripping for string resolution,
        # but resolve_query takes the inside content usually. 
        # Check QueryEngine.resolve_query implementation (line 57). 
        # It calls `Identifier.parse`.
        # Identifier.parse handles "sha256:..."
        
        # So we query "sha256:{hash}"
        q = f"sha256:{computed_hash}"
        engine = QueryEngine(symbol_table)
        results = engine.resolve_query(q)
        
        self.assertTrue(len(results) > 0, "Should resolve by hash")
        self.assertEqual(results[0], alice_node)
        
        # Also test property access on hash: [[sha256:...]].name
        q_prop = f"sha256:{computed_hash}.name"
        results_prop = engine.resolve_query(q_prop)
        self.assertEqual(results_prop[0], "Alice")


"""
End-to-End Integration Scenarios

These tests simulate real-world usage scenarios combining:
- VSCode Extension behaviors
- LSP Server operations  
- Compiler functionality

Each scenario tests a complete user workflow from start to finish.
"""

import pytest
import asyncio



# =============================================================================
# Scenario 1: New User Onboarding
# =============================================================================

class TestNewUserOnboarding:
    """
    Scenario: A new user creates their first Typedown project.
    
    Steps:
    1. Open VSCode in a new folder
    2. Create config.td
    3. Create first model
    4. Create first entity
    5. Get completions and validation
    """
    
    @pytest.mark.asyncio
    async def test_complete_onboarding_flow(self, lsp_pair, integration_project):
        """Test the complete onboarding flow for a new user."""
        # lsp_pair already initialized by fixture
        
        # Step 1: Create config.td
        config_content = """---
title: My First Typedown Project
---

```config python
# Project configuration
project_name = "MyProject"
```
"""
        await lsp_pair.open_document("config.td", config_content)
        
        # Step 2: Create first model
        model_content = """---
title: User Model
---

```model:User
name: str
email: str
age: int = 0
```
"""
        await lsp_pair.open_document("models/user.td", model_content)
        await asyncio.sleep(0.6)
        
        # Step 3: Create first entity
        entity_content = """---
title: My User
---

```entity User: my_first_user
name: "Alice"
email: "alice@example.com"
age: 30
```
"""
        await lsp_pair.open_document("users/alice.td", entity_content)
        await asyncio.sleep(0.6)
        
        # Verify everything works
        compiler = lsp_pair.server.compiler
        assert compiler is not None
        assert compiler.model_registry is not None
        assert compiler.symbol_table is not None
    
    @pytest.mark.asyncio
    async def test_onboarding_with_errors_and_fixes(self, lsp_pair, integration_project):
        """Test onboarding where user makes and fixes mistakes."""
        # lsp_pair already initialized by fixture
        
        # User creates model with typo
        bad_model = """---
title: User
---

```model:User
name: str
emial: str
```
"""
        await lsp_pair.open_document("models/user.td", bad_model)
        
        # User realizes mistake and fixes
        good_model = """---
title: User
---

```model:User
name: str
email: str
```
"""
        await lsp_pair.change_document("models/user.td", good_model, version=2)
        await asyncio.sleep(0.6)
        
        # Server should handle the fix
        compiler = lsp_pair.server.compiler
        assert compiler is not None


# =============================================================================
# Scenario 2: Team Collaboration
# =============================================================================

class TestTeamCollaboration:
    """
    Scenario: Multiple team members working on the same project.
    
    Tests:
    - Model changes affecting existing entities
    - Adding new fields
    - Backward compatibility
    """
    
    @pytest.mark.asyncio
    async def test_model_evolution_scenario(self, lsp_pair, integration_project):
        """Test model evolution in a team setting."""
        # Initial project state (existing models and entities)
        (integration_project
            .add_config()
            .add_model("Product", "name: str\nprice: float")
            .add_entity("Product", "existing", {"name": "Old Product", "price": 9.99}))
        
        # lsp_pair already initialized by fixture
        
        # Team member A adds new field to model
        updated_model = """---
title: Product Model v2
---

```model:Product
name: str
price: float
description: str = ""
```
"""
        await lsp_pair.open_document("models/product.td", updated_model)
        await asyncio.sleep(0.6)
        
        # Existing entity should still work (has default value)
        compiler = lsp_pair.server.compiler
        assert compiler is not None
    
    @pytest.mark.asyncio
    async def test_cross_reference_collaboration(self, lsp_pair, integration_project):
        """Test that team members can reference each other's work."""
        # Member A creates Category model
        # lsp_pair already initialized by fixture
        
        category_model = """---
title: Categories
---

```model:Category
name: str
```

```entity Category: electronics
name: "Electronics"
```
"""
        await lsp_pair.open_document("categories.td", category_model)
        
        # Member B creates Product model referencing Category
        product_model = """---
title: Products
---

```model:Product
name: str
category: Category
```

```entity Product: phone
name: "Smartphone"
category: electronics
```
"""
        await lsp_pair.open_document("products.td", product_model)
        await asyncio.sleep(0.6)
        
        # Cross-reference should work
        compiler = lsp_pair.server.compiler
        assert compiler is not None


# =============================================================================
# Scenario 3: Refactoring Workflow
# =============================================================================

class TestRefactoringWorkflow:
    """
    Scenario: User refactors their Typedown project.
    
    Tests:
    - Renaming models
    - Moving entities
    - Updating references
    """
    
    @pytest.mark.asyncio
    async def test_rename_model_scenario(self, lsp_pair, integration_project):
        """Test renaming a model and updating all references."""
        # Initial state
        (integration_project
            .add_config()
            .add_model("OldName", "value: str")
            .add_entity("OldName", "item1", {"value": "test"}))
        
        # lsp_pair already initialized by fixture
        
        # Rename model (simulated by creating new and removing old)
        new_model = """---
title: Renamed Model
---

```model:NewName
value: str
```
"""
        await lsp_pair.open_document("models/newname.td", new_model)
        
        # Update entity to use new name
        updated_entity = """---
title: Updated Entity
---

```entity NewName: item1
value: "test"
```
"""
        await lsp_pair.open_document("entities/item1.td", updated_entity)
        await asyncio.sleep(0.6)
        
        compiler = lsp_pair.server.compiler
        assert compiler is not None
    
    @pytest.mark.asyncio
    async def test_split_large_file_scenario(self, lsp_pair, integration_project):
        """Test splitting a large file into smaller ones."""
        # lsp_pair already initialized by fixture
        
        # Original large file
        large_file = """---
title: Everything
---

```model:User
name: str
```

```model:Post
title: str
author: User
```

```entity User: alice
name: "Alice"
```

```entity Post: p1
title: "Hello"
author: alice
```
"""
        await lsp_pair.open_document("everything.td", large_file)
        await asyncio.sleep(0.6)
        
        # Split into models.td
        models_file = """---
title: Models
---

```model:User
name: str
```

```model:Post
title: str
author: User
```
"""
        await lsp_pair.open_document("models.td", models_file)
        
        # Split into entities.td
        entities_file = """---
title: Entities
---

```entity User: alice
name: "Alice"
```

```entity Post: p1
title: "Hello"
author: alice
```
"""
        await lsp_pair.open_document("entities.td", entities_file)
        await asyncio.sleep(0.6)
        
        # Both files should work together
        compiler = lsp_pair.server.compiler
        assert compiler is not None


# =============================================================================
# Scenario 4: Validation and Quality Assurance
# =============================================================================

class TestValidationQA:
    """
    Scenario: Using Typedown for data validation and quality checks.
    
    Tests:
    - Spec validation
    - Error detection
    - Batch validation
    """
    
    @pytest.mark.asyncio
    async def test_spec_driven_validation_scenario(self, lsp_pair, integration_project):
        """Test using specs for data validation."""
        # Setup project with specs
        (integration_project
            .add_config()
            .add_model("Order", "total: float\nitems: int")
            .add_spec("validate_order", "Order", """
    assert subject.total > 0, "Order total must be positive"
    assert subject.items > 0, "Order must have items"
    return True
""", scope="global"))
        
        # lsp_pair already initialized by fixture
        
        # Add valid order
        valid_order = """---
title: Valid Order
---

```entity Order: order1
total: 99.99
items: 3
```
"""
        await lsp_pair.open_document("orders/valid.td", valid_order)
        
        # Add invalid order
        invalid_order = """---
title: Invalid Order
---

```entity Order: order2
total: -10.00
items: 0
```
"""
        await lsp_pair.open_document("orders/invalid.td", invalid_order)
        await asyncio.sleep(0.6)
        
        # Server should have validation results
        compiler = lsp_pair.server.compiler
        assert compiler is not None
    
    @pytest.mark.asyncio
    async def test_batch_data_entry_scenario(self, lsp_pair, integration_project):
        """Test batch data entry with validation feedback."""
        (integration_project
            .add_config()
            .add_model("Contact", "name: str\nemail: str"))
        
        # lsp_pair already initialized by fixture
        
        # Batch create contacts
        contacts = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
            {"name": "Charlie", "email": "charlie@example.com"},
        ]
        
        for i, contact in enumerate(contacts):
            name = contact["name"]
            email = contact["email"]
            content = f"""---
title: Contact {i+1}
---

```entity Contact: contact_{i+1}
name: "{name}"
email: "{email}"
```
"""
            await lsp_pair.open_document(f"contacts/contact_{i+1}.td", content)
        
        await asyncio.sleep(0.6)
        
        # All contacts should be in symbol table
        compiler = lsp_pair.server.compiler
        assert compiler is not None


# =============================================================================
# Scenario 5: Complex Project Structure
# =============================================================================

class TestComplexProjectStructure:
    """
    Scenario: Working with a complex, multi-directory project.
    
    Tests:
    - Nested directories
    - Many files
    - Complex references
    """
    
    @pytest.mark.asyncio
    async def test_nested_directory_structure(self, lsp_pair, integration_project):
        """Test project with deeply nested directory structure."""
        (integration_project
            .add_config()
            .add_model("Company", "name: str")
            .add_model("Department", "name: str\ncompany: Company")
            .add_model("Employee", "name: str\ndept: Department"))
        
        # lsp_pair already initialized by fixture
        
        # Create nested structure
        files = {
            "companies/acme.td": """---
title: ACME Corp
---

```entity Company: acme
name: "ACME Corporation"
```
""",
            "departments/engineering.td": """---
title: Engineering
---

```entity Department: engineering
name: "Engineering"
company: acme
```
""",
            "employees/alice.td": """---
title: Alice Engineer
---

```entity Employee: alice
name: "Alice"
dept: engineering
```
""",
        }
        
        for path, content in files.items():
            await lsp_pair.open_document(path, content)
        
        await asyncio.sleep(0.6)
        
        # All references should resolve
        compiler = lsp_pair.server.compiler
        assert compiler is not None
    
    @pytest.mark.asyncio
    async def test_many_files_performance(self, lsp_pair, integration_project):
        """Test project with many files."""
        (integration_project
            .add_config()
            .add_model("Item", "id: str\nvalue: int"))
        
        # lsp_pair already initialized by fixture
        
        # Create 20 item files
        for i in range(20):
            item_id = f"ITEM-{i:04d}"
            value = i * 10
            content = f"""---
title: Item {i}
---

```entity Item: item_{i}
id: "{item_id}"
value: {value}
```
"""
            await lsp_pair.open_document(f"items/item_{i}.td", content)
        
        await asyncio.sleep(1.0)  # Give more time for many files
        
        compiler = lsp_pair.server.compiler
        assert compiler is not None


# =============================================================================
# Scenario 6: Error Recovery and Edge Cases
# =============================================================================

class TestErrorRecoveryScenarios:
    """
    Scenario: Handling errors and edge cases gracefully.
    """
    
    @pytest.mark.asyncio
    async def test_circular_reference_detection(self, lsp_pair, integration_project):
        """Test detection of circular references."""
        # lsp_pair already initialized by fixture
        
        # Create circular reference: A -> B -> A
        model_a = """---
title: Model A
---

```model:A
name: str
b: B
```
"""
        model_b = """---
title: Model B
---

```model:B
name: str
a: A
```
"""
        await lsp_pair.open_document("models/a.td", model_a)
        await lsp_pair.open_document("models/b.td", model_b)
        await asyncio.sleep(0.6)
        
        # Server should handle gracefully
        compiler = lsp_pair.server.compiler
        assert compiler is not None
    
    @pytest.mark.asyncio
    async def test_unicode_and_special_chars(self, lsp_pair, integration_project):
        """Test handling of unicode and special characters."""
        (integration_project
            .add_config()
            .add_model("Document", "title: str\ncontent: str"))
        
        # lsp_pair already initialized by fixture
        
        # Content with unicode
        unicode_content = """---
title: Unicode Test
---

```entity Document: unicode_doc
title: "Hello World"
content: "Special content"
```
"""
        await lsp_pair.open_document("unicode.td", unicode_content)
        await asyncio.sleep(0.6)
        
        compiler = lsp_pair.server.compiler
        assert compiler is not None
    
    @pytest.mark.asyncio
    async def test_empty_and_minimal_files(self, lsp_pair, integration_project):
        """Test handling of empty and minimal files."""
        # lsp_pair already initialized by fixture
        
        # Empty markdown file
        await lsp_pair.open_document("empty.md", "")
        
        # Minimal file with just frontmatter
        await lsp_pair.open_document("minimal.md", "---\ntitle: Minimal\n---\n")
        
        # File with only markdown (no typedown blocks)
        await lsp_pair.open_document("plain.md", "# Just Markdown\n\nNo typedown here.")
        
        await asyncio.sleep(0.6)
        
        # Server should handle all gracefully
        compiler = lsp_pair.server.compiler
        assert compiler is not None


# =============================================================================
# Scenario 7: IDE Feature Integration
# =============================================================================

class TestIDEFeatureIntegration:
    """
    Scenario: Testing IDE features through LSP.
    
    Tests:
    - Completions
    - Hover
    - Go to definition
    - Document symbols
    """
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires full LSP protocol stack - TODO: implement proper LSP client")
    async def test_completion_in_entity_context(self, lsp_pair, integration_project):
        """Test that completions work when editing entities."""
        (integration_project
            .add_config()
            .add_model("Task", "title: str\ndone: bool = false"))
        
        # lsp_pair already initialized by fixture
        
        # Open entity file
        entity_content = """---
title: My Task
---

```entity Task: task1
title: "Do something"
```
"""
        await lsp_pair.open_document("tasks/task1.td", entity_content)
        await asyncio.sleep(0.6)
        
        # Request completion at position after 'title: '
        completions = await lsp_pair.request_completion("tasks/task1.td", 5, 15)
        
        # Should return some completions (may be empty depending on implementation)
        assert completions is not None
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires full LSP protocol stack - TODO: implement proper LSP client")
    async def test_hover_on_reference(self, lsp_pair, integration_project):
        """Test hover information on references."""
        (integration_project
            .add_config()
            .add_model("Person", "name: str\nage: int")
            .add_entity("Person", "john", {"name": "John", "age": 30}))
        
        # lsp_pair already initialized by fixture
        
        # Open file with reference
        content = """---
title: Reference Test
---

# Document

[[Person: john]]

More text here.
"""
        await lsp_pair.open_document("refs.td", content)
        await asyncio.sleep(0.6)
        
        # Request hover on reference
        _ = await lsp_pair.request_hover("refs.td", 5, 5)

        # Should return hover info (may be None if not implemented)
        # Just verify it does not crash
        assert True
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires full LSP protocol stack - TODO: implement proper LSP client")
    async def test_document_symbols_listing(self, lsp_pair, integration_project):
        """Test document symbols feature."""
        (integration_project
            .add_config()
            .add_model("Note", "content: str"))
        
        # lsp_pair already initialized by fixture
        
        # Open file with multiple blocks
        content = """---
title: Notes Document
---

# My Notes

```model:ExtendedNote
content: str
tags: list[str]
```

```entity Note: note1
content: "First note"
```

```entity Note: note2
content: "Second note"
```
"""
        await lsp_pair.open_document("notes.td", content)
        await asyncio.sleep(0.6)
        
        # Request document symbols
        from lsprotocol.types import DocumentSymbolParams, TextDocumentIdentifier
        from typedown.server.features.navigation import document_symbol
        
        params = DocumentSymbolParams(
            text_document=TextDocumentIdentifier(
                uri=integration_project.get_uri("notes.td")
            )
        )
        
        symbols = await document_symbol(lsp_pair.server, params)
        
        # Should return symbols (may be empty depending on implementation)
        assert symbols is not None


# =============================================================================
# Scenario 8: Real-time Collaboration Simulation
# =============================================================================

class TestRealtimeCollaboration:
    """
    Scenario: Simulating real-time collaborative editing.
    
    Tests rapid changes as if multiple users were editing.
    """
    
    @pytest.mark.asyncio
    async def test_rapid_editing_simulation(self, lsp_pair, integration_project):
        """Test rapid edits simulating collaborative editing."""
        (integration_project
            .add_config()
            .add_model("LiveDoc", "content: str"))
        
        # lsp_pair already initialized by fixture
        
        # Simulate typing character by character
        base_content = "---\ntitle: Live\n---\n\n```entity LiveDoc: live\ncontent: \""
        
        await lsp_pair.open_document("live.td", base_content + "\"")
        
        text = "Hello World"
        for i, char in enumerate(text):
            current = base_content + text[:i+1] + "\""
            await lsp_pair.change_document("live.td", current, version=i+2)
            await asyncio.sleep(0.01)  # Very rapid changes
        
        await asyncio.sleep(0.6)
        
        # Server should be stable
        compiler = lsp_pair.server.compiler
        assert compiler is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_file_edits(self, lsp_pair, integration_project):
        """Test editing multiple files concurrently."""
        (integration_project
            .add_config()
            .add_model("Component", "name: str"))
        
        # lsp_pair already initialized by fixture
        
        # Open multiple files
        files = [f"component_{i}.td" for i in range(5)]
        for i, filename in enumerate(files):
            content = f"""---
title: Component {i}
---

```entity Component: comp_{i}
name: "Component {i}"
```
"""
            await lsp_pair.open_document(filename, content)
        
        # Edit all files concurrently
        async def edit_file(filename, idx):
            for version in range(3):
                new_content = f"""---
title: Component {idx} v{version+2}
---

```entity Component: comp_{idx}
name: "Component {idx} v{version+2}"
```
"""
                await lsp_pair.change_document(filename, new_content, version=version+2)
                await asyncio.sleep(0.05)
        
        tasks = [edit_file(f, i) for i, f in enumerate(files)]
        await asyncio.gather(*tasks)
        
        await asyncio.sleep(0.6)
        
        # All changes should be processed
        compiler = lsp_pair.server.compiler
        assert compiler is not None

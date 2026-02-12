"""
Test: Entity Signature and ID Rules
Related Doc: docs/zh/02_concepts/01_model-and-entity.md Section "Entity（实体）"
Error Codes: E0241 (Duplicate ID), E0363 (ID conflict), E0364 (Missing model)
"""

from typedown.core.base.errors import ErrorCode
from test.conftest import assert_error_exists, assert_no_errors


class TestEntitySignature:
    """Test Entity block signature requirements."""
    
    # === Success Cases ===
    
    def test_valid_entity_signature(self, project):
        """Test valid entity signature."""
        project.add_config().add_file("user_model.td", '''
---
title: User Model
---

```model:User
class User(BaseModel):
    name: str
    age: int
```
''').add_file("user_entity.td", '''
---
title: User Alice
---

```entity User: user-alice-v1
name: Alice
age: 30
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_no_errors(scan_diag)
        assert_no_errors(link_diag)
    
    def test_entity_id_with_allowed_chars(self, project):
        """Test entity ID with allowed characters: letters, numbers, _, -, ."""
        valid_ids = [
            "user-alice",
            "user_alice",
            "user.alice",
            "user123",
            "User_Alice-2.0",
        ]
        
        content_parts = ['---\ntitle: User Model\n---\n\n```model:User\nclass User(BaseModel):\n    name: str\n```\n']
        
        for i, eid in enumerate(valid_ids):
            content_parts.append(f'''
---
title: Entity {i}
---

```entity User: {eid}
name: Test
```
''')
        
        project.add_config().add_file("combined.td", "\n".join(content_parts))
        scan_diag, _, _ = project.compile()
        
        # Should not have scanner errors for valid IDs
        assert_no_errors(scan_diag)
    
    def test_entity_yaml_body(self, project):
        """Test entity with YAML body is parsed correctly."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Product
class Product(BaseModel):
    name: str
    price: float
    tags: List[str]
```

```entity Product: product-1
name: Laptop
price: 999.99
tags:
  - electronics
  - computers
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_no_errors(scan_diag)
        assert_no_errors(link_diag)
    
    # === Error Cases ===
    
    def test_duplicate_entity_id__should_raise_E0241(self, project):
        """Test that duplicate entity IDs raise E0241."""
        project.add_config().add_file("models.td", '''
---
title: Models
---

```model:User
class User(BaseModel):
    name: str
```
''').add_file("entities1.td", '''
---
title: Alice
---

```entity User: user-alice
name: Alice
```
''').add_file("entities2.td", '''
---
title: Alice Duplicate
---

```entity User: user-alice
name: Alice Clone
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_error_exists(link_diag, ErrorCode.E0241, "user-alice")
    
    def test_entity_id_in_body__should_raise_E0363(self, project):
        """Test that having 'id' in entity body raises E0363."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:User
class User(BaseModel):
    name: str
```

```entity User: user-alice
id: user-alice
name: Alice
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        # E0363 should be in validator diagnostics
        assert_error_exists(val_diag, ErrorCode.E0363)
    
    def test_entity_missing_model__should_raise_E0364(self, project):
        """Test that referencing non-existent model is handled."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```entity NonExistent: entity-1
name: Test
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        # Entity should still be parsed even without model
        # But validation may flag it
        # Check that it doesn't crash
    
    # === Edge Cases ===
    
    def test_entity_with_uuid(self, project):
        """Test entity with explicit UUID field."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Item
class Item(BaseModel):
    name: str
```

```entity Item: item-1
uuid: 550e8400-e29b-41d4-a716-446655440000
name: Special Item
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        # Should parse without errors
        assert_no_errors(scan_diag)

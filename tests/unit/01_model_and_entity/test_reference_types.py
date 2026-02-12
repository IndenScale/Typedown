"""
Test: Reference Types (Ref[T])
Related Doc: docs/zh/02_concepts/01_model-and-entity.md Section "引用类型"
Error Codes: E0362 (Type mismatch in Ref[T])
"""

import pytest
from typedown.core.base.errors import ErrorCode
from test.conftest import assert_error_exists


class TestReferenceTypes:
    """Test Ref[T] type system and validation."""
    
    # === Success Cases ===
    
    def test_single_type_reference(self, project):
        """Test single type Ref[T] works correctly."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:User
class User(BaseModel):
    name: str
```

```model:Task
class Task(BaseModel):
    title: str
    assignee: Ref["User"]
```

```entity User: user-alice
name: Alice
```

```entity Task: task-1
title: Fix Bug
assignee: [[user-alice]]
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        # Should not have type mismatch errors
        errors = [e for e in val_diag.errors if e.code == ErrorCode.E0362]
        assert len(errors) == 0
    
    def test_optional_reference(self, project):
        """Test Optional[Ref[T]] works correctly."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Node
class Node(BaseModel):
    name: str
    parent: Optional[Ref["Node"]] = None
```

```entity Node: node-1
name: Root
parent: null
```

```entity Node: node-2
name: Child
parent: [[node-1]]
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        errors = [e for e in val_diag.errors if e.code == ErrorCode.E0362]
        assert len(errors) == 0
    
    def test_list_of_references(self, project):
        """Test List[Ref[T]] works correctly."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:User
class User(BaseModel):
    name: str
```

```model:Group
class Group(BaseModel):
    name: str
    members: List[Ref["User"]]
```

```entity User: user-bob
name: Bob
```

```entity User: user-alice
name: Alice
```

```entity Group: team-a
name: Team A
members:
  - [[user-bob]]
  - [[user-alice]]
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        errors = [e for e in val_diag.errors if e.code == ErrorCode.E0362]
        assert len(errors) == 0
    
    # === Error Cases ===
    
    def test_ref_type_mismatch__should_raise_E0362(self, project):
        """Test that Ref[T] pointing to wrong type raises E0362."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:User
class User(BaseModel):
    name: str
```

```model:Product
class Product(BaseModel):
    name: str
```

```model:Order
class Order(BaseModel):
    buyer: Ref["User"]
```

```entity Product: product-1
name: Laptop
```

```entity Order: order-1
buyer: [[product-1]]
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_error_exists(val_diag, ErrorCode.E0362, "User")
    
    def test_ref_to_nonexistent_entity__should_raise_E0341(self, project):
        """Test that Ref to non-existent entity raises E0341."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:User
class User(BaseModel):
    name: str
```

```model:Task
class Task(BaseModel):
    assignee: Ref["User"]
```

```entity Task: task-1
assignee: [[nonexistent-user]]
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_error_exists(val_diag, ErrorCode.E0341)
    
    # === Edge Cases / Known Limitations ===
    
    @pytest.mark.skip(reason="Polymorphic references not yet implemented")
    def test_polymorphic_reference(self, project):
        """Test Ref[T1, T2] polymorphic reference (documented but not implemented)."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:User
class User(BaseModel):
    name: str
```

```model:ServiceAccount
class ServiceAccount(BaseModel):
    service_name: str
```

```model:Task
class Task(BaseModel):
    # Polymorphic reference - documented but not implemented
    subject: Ref["User", "ServiceAccount"]
```
''')
        # This test is skipped until polymorphic references are implemented
        pass
    
    def test_reference_naming_consistency(self):
        """Test that Ref and Reference naming is consistent.
        
        Doc says: Reference[T]
        Implementation: Ref["T"]
        
        This test documents the current state.
        """
        from typedown.core.base.types import Ref, ReferenceMeta
        
        # Ref should be available
        assert Ref is not None
        
        # Ref["Type"] should return Annotated type
        ref_type = Ref["User"]
        assert ref_type is not None
        
        # Check that ReferenceMeta is attached
        from typing import get_args, get_origin, Annotated
        assert get_origin(ref_type) is Annotated
        
        args = get_args(ref_type)
        assert len(args) >= 2
        assert isinstance(args[1], ReferenceMeta)
        assert args[1].target_type == "User"

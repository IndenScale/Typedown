"""
Test: Reference Type Safety
Related Doc: docs/zh/03_guides/01_references.md Section "类型安全"
Error Codes: E0362 (Type mismatch in Ref[T])
"""

from typedown.core.base.errors import ErrorCode
from tests.conftest import assert_error_exists


class TestTypeSafety:
    """Test Ref[T] type safety enforcement."""
    
    def test_correct_type_reference(self, project):
        """Test that correct type reference passes."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Person
class Person(BaseModel):
    name: str
```

```model:Task
class Task(BaseModel):
    title: str
    owner: Ref["Person"]
```

```entity Person: person-1
name: John
```

```entity Task: task-1
title: Do Work
owner: [[person-1]]
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        errors = [e for e in val_diag.errors if e.code == ErrorCode.E0362]
        assert len(errors) == 0
    
    def test_wrong_type_reference(self, project):
        """Test that wrong type reference raises E0362."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Person
class Person(BaseModel):
    name: str
```

```model:Company
class Company(BaseModel):
    name: str
```

```model:Task
class Task(BaseModel):
    title: str
    owner: Ref["Person"]
```

```entity Company: company-1
name: Acme Corp
```

```entity Task: task-1
title: Do Work
owner: [[company-1]]
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_error_exists(val_diag, ErrorCode.E0362)
    
    def test_list_of_refs_type_check(self, project):
        """Test type checking for List[Ref[T]]."""
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

```model:Group
class Group(BaseModel):
    name: str
    members: List[Ref["User"]]
```

```entity Product: product-1
name: Laptop
```

```entity Group: group-1
name: Bad Group
members:
  - [[product-1]]
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        # Should detect that product-1 is Product, not User
        assert_error_exists(val_diag, ErrorCode.E0362)

"""
Test: ID Reference [[entity-id]]
Related Doc: docs/zh/03_guides/01_references.md Section "ID 规范"
Error Codes: E0341 (Reference resolution failed)
"""

import pytest
from test.conftest import assert_error_exists, assert_no_errors


class TestIdReference:
    """Test ID reference syntax and resolution."""
    
    def test_simple_id_reference(self, project):
        """Test simple [[entity-id]] reference."""
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
        
        assert_no_errors(scan_diag)
        assert_no_errors(link_diag)
    
    def test_id_with_dashes(self, project):
        """Test ID with dashes (slug-style)."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Item
class Item(BaseModel):
    name: str
```

```entity Item: iam-user-alice-v1
name: Alice
```
''')
        scan_diag, _, _ = project.compile()
        
        assert_no_errors(scan_diag)
    
    def test_id_with_underscores(self, project):
        """Test ID with underscores."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Item
class Item(BaseModel):
    name: str
```

```entity Item: user_alice_v1
name: Alice
```
''')
        scan_diag, _, _ = project.compile()
        
        assert_no_errors(scan_diag)
    
    def test_id_with_dots(self, project):
        """Test ID with dots.
        
        Note: Implementation allows dots, but doc says only _ and -.
        This test documents the current behavior.
        """
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Item
class Item(BaseModel):
    name: str
```

```entity Item: v1.2.config
name: Config
```
''')
        scan_diag, _, _ = project.compile()
        
        # Currently allowed by implementation
        assert_no_errors(scan_diag)

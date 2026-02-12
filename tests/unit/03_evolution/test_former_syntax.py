"""
Test: Linear Evolution (former)
Related Doc: docs/zh/02_concepts/03_evolution.md Section "线性演进"
Error Codes: E0343 (Evolution target not found)
"""

import pytest
from typedown.core.base.errors import ErrorCode
from test.conftest import assert_error_exists, assert_no_errors


class TestFormerSyntax:
    """Test former field syntax and semantics."""
    
    # === Success Cases ===
    
    def test_former_with_id_reference(self, project):
        """Test former with ID reference [[target-id]]."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Feature
class Feature(BaseModel):
    status: str
```

```entity Feature: login_v1
status: planned
```

```entity Feature: login_v2
former: [[login_v1]]
status: in_progress
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        # Should not have evolution target errors
        errors = [e for e in val_diag.errors if e.code == ErrorCode.E0343]
        assert len(errors) == 0
    
    def test_former_with_hash_reference(self, project):
        """Test former with hash reference [[sha256:...]]."""
        # Note: This requires content hashing to work
        pass
    
    def test_former_chain(self, project):
        """Test chain of former references."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Document
class Document(BaseModel):
    version: str
    content: str
```

```entity Document: doc-v1
version: "1.0"
content: "Initial"
```

```entity Document: doc-v2
former: [[doc-v1]]
version: "2.0"
content: "Updated"
```

```entity Document: doc-v3
former: [[doc-v2]]
version: "3.0"
content: "Final"
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        errors = [e for e in val_diag.errors if e.code == ErrorCode.E0343]
        assert len(errors) == 0
    
    def test_former_list_syntax(self, project):
        """Test former field with YAML list syntax."""
        # former can be:
        # - "id" (Str)
        # - ["id"] (List[Str])
        # - [["id"]] (List[List[Str]] - Ref Sugar)
        pass
    
    # === Error Cases ===
    
    def test_former_target_not_found__should_raise_E0343(self, project):
        """Test that former pointing to non-existent entity raises E0343."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Feature
class Feature(BaseModel):
    status: str
```

```entity Feature: login_v2
former: [[nonexistent-v1]]
status: in_progress
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_error_exists(val_diag, ErrorCode.E0343, "nonexistent-v1")
    
    # === Semantics Tests ===
    
    def test_former_pure_pointer_no_merge(self, project):
        """Test that former is pure pointer, no data merging."""
        # According to doc: "Pure Pointer Logic: compiler does NOT merge data"
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Item
class Item(BaseModel):
    name: str
    value: int
```

```entity Item: item-v1
name: Original Name
value: 100
```

```entity Item: item-v2
former: [[item-v1]]
name: New Name
# Note: value is NOT specified, should NOT be inherited
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        # v2 should be validated independently
        # The pure pointer semantics means former is metadata only
    
    @pytest.mark.skip(reason="Immutability not enforced")
    def test_former_target_immutability(self, project):
        """Test that former targets are immutable (append-only)."""
        # Doc says: "被指向的实体不应再修改（Append Only）"
        # This is not currently enforced
        pass

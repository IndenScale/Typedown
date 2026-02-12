"""
Test: List Reference Syntax
Related Doc: docs/zh/03_guides/01_references.md Section "列表引用"
"""

import pytest
from test.conftest import assert_no_errors


class TestListReference:
    """Test list reference syntax sugar."""
    
    def test_block_style_list_reference(self, project):
        """Test block-style list references (- [[id]])."""
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
        
        assert_no_errors(scan_diag)
        assert_no_errors(link_diag)
    
    def test_flow_style_list_reference(self, project):
        """Test flow-style list references ([[[id]], [[id]]])."""
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
    reviewers: List[Ref["User"]]
```

```entity User: user-vader
name: Vader
```

```entity User: user-tarkin
name: Tarkin
```

```entity Group: empire-council
name: Empire Council
reviewers: [[[user-vader]], [[user-tarkin]]]
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_no_errors(scan_diag)
    
    def test_nested_list_desugaring(self, project):
        """Test that [[['ref']] is desugared to [[ref]]."""
        # YAML parses - [[ref]] as [['ref']]
        # The desugarer should convert this back to "[[ref]]"
        pass

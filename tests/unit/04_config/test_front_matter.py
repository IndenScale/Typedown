"""
Test: Front Matter Parsing
Related Doc: docs/zh/02_concepts/04_config.md Section "2. Front Matter"
"""

import pytest
from test.conftest import assert_no_errors


class TestFrontMatter:
    """Test Front Matter parsing and fields."""
    
    def test_front_matter_title(self, project):
        """Test title field parsing."""
        project.add_config().add_file("test.td", '''
---
title: My Document Title
---

# Content

```model:Test
class Test(BaseModel):
    name: str
```
''')
        scan_diag, _, _ = project.compile()
        
        assert_no_errors(scan_diag)
    
    def test_front_matter_tags(self, project):
        """Test tags field parsing."""
        project.add_config().add_file("test.td", '''
---
title: Tagged Doc
tags: [api, v2, critical]
---

# Content
''')
        scan_diag, _, _ = project.compile()
        
        assert_no_errors(scan_diag)
    
    def test_front_matter_author(self, project):
        """Test author field parsing."""
        project.add_config().add_file("test.td", '''
---
title: Authored Doc
author: John Doe
---

# Content
''')
        scan_diag, _, _ = project.compile()
        
        assert_no_errors(scan_diag)
    
    def test_front_matter_scripts(self, project):
        """Test scripts field parsing."""
        project.add_config().add_file("test.td", '''
---
title: Scripted Doc
scripts:
  validate: 'typedown check --full ${FILE}'
  test-api: 'pytest tests/api.py --id ${entity.id}'
  ci-pass: 'typedown check --full ${FILE} && typedown run test-api'
---

# Content
''')
        scan_diag, _, _ = project.compile()
        
        assert_no_errors(scan_diag)
    
    def test_front_matter_order(self, project):
        """Test order field parsing."""
        project.add_config().add_file("test.td", '''
---
title: Ordered Doc
order: 10
---

# Content
''')
        scan_diag, _, _ = project.compile()
        
        assert_no_errors(scan_diag)

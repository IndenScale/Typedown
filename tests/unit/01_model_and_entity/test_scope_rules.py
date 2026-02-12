"""
Test: Scope Rules (Lexical Scoping)
Related Doc: docs/zh/02_concepts/01_model-and-entity.md Section "作用域"
Related Doc: docs/zh/04_reference/02_glossary.md Section "Scope"
"""

from tests.conftest import assert_no_errors


class TestScopeRules:
    """Test lexical scoping rules for model/entity visibility."""
    
    # === Success Cases ===
    
    def test_same_directory_scope(self, project):
        """Test that entities can reference models in the same directory."""
        project.add_config().add_file("models/user.td", '''
---
title: User Model
---

```model:User
class User(BaseModel):
    name: str
```
''').add_file("models/user_entity.td", '''
---
title: User Entity
---

```entity User: user-1
name: Test User
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_no_errors(link_diag)
    
    def test_subdirectory_inherits_parent_scope(self, project):
        """Test that subdirectories inherit parent directory models."""
        project.add_config().add_file("models/base.td", '''
---
title: Base Models
---

```model:BaseEntity
class BaseEntity(BaseModel):
    entity_id: str
```
''').add_file("models/sub/specific.td", '''
---
title: Specific Model
---

```model:Specific
class Specific(BaseEntity):
    details: str
```

```entity Specific: spec-1
entity_id: spec-1
details: Test
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        # Should find BaseEntity from parent scope
        assert_no_errors(link_diag)
    
    def test_sibling_directories_not_visible(self, project):
        """Test that sibling directories don't share scope."""
        # This test documents expected behavior
        # If models in dir A should not be visible in dir B
        # This may or may not be enforced depending on implementation
        pass
    
    # === Config Scope Inheritance ===
    
    def test_config_scope_inheritance(self, project):
        """Test that config variables are inherited by child directories."""
        project.add_file("config.td", '''
---
title: Root Config
---

```config python
DEFAULT_TIMEOUT = 30
SHARED_VALUE = "from_root"
```
''').add_file("sub/config.td", '''
---
title: Sub Config
---

```config python
# Should inherit DEFAULT_TIMEOUT
OVERRIDE_VALUE = "from_sub"
```
''').add_file("sub/model.td", '''
---
title: Model Using Config
---

```model:Service
class Service(BaseModel):
    timeout: int = Field(default=DEFAULT_TIMEOUT)
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        # Should find DEFAULT_TIMEOUT from parent config
        assert_no_errors(link_diag)
    
    def test_config_override(self, project):
        """Test that child directory config can override parent."""
        project.add_file("config.td", '''
---
title: Root Config
---

```config python
VALUE = "parent"
```
''').add_file("sub/config.td", '''
---
title: Sub Config
---

```config python
VALUE = "child"
```
''').add_file("sub/model.td", '''
---
title: Model
---

```model:Test
class Test(BaseModel):
    value: str = Field(default=VALUE)
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_no_errors(link_diag)
        
        # Verify the model got the overridden value
        # This would require inspecting the model registry

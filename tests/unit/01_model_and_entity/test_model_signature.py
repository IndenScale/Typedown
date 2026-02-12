"""
Test: Model Signature Strictness
Related Doc: docs/zh/02_concepts/01_model-and-entity.md Section "代码块签名规范"
Error Codes: E0231 (Class name mismatch), E0233 (Invalid model type)
"""

import pytest
from typedown.core.base.errors import ErrorCode
from tests.conftest import assert_error_exists, assert_no_errors


class TestModelSignatureStrictness:
    """Test Model block signature strictness requirements."""
    
    # === Success Cases ===
    
    def test_model_id_matches_class_name(self, project):
        """Test that model block ID matching class name is valid."""
        project.add_config().add_file("user.td", '''
---
title: User Model
---

```model:User
class User(BaseModel):
    name: str
    age: int
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_no_errors(scan_diag)
        assert_no_errors(link_diag)
    
    def test_model_colon_whitespace_variations(self, project):
        """Test that whitespace variations around colon are accepted."""
        variations = [
            "```model:User",
            "```model : User",
            "```model: User",
            "```model :User",
        ]
        
        for i, info_str in enumerate(variations):
            content = f'''---
title: Test
---

{info_str}
class User(BaseModel):
    name: str
```
'''
            p = TestProjectBuilder()
            p.add_config().add_file(f"test_{i}.td", content)
            scan_diag, link_diag, _ = p.compile()
            
            errors = [e for e in link_diag.errors if e.code == ErrorCode.E0231]
            assert len(errors) == 0, f"Variation '{info_str}' should not cause E0231"
            p.cleanup()
    
    def test_model_with_field_validator(self, project):
        """Test model with @field_validator works correctly."""
        project.add_config().add_file("order.td", '''
---
title: Order Model
---

```model:Order
class Order(BaseModel):
    item_id: str
    quantity: int
    price: float

    @field_validator('quantity')
    @classmethod
    def check_qty(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('数量必须大于 0')
        return v
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_no_errors(link_diag)
    
    def test_model_with_reference_field(self, project):
        """Test model with Ref[T] field works correctly."""
        project.add_config().add_file("models.td", '''
---
title: Models
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
''')
        scan_diag, link_diag, _ = project.compile()
        
        # Should not have model type errors
        errors = [e for e in link_diag.errors if e.code == ErrorCode.E0233]
        assert len(errors) == 0
    
    # === Error Cases ===
    
    def test_model_id_class_name_mismatch__should_raise_E0231(self, project):
        """Test that model ID not matching class name raises E0231."""
        project.add_config().add_file("user.td", '''
---
title: User Model
---

```model:UserProfile
class User(BaseModel):
    name: str
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_error_exists(link_diag, ErrorCode.E0231, "User")
    
    def test_model_not_base_model__should_raise_E0233(self, project):
        """Test that non-BaseModel class raises E0233."""
        project.add_config().add_file("invalid.td", '''
---
title: Invalid Model
---

```model:RegularClass
class RegularClass:
    name: str
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_error_exists(link_diag, ErrorCode.E0233, "RegularClass")
    
    def test_model_reserved_id_field__should_raise_E0232(self, project):
        """Test that using reserved 'id' field raises E0232."""
        project.add_config().add_file("bad_model.td", '''
---
title: Bad Model
---

```model:BadUser
class BadUser(BaseModel):
    id: str
    name: str
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_error_exists(link_diag, ErrorCode.E0232, "BadUser")
    
    def test_model_import_in_model_block__should_fail(self, project):
        """Test that import statements in model block are rejected."""
        # This should be caught at parser level
        content = '''
---
title: Model with Import
---

```model:BadModel
import os

class BadModel(BaseModel):
    name: str
```
'''
        project.add_config()
        # Parser should raise ValueError during parsing
        from typedown.core.parser import TypedownParser
        parser = TypedownParser()
        
        import tempfile
        import os as os_module
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.td', delete=False)
        temp_file.write(content)
        temp_file.close()
        
        try:
            with pytest.raises(ValueError) as exc_info:
                parser.parse(temp_file.name)
            assert "Imports are forbidden" in str(exc_info.value)
        finally:
            os_module.unlink(temp_file.name)
    
    # === Edge Cases ===
    
    def test_model_enum_is_valid(self, project):
        """Test that Enum classes are valid in model blocks."""
        project.add_config().add_file("status.td", '''
---
title: Status Enum
---

```model:Status
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        # Enum should be accepted as valid model type
        errors = [e for e in link_diag.errors if e.code == ErrorCode.E0233]
        assert len(errors) == 0


# Need to import here to avoid circular import in fixture
from tests.conftest import TestProjectBuilder  # noqa: E402

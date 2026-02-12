"""
Test: Field-level Validation (@field_validator)
Related Doc: docs/zh/02_concepts/02_validation.md Section "1. 字段级验证"
Error Codes: E0361 (Schema validation failed)
"""

import pytest
from typedown.core.base.errors import ErrorCode
from test.conftest import assert_error_exists, assert_no_errors


class TestFieldValidator:
    """Test Pydantic @field_validator integration."""
    
    # === Success Cases ===
    
    def test_valid_field_passes_validation(self, project):
        """Test that valid field values pass validation."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:User
class User(BaseModel):
    email: str
    age: int

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('邮箱格式无效')
        return v

    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError('年龄范围无效')
        return v
```

```entity User: user-1
email: alice@example.com
age: 30
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_no_errors(val_diag)
    
    def test_field_validator_transforms_value(self, project):
        """Test that field validator can transform values."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Product
class Product(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip().title()
```

```entity Product: prod-1
name: "  laptop computer  "
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        # Transformation should not cause validation error
        errors = [e for e in val_diag.errors if e.code == ErrorCode.E0361]
        assert len(errors) == 0
    
    # === Error Cases ===
    
    def test_invalid_field_fails_validation__should_raise_E0361(self, project):
        """Test that invalid field values raise E0361."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:User
class User(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('邮箱格式无效')
        return v
```

```entity User: user-1
email: "invalid-email"
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_error_exists(val_diag, ErrorCode.E0361, "email")
    
    def test_age_range_validation(self, project):
        """Test age range validation with boundary values."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Person
class Person(BaseModel):
    name: str
    age: int

    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError('年龄必须在 0-150 之间')
        return v
```

```entity Person: person-negative
name: Test
age: -5
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_error_exists(val_diag, ErrorCode.E0361)

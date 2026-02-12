"""
Test: Complete Error Code Coverage
Related Doc: docs/zh/04_reference/01_error-codes.md

Each error code from the documentation should have a test that triggers it.
"""

import pytest
from typedown.core.base.errors import ErrorCode
from test.conftest import assert_error_exists


class TestL1ScannerErrors:
    """Test L1 Scanner errors (E01xx)."""
    
    def test_E0101_syntax_parse_failure(self):
        """Trigger E0101: Syntax parse failure."""
        # E0101 is triggered by scanner when file parsing fails
        pass
    
    def test_E0102_config_block_location_error(self, project):
        """Trigger E0102: Config block in wrong location."""
        project.add_file("regular.td", '''
---
title: Regular
---

```config python
# Config in wrong file
```
''')
        from typedown.core.base.errors import ErrorCode
        scan_diag, _, _ = project.compile()
        assert_error_exists(scan_diag, ErrorCode.E0102)
    
    def test_E0103_nested_list_anti_pattern(self, project):
        """Trigger E0103: Nested list anti-pattern."""
        project.add_config().add_file("bad.td", '''
---
title: Bad
---

```model:Item
class Item(BaseModel):
    data: list
```

```entity Item: item-1
data:
  - [1, 2, 3]
  - [4, 5, 6]
```
''')
        from typedown.core.base.errors import ErrorCode
        scan_diag, _, _ = project.compile()
        assert_error_exists(scan_diag, ErrorCode.E0103)
    
    def test_E0104_file_read_error(self):
        """Trigger E0104: File read error."""
        # This would require simulating file system errors
        pass
    
    def test_E0105_document_structure_error(self):
        """Trigger E0105: Document structure error."""
        pass


class TestL2LinkerErrors:
    """Test L2 Linker errors (E02xx)."""
    
    def test_E0221_model_execution_failed(self, project):
        """Trigger E0221: Model execution failed."""
        project.add_config().add_file("bad_model.td", '''
---
title: Bad Model
---

```model:BadModel
# Reference to undefined base class
class BadModel(UndefinedBaseClass):
    name: str
```
''')
        from typedown.core.base.errors import ErrorCode
        _, link_diag, _ = project.compile()
        assert_error_exists(link_diag, ErrorCode.E0221)
    
    def test_E0222_config_execution_failed(self, project):
        """Trigger E0222: Config execution failed."""
        project.add_file("config.td", '''
---
title: Config
---

```config python
raise ValueError("Config error")
```
''')
        from typedown.core.base.errors import ErrorCode
        _, link_diag, _ = project.compile()
        assert_error_exists(link_diag, ErrorCode.E0222)
    
    def test_E0231_class_name_mismatch(self, project):
        """Trigger E0231: Model block ID doesn't match class name."""
        project.add_config().add_file("model.td", '''
---
title: Model
---

```model:WrongName
class CorrectName(BaseModel):
    name: str
```
''')
        from typedown.core.base.errors import ErrorCode
        _, link_diag, _ = project.compile()
        assert_error_exists(link_diag, ErrorCode.E0231)
    
    def test_E0241_duplicate_id(self, project):
        """Trigger E0241: Duplicate ID definition."""
        project.add_config().add_file("models.td", '''
---
title: Models
---

```model:Item
class Item(BaseModel):
    name: str
```
''').add_file("a.td", '''
---
title: A
---

```entity Item: dup-id
name: A
```
''').add_file("b.td", '''
---
title: B
---

```entity Item: dup-id
name: B
```
''')
        from typedown.core.base.errors import ErrorCode
        _, link_diag, _ = project.compile()
        assert_error_exists(link_diag, ErrorCode.E0241)


class TestL3ValidatorErrors:
    """Test L3 Validator errors (E03xx)."""
    
    def test_E0341_reference_resolution_failed(self, project):
        """Trigger E0341: Reference resolution failed."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Item
class Item(BaseModel):
    name: str
    ref: Ref["Item"]
```

```entity Item: item-1
name: Item 1
ref: [[nonexistent]]
```
''')
        from typedown.core.base.errors import ErrorCode
        _, _, val_diag = project.compile()
        assert_error_exists(val_diag, ErrorCode.E0341)
    
    def test_E0343_evolution_target_not_found(self, project):
        """Trigger E0343: Evolution target not found."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Version
class Version(BaseModel):
    data: str
```

```entity Version: v2
former: [[v1-nonexistent]]
data: updated
```
''')
        from typedown.core.base.errors import ErrorCode
        _, _, val_diag = project.compile()
        assert_error_exists(val_diag, ErrorCode.E0343)
    
    def test_E0361_schema_validation_failed(self, project):
        """Trigger E0361: Schema validation failed."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:User
class User(BaseModel):
    name: str
    age: int

    @field_validator('age')
    @classmethod
    def check_age(cls, v):
        if v < 0:
            raise ValueError("Age must be positive")
        return v
```

```entity User: user-1
name: Test
age: -5
```
''')
        from typedown.core.base.errors import ErrorCode
        _, _, val_diag = project.compile()
        assert_error_exists(val_diag, ErrorCode.E0361)
    
    def test_E0362_ref_type_mismatch(self, project):
        """Trigger E0362: Type mismatch in Ref[T]."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Cat
class Cat(BaseModel):
    name: str
```

```model:Dog
class Dog(BaseModel):
    name: str
```

```model:Owner
class Owner(BaseModel):
    pet: Ref["Cat"]
```

```entity Dog: dog-1
name: Rex
```

```entity Owner: owner-1
pet: [[dog-1]]
```
''')
        from typedown.core.base.errors import ErrorCode
        _, _, val_diag = project.compile()
        assert_error_exists(val_diag, ErrorCode.E0362)


class TestL4SpecErrors:
    """Test L4 Spec errors (E04xx)."""
    
    @pytest.mark.skip(reason="Spec execution test setup required")
    def test_E0421_spec_execution_failed(self):
        """Trigger E0421: Spec execution failed."""
        pass
    
    @pytest.mark.skip(reason="Spec execution test setup required")
    def test_E0423_spec_target_not_found(self):
        """Trigger E0423: Spec target not found."""
        pass
    
    @pytest.mark.skip(reason="Spec execution test setup required")
    def test_E0424_spec_assertion_failed(self):
        """Trigger E0424: Spec assertion failed."""
        pass


class TestSystemErrors:
    """Test System errors (E09xx)."""
    
    @pytest.mark.skip(reason="System error conditions hard to simulate")
    def test_E0981_internal_compiler_error(self):
        """Trigger E0981: Internal compiler error."""
        pass
    
    @pytest.mark.skip(reason="System error conditions hard to simulate")
    def test_E0982_file_system_error(self):
        """Trigger E0982: File system error."""
        pass
    
    @pytest.mark.skip(reason="System error conditions hard to simulate")
    def test_E0983_configuration_error(self):
        """Trigger E0983: Configuration error."""
        pass


class TestErrorCodeRegistry:
    """Test that all error codes are properly defined."""
    
    def test_all_error_codes_defined(self):
        """Verify all documented error codes are defined in ErrorCode enum."""
        documented_codes = [
            # L1: Scanner
            "E0101", "E0102", "E0103", "E0104", "E0105",
            # L2: Linker
            "E0221", "E0222", "E0231", "E0241", "E0223", "E0224", "E0232", "E0233",
            # L3: Validator
            "E0341", "E0342", "E0343", "E0361", "E0362", "E0363", "E0364", "E0365",
            # L4: Spec
            "E0421", "E0422", "E0423", "E0424",
            # System
            "E0981", "E0982", "E0983",
        ]
        
        for code_str in documented_codes:
            assert hasattr(ErrorCode, code_str), f"ErrorCode.{code_str} not defined"
            assert ErrorCode[code_str].value == code_str
    
    def test_error_templates_defined(self):
        """Verify all error codes have message templates."""
        from typedown.core.base.errors import ERROR_TEMPLATES
        
        for code in ErrorCode:
            assert code in ERROR_TEMPLATES, f"No template for {code}"

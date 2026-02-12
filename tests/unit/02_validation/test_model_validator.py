"""
Test: Model-level Validation (@model_validator)
Related Doc: docs/zh/02_concepts/02_validation.md Section "2. 模型级验证"
Error Codes: E0361 (Schema validation failed)
"""

from typedown.core.base.errors import ErrorCode
from tests.conftest import assert_error_exists, assert_no_errors


class TestModelValidator:
    """Test Pydantic @model_validator integration."""
    
    # === Success Cases ===
    
    def test_valid_model_passes_validation(self, project):
        """Test that valid multi-field constraints pass."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:TimeRange
from datetime import datetime
from pydantic import model_validator

class TimeRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode='after')
    def check_time_order(self):
        if self.end <= self.start:
            raise ValueError('结束时间必须晚于开始时间')
        return self
```

```entity TimeRange: range-1
start: 2024-01-01T10:00:00
end: 2024-01-01T12:00:00
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_no_errors(val_diag)
    
    def test_model_validator_with_multiple_fields(self, project):
        """Test model validator accessing multiple fields."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Order
from pydantic import model_validator

class Order(BaseModel):
    quantity: int
    unit_price: float
    total_price: float

    @model_validator(mode='after')
    def check_total(self):
        expected = self.quantity * self.unit_price
        if abs(self.total_price - expected) > 0.01:
            raise ValueError(f'总价不匹配: 期望 {expected}, 实际 {self.total_price}')
        return self
```

```entity Order: order-1
quantity: 5
unit_price: 10.00
total_price: 50.00
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_no_errors(val_diag)
    
    # === Error Cases ===
    
    def test_invalid_time_range__should_raise_E0361(self, project):
        """Test that invalid time order raises E0361."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:TimeRange
from datetime import datetime
from pydantic import model_validator

class TimeRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode='after')
    def check_time_order(self):
        if self.end <= self.start:
            raise ValueError('结束时间必须晚于开始时间')
        return self
```

```entity TimeRange: range-bad
start: 2024-01-01T12:00:00
end: 2024-01-01T10:00:00
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_error_exists(val_diag, ErrorCode.E0361, "结束时间")
    
    def test_price_mismatch_detection(self, project):
        """Test that price mismatch is detected."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Order
from pydantic import model_validator

class Order(BaseModel):
    quantity: int
    unit_price: float
    total_price: float

    @model_validator(mode='after')
    def check_total(self):
        expected = self.quantity * self.unit_price
        if abs(self.total_price - expected) > 0.01:
            raise ValueError('价格不匹配')
        return self
```

```entity Order: order-bad
quantity: 5
unit_price: 10.00
total_price: 100.00
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        assert_error_exists(val_diag, ErrorCode.E0361)

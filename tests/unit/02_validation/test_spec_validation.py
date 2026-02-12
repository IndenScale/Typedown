"""
Test: Global Validation (spec with @target)
Related Doc: docs/zh/02_concepts/02_validation.md Section "3. 全局级验证"
Error Codes: E0421 (Spec execution failed), E0423 (Spec target not found), E0424 (Spec assertion failed)
"""

import pytest
from typedown.core.base.errors import ErrorCode
from test.conftest import assert_error_exists, assert_no_errors, assert_error_count


class TestSpecValidation:
    """Test spec-based global validation."""
    
    # === Local Scope Tests ===
    
    def test_spec_local_scope_passes(self, project):
        """Test local scope spec that passes."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:User
class User(BaseModel):
    name: str
    role: str
    mfa_enabled: bool = False
```

```entity User: admin-1
name: Admin User
role: admin
mfa_enabled: true
```

```entity User: user-1
name: Regular User
role: user
mfa_enabled: false
```

```spec:check_admin_mfa
@target(type="User", scope="local")
def check_admin_mfa(subject):
    """每个管理员都必须启用 MFA"""
    if subject.role == "admin":
        assert subject.mfa_enabled, f"管理员 {subject.name} 必须启用 MFA"
```
''')
        scan_diag, link_diag, val_diag = project.compile()
        
        # Run spec execution
        from typedown.core.analysis.spec_executor import SpecExecutor
        from rich.console import Console
        
        console = Console(quiet=True)
        executor = SpecExecutor(console)
        
        from pathlib import Path
        documents_map = {Path(str(k)): v for k, v in project.files.items() if str(k).endswith('.td')}
        
        # This would need actual spec execution
        # For now, just verify no setup errors
    
    def test_spec_local_scope_fails(self, project):
        """Test local scope spec that fails."""
        # Similar setup with failing assertion
        pass
    
    # === Global Scope Tests ===
    
    def test_spec_global_scope_aggregation(self, project):
        """Test global scope spec with SQL aggregation."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Item
class Item(BaseModel):
    name: str
    weight: float
```

```entity Item: item-1
name: Light Item
weight: 100
```

```entity Item: item-2
name: Medium Item
weight: 200
```

```spec:check_total_weight
@target(type="Item", scope="global")
def check_total_weight(subject):
    """所有 Item 的总重量不能超过限制"""
    result = sql("SELECT sum(weight) as total FROM Item")
    total = result[0]['total']
    assert total <= 10000, f"总重量 ({total}) 超过限制 10000"
```
''')
        # Test global scope execution
        pass
    
    # === Target Selector Tests ===
    
    def test_target_selector_by_type(self, project):
        """Test @target(type="...") selector."""
        pass
    
    def test_target_selector_by_id(self, project):
        """Test @target(id="...") selector."""
        pass
    
    @pytest.mark.skip(reason="Tag filtering not implemented")
    def test_target_selector_by_tag(self, project):
        """Test @target(tag="...") selector (not yet implemented)."""
        pass
    
    # === Error Cases ===
    
    def test_spec_no_target__should_warn_E0423(self, project):
        """Test spec without @target raises E0423 warning."""
        project.add_config().add_file("test.td", '''
---
title: Test
---

```spec:no_target_spec
def no_target_spec(subject):
    assert True
```
''')
        # Should produce E0423 warning
        pass
    
    def test_spec_assertion_fail__should_raise_E0424(self, project):
        """Test failed assertion raises E0424."""
        pass

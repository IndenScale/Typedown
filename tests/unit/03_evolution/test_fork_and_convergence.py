"""
Test: Fork Detection and Convergence
Related Doc: docs/zh/02_concepts/03_evolution.md Section "散敛规则"

Known Issue: These features are documented but not fully implemented.
"""

import pytest


class TestForkDetection:
    """Test detection of evolution fork (one ID becoming former of two entities).
    
    Doc: "演变分叉（错误）：一个 ID 不能成为两个不同实体的 former，时间线不可分裂"
    """
    
    @pytest.mark.skip(reason="Fork detection not implemented")
    def test_fork_should_be_detected(self, project):
        """Test that creating a fork raises an error."""
        # This should fail according to the doc
        project.add_config().add_file("test.td", '''
---
title: Test
---

```model:Feature
class Feature(BaseModel):
    status: str
```

```entity Feature: base-v1
status: base
```

```entity Feature: branch-a
former: [[base-v1]]
status: branch-a-status
```

```entity Feature: branch-b
former: [[base-v1]]
status: branch-b-status
```
''')
        # Should detect that base-v1 is former of both branch-a and branch-b
        # This is currently NOT implemented
        pass


class TestConvergence:
    """Test evolution convergence (multiple formers merging).
    
    Doc: "演变收敛：多个旧版本可以合并为一个新版本，但需谨慎处理语义冲突"
    """
    
    @pytest.mark.skip(reason="Convergence semantics not fully implemented")
    def test_convergence_multiple_formers(self, project):
        """Test merging multiple entities into one."""
        # This is allowed by the doc but semantics are complex
        pass
    
    @pytest.mark.skip(reason="Conflict detection not implemented")
    def test_convergence_conflict_detection(self, project):
        """Test detection of semantic conflicts in convergence."""
        pass

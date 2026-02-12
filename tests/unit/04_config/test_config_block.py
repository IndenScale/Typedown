"""
Test: Config Block Syntax and Execution
Related Doc: docs/zh/02_concepts/04_config.md Section "1. Config 代码块"
Error Codes: E0102 (Config block location error), E0222 (Config execution failed)
"""

from typedown.core.base.errors import ErrorCode
from tests.conftest import assert_error_exists, assert_no_errors


class TestConfigBlock:
    """Test config block functionality."""
    
    # === Success Cases ===
    
    def test_config_python_syntax(self, project):
        """Test config python block execution."""
        project.add_file("config.td", '''
---
title: Root Config
---

```config python
import sys
TEST_VAR = "loaded"
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_no_errors(scan_diag)
        assert_no_errors(link_diag)
    
    def test_config_default_python(self, project):
        """Test config block defaults to python."""
        project.add_file("config.td", '''
---
title: Config
---

```config
DEFAULT_VALUE = 42
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_no_errors(link_diag)
    
    def test_config_sets_sys_path(self, project):
        """Test that config can modify sys.path."""
        project.add_file("config.td", '''
---
title: Config
---

```config python
import sys
sys.path.append("${ROOT}/scripts")
```
''')
        # Should execute without error
        scan_diag, link_diag, _ = project.compile()
        
        assert_no_errors(link_diag)
    
    def test_config_defines_global_variables(self, project):
        """Test that config variables are available in models."""
        project.add_file("config.td", '''
---
title: Config
---

```config python
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
```
''').add_file("model.td", '''
---
title: Model
---

```model:Service
class Service(BaseModel):
    timeout: int = Field(default=DEFAULT_TIMEOUT)
    retries: int = Field(default=MAX_RETRIES)
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_no_errors(link_diag)
    
    # === Error Cases ===
    
    def test_config_in_wrong_file__should_raise_E0102(self, project):
        """Test that config block in non-config.td file raises E0102."""
        project.add_file("regular.td", '''
---
title: Regular File
---

```config python
# This should not be here
```
''')
        scan_diag, _, _ = project.compile()
        
        assert_error_exists(scan_diag, ErrorCode.E0102)
    
    def test_config_execution_error__should_raise_E0222(self, project):
        """Test that config execution error raises E0222."""
        project.add_file("config.td", '''
---
title: Config
---

```config python
# This will fail
raise ValueError("Config error")
```
''')
        scan_diag, link_diag, _ = project.compile()
        
        assert_error_exists(link_diag, ErrorCode.E0222)

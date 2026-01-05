---
title: Environment Config
---

# Environment Config (Config)

The `config` block is used to configure the compiler's runtime environment. It is typically used to import common libraries, set global variables, or modify system paths.

## Syntax Signature

```markdown
```config:python
<Setup Script>
```
```

- **Keyword**: `config`
- **Language**: Currently only `python` is supported.
- **Location Restriction**: Usually allowed only in `config.td` files.

## Scope

`config` blocks take effect at the **directory level**.
Configuration defined in `config.td` applies to all files in that directory and its subdirectories (unless overridden by a `config.td` in a subdirectory).

## Common Uses

### 1. Import Common Modules

```python
import sys
import datetime
from typing import List, Optional

# Add project source directory to path to import custom Python tool libraries
sys.path.append("${ROOT}/scripts")
```

### 2. Define Global Variables

Variables defined in a `config` block can be used directly in `model` or `spec` blocks in the same directory.

```python
# config.td
DEFAULT_TIMEOUT = 30
```

```python
# model.td
class Service(BaseModel):
    timeout: int = Field(default=DEFAULT_TIMEOUT)
```

## Execution Timing

Config blocks are executed **before the parsing phase**. This means they prepare the environment for subsequent Model definitions and Entity instantiation.

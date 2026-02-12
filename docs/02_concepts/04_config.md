---
title: Configuration System
---

# Configuration System

Typedown provides two layers of configuration: **config code blocks** (directory-level) and **Front Matter** (file-level).

## 1. Config Code Blocks

`config` code blocks are used to configure the compiler's runtime environment, typically appearing in `config.td` files.

### Syntax

````typedown
```config python
<Setup Script>
```
````

- **Keyword**: `config`
- **Language**: Currently only supports `python`
- **Location restriction**: Usually only allowed in `config.td` files

### Scope

`config` blocks take effect at the **directory level**. Configuration defined in `config.td` applies to all files in that directory and its subdirectories (unless overridden by a subdirectory's `config.td`).

### Common Uses

#### Import Common Modules

```python
import sys
import datetime
from typing import List, Optional

# Add project source directory to path
sys.path.append("${ROOT}/scripts")
```

#### Define Global Variables

```python
# config.td
DEFAULT_TIMEOUT = 30
```

```python
# model.td
class Service(BaseModel):
    timeout: int = Field(default=DEFAULT_TIMEOUT)
```

### Execution Timing

Config blocks execute **before the parsing phase**, preparing the environment for Model definitions and Entity instantiation.

---

## 2. Front Matter

Typedown files support standard YAML Front Matter at the beginning of the file, used to define file-level metadata and shortcut scripts.

### Syntax

```yaml
---
title: Document Title
tags: [api, v2]
scripts:
  validate: 'typedown check --full ${FILE}'
---
```

### Standard Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | `str` | Document title |
| `tags` | `List[str]` | Document tags, can be used for query filtering |
| `author` | `str` | Document author |
| `order` | `int` | Directory sorting priority |

### Script Definitions

```yaml
scripts:
  # Override default validation command
  validate: 'typedown check --full ${FILE}'
  
  # Custom test command
  test-api: 'pytest tests/api_test.py --target ${entity.id}'
  
  # Composite command
  ci-pass: 'typedown check --full ${FILE} && typedown run test-api'
```

### Environment Variables

Variables available in scripts:

| Variable | Description |
|----------|-------------|
| `${FILE}` | Current file absolute path |
| `${DIR}` | Current directory absolute path |
| `${ROOT}` | Project root directory |
| `${FILE_NAME}` | Filename without extension |
| `${TD_ENV}` | Current environment (local, ci, prod) |

### Scope Inheritance

Script parsing follows the **nearest priority** principle:

1. **File-level**: Current file Front Matter (highest priority)
2. **Directory-level**: Current directory `config.td` Front Matter
3. **Project-level**: Root directory `typedown.yaml` global configuration

---

## Configuration Priority

| Level | Scope | Priority |
|-------|-------|----------|
| Front Matter | File-level | Highest |
| config.td | Directory-level | Medium |
| typedown.yaml | Project-level | Lowest |

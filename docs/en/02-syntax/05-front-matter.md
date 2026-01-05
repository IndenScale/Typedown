---
title: File Metadata
---

# File Metadata (Front Matter)

Typedown files support standard YAML Front Matter, located at the very beginning of the file. It is used to define file-level metadata and shortcut scripts.

## Syntax

```yaml
---
key: value
scripts:
  ...
---
```

## Standard Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| **title** | `str` | Document title, used for generating sidebars or indices. |
| **tags** | `List[str]` | Document tags, can be used for query filtering. |
| **author** | `str` | Document author. |
| **order** | `int` | Sort priority in the directory. |

## Scripts

The `scripts` field is used to define operations specific to the file.

```yaml
scripts:
  # Override default validation command
  validate: "td validate --strict ${FILE}"
  
  # Custom test command
  test-api: "pytest tests/api_test.py --target ${entity.id}"
```

### Environment Variables

The following variables can be used in script commands:

- `${FILE}`: Absolute path of the current file.
- `${DIR}`: Absolute path of the current directory.
- `${ROOT}`: Project root directory.

---
title: File Metadata
---

# File Metadata

Typedown files support standard YAML Front Matter, located at the very beginning of the file. It is used to define file-level metadata.

## Syntax

```yaml
---
key: value
---
```

## Standard Fields

| Field      | Type        | Description                                              |
| :--------- | :---------- | :------------------------------------------------------- |
| **title**  | `str`       | Document title, used for generating sidebars or indices. |
| **tags**   | `List[str]` | Document tags, can be used for query filtering.          |
| **author** | `str`       | Document author.                                         |
| **order**  | `int`       | Sort priority in the directory.                          |

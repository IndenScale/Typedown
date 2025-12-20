# RFC 007: Scripts & Configuration

## Summary

This RFC formalizes the project configuration file `typedown.toml` and introduces the `[scripts]` section. Scripts serve as **Compilation Presets**, allowing developers to define reproducible build/test scopes and execution modes (Context vs. Strict) for different workflows.

## 1. Manifest File: `typedown.toml`

The root of every Typedown project MUST contain a `typedown.toml` file. This file serves as the single source of truth for project metadata, dependencies, and build configuration.

### 1.1 Standard Structure

```toml
[package]
name = "my-rpg-system"
version = "0.1.0"
description = "A core rulebook for the RPG system."
authors = ["Alice <alice@example.com>"]

[scripts]
# Defined below in Section 2

[linker]
# Symbols to implicitly load into every file's scope
prelude = [
    "std.math",
    "models.common.BaseEntity"
]

[dependencies]
# External dependencies (Future scope: Git/Registry)
standard_lib = { path = "../stdlib" }
```

## 2. Scripts (Compilation Presets)

Scripts are named configurations that control the **Compiler Scope** and **Execution Filters**. They replace complex, repetitive CLI arguments.

### 2.1 Definition Syntax

Define scripts under the `[scripts]` table.

```toml
[scripts]
# Key is the script name invoked via `td test :key`
core_tests = { include = ["src/core"], tags = ["critical"] }

# Full validation with strict isolation
api_stable = { include = ["src/api"], strict = true }
```

### 2.2 Configuration Fields

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **`include`** | `List[Glob]` | `["**"]` | The **Target Set** of files to fully Scan, Link, Validate, and Execute. |
| **`exclude`** | `List[Glob]` | `[]` | Patterns to explicitly ignore within the `include` set. |
| **`strict`** | `Boolean` | `false` | If `true`, disables the **Global Context**. References to files outside `include` will fail. If `false`, the compiler performs a shallow scan of the whole project to resolve references (Context Set). |
| **`tags`** | `List[Str]` | `[]` | Only run `spec` blocks marked with these Pytest markers. |
| **`tags_exclude`**| `List[Str]` | `[]` | Skip `spec` blocks with these markers. |

## 3. Scope Logic

### 3.1 The "Context" Concept

One of the biggest challenges in modular builds is **Cross-Module References**.
*   **Scenario**: `src/features/login.td` references `[[User]]` defined in `src/core/user.td`.
*   **Task**: Run tests *only* for `src/features`.

**Default Behavior (`strict = false`)**:
1.  **Target Scope**: `src/features` (Validation + Execution).
2.  **Context Scope**: Everything else (Symbol Indexing only).
3.  **Result**: `[[User]]` resolves correctly. Tests in `src/core` are NOT run.

**Strict Mode (`strict = true`)**:
1.  **Target Scope**: `src/features`.
2.  **Context Scope**: None (or explicitly defined dependencies).
3.  **Result**: `[[User]]` is a **Dangling Reference Error**.

## 4. CLI Usage

Scripts are invoked using the colon syntax:

```bash
td test :script_name
```

This is equivalent to manually passing all the include/exclude/tag flags to the compiler.

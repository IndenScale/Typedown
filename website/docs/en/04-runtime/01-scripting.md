---
title: Script System
---

# Script System

Typedown's script system allows defining operational logic within the Front Matter of `.td` files, transforming static documentation into executable units.

## 1. Core Mechanism

Scripts are defined in the file's Front Matter.

### Definition Method

```yaml
---
# Define actions specific to this file
scripts:
  # Override standard action: validate current file logic
  validate: "td validate --strict ${FILE}"

  # Custom action: connect to business bureau API to verify data
  verify-business: "python scripts/oracle_check.py --id ${entity.id}"

  # Combined action
  ci-pass: "td validate ${FILE} && td run verify-business"
---
```

## 2. Scoping and Inheritance

Script resolution follows the **Nearest Winner** principle, implementing hierarchical inheritance of configuration:

1. **File Scope**: Front Matter of the current file. Highest priority, overrides scripts with the same name.
2. **Directory Scope**: `config.td` of the current directory (or nearest parent directory).
   - **Note**: Must be defined in the **Front Matter** of `config.td`, not in a code block.
   - Applies to all files under that directory.
3. **Project Scope**: `typedown.yaml` in the root directory. Defines global default behaviors.

## 3. Environment Variable Injection

The runtime environment automatically injects context variables, empowering scripts to be environment-aware:

- `${FILE}`: Absolute path of the current file.
- `${DIR}`: Absolute path of the directory containing the current file.
- `${ROOT}`: Project root directory.
- `${FILE_NAME}`: File name without extension.
- `${TD_ENV}`: Current runtime environment (local, ci, prod).

## 4. Command Line Interaction

Users invoke these scripts through a unified interface, without needing to memorize complex underlying commands.

```bash
# Execute the validate script of the current file
$ td run validate user_profile.td

# Batch execute test scripts for all files in the specs/ directory
$ td run test specs/
```

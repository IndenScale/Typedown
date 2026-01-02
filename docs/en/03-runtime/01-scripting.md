# Script System

Typedown's core philosophy transforms static documents into executable intelligent units via **Scripts**. This is a First-Class Citizen of the Typedown runtime.

## 1. Core Mechanism

The script system allows defining operation logic within the Front Matter of `.td` files. This makes each file not just a carrier of data, but an **object** with behavior.

### Definition

```yaml
---
# Define actions exclusive to this file
scripts:
  # Override standard action: validate current file logic
  validate: "td validate --strict ${FILE}"

  # Custom action: Connect to business registry API to verify data
  verify-business: "python scripts/oracle_check.py --id ${entity.id}"

  # Composed action
  ci-pass: "td validate ${FILE} && td run verify-business"
---
```

## 2. Scoping and Inheritance

Script resolution follows the **Nearest Winner** principle, implementing hierarchical configuration inheritance:

1. **File Scope**: Front Matter of the current file. Highest priority, overrides scripts with the same name.
2. **Directory Scope**: `config.td` in the current directory (or nearest parent directory).
   - **Note**: Must be defined in the **Front Matter** of `config.td`, not in code blocks.
   - Applies to all files under that directory.
3. **Project Scope**: `typedown.yaml` in the root directory. Defines global default behaviors.

## 3. Environment Variable Injection

The runtime environment automatically injects context variables, empowering scripts with environmental awareness:

- `${FILE}`: Absolute path of the current file.
- `${DIR}`: Absolute path of the directory containing the current file.
- `${ROOT}`: Project root directory.
- `${FILE_NAME}`: Filename without extension.
- `${TD_ENV}`: Current running environment (local, ci, prod).

## 4. CLI Interaction

Users invoke these scripts through a unified interface without needing to memorize complex underlying commands.

```bash
# Execute the validate script of the current file
$ td run validate user_profile.td

# Batch execute test scripts for all files in the specs/ directory
$ td run test specs/
```

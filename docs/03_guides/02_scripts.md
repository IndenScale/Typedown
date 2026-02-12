---
title: Script System
---

# Script System

Typedown's script system allows defining operational logic in `.td` file Front Matter, transforming static documents into executable units.

## Defining Scripts

Define in file Front Matter:

```yaml
---
scripts:
  # Override standard action: validate current file
  validate: 'typedown check --full ${FILE}'
  
  # Custom action
  verify-api: 'pytest tests/api.py --id ${entity.id}'
  
  # Composite action
  ci-pass: 'typedown check --full ${FILE} && typedown run verify-api'
---
```

## Scope and Inheritance

Script parsing follows the **nearest principle**:

1. **File-level**: Current file Front Matter (highest priority)
2. **Directory-level**: Current directory `config.td` Front Matter
3. **Project-level**: Root directory `typedown.yaml`

## Environment Variables

| Variable | Description |
|----------|-------------|
| `${FILE}` | Current file absolute path |
| `${DIR}` | Current directory absolute path |
| `${ROOT}` | Project root directory |
| `${FILE_NAME}` | Filename without extension |
| `${TD_ENV}` | Current environment (local, ci, prod) |

## Command Line Invocation

```bash
# Execute file's validate script
typedown run validate user_profile.td

# Batch execute test scripts for all files in directory
typedown run test specs/
```

## Common Script Patterns

### CI/CD Check

```yaml
scripts:
  ci: 'typedown check --json | tee typedown-report.json'
```

### Data Export

```yaml
scripts:
  export: 'typedown export ${FILE} --format json > output.json'
```

### External Validation

```yaml
scripts:
  verify-oracle: 'python scripts/check_external.py --ref ${entity.id}'
```

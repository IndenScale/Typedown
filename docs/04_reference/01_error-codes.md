---
title: Error Codes
---

# Error Code Reference

## Format Description

Error code format: `E{stage}{category}{number}`

- **Stage** (2nd-3rd digits): Compilation stage
  - `01` = L1 Scanner
  - `02` = L2 Linker
  - `03` = L3 Validator
  - `04` = L4 Spec
  - `09` = System

- **Category** (4th digit): Error category
  - `0-1` = Syntax/Parse
  - `2-3` = Execution
  - `4-5` = Reference/Link
  - `6-7` = Schema/Type
  - `8-9` = System

- **Number** (5th digit): Sequence number (1-9)

## Error Levels

- **Error**: Critical error, blocks execution
- **Warning**: Potential issue, execution continues
- **Info**: Informational message
- **Hint**: Improvement suggestion

## Error Code List

### L1: Scanner (E01xx)

| Code | Level | Description |
|------|-------|-------------|
| E0101 | Error | Syntax parse failed |
| E0102 | Error | Config block location error (config can only be in config.td) |
| E0103 | Error | Nested list anti-pattern |
| E0104 | Error | File read error |
| E0105 | Error | Document structure error |

### L2: Linker (E02xx)

| Code | Level | Description |
|------|-------|-------------|
| E0221 | Error | Model execution failed |
| E0222 | Error | Config execution failed |
| E0223 | Warning | Prelude symbol loading failed |
| E0224 | Warning | Model rebuild failed |
| E0231 | Error | Model block ID does not match class name |
| E0232 | Error | Model uses reserved field 'id' |
| E0233 | Error | Invalid model type |
| E0241 | Error | Duplicate ID definition |

### L3: Validator (E03xx)

| Code | Level | Description |
|------|-------|-------------|
| E0341 | Error | Reference resolution failed |
| E0342 | Error | Circular dependency detected |
| E0343 | Error | Evolution target not found |
| E0361 | Error | Schema validation failed |
| E0362 | Error | Ref[T] type mismatch |
| E0363 | Error | ID conflict |
| E0364 | Error | Model class not found |
| E0365 | Error | Query syntax error |

### L4: Spec (E04xx)

| Code | Level | Description |
|------|-------|-------------|
| E0421 | Error | Spec execution failed |
| E0422 | Error | Oracle execution failed |
| E0423 | Warning | Spec target not found |
| E0424 | Error | Spec assertion failed |

### System (E09xx)

| Code | Level | Description |
|------|-------|-------------|
| E0981 | Error | Internal compiler error |
| E0982 | Error | File system error |
| E0983 | Error | Configuration error |

## CI/CD Integration

```bash
# Check and output JSON
typedown check --json

# Filter specific error codes
typedown check --json | jq '.diagnostics[] | select(.code == "E0103")'

# Count errors by stage
typedown check --json | jq '.summary.by_stage'
```

---
title: Quality Control
---

# Quality Control

Typedown's quality control system is divided into four layers, ranging from low-level syntax validation to high-level external fact verification.

## 1. QC Hierarchy Model

```mermaid
graph TD
    L1[L1: Syntax] -->|Pass| L2[L2: Schema Check]
    L2 -->|Pass| L3[L3: Internal Logic]
    L3 -->|Pass| L4[L4: External Verification]
```

### L1: Syntax & Format

- **Command**: `td lint`
- **Timing**: Editing / Pre-commit
- **Checks**:
  - Markdown AST structure validity.
  - YAML format correctness (indentation, special characters).
  - **Does not load Python environment**.

### L2: Schema Compliance

- **Command**: `td check`
- **Timing**: Editing / Save
- **Core Engine**: Pydantic Runtime
- **Checks**:
  - Load `model` definitions.
  - Instantiate `entity`. Execute all Pydantic native validations:
    - Type Checking.
    - Field Validators (`@field_validator`).
    - Model Validators (`@model_validator`).
    - Computed Fields (`@computed_field`).
    - Reference Format validation.
  - **Boundary**: Ensures data is "structurally" perfect. **Does not run Specs**.

### L3: Business Logic

- **Command**: `td validate` (Defaults to include L1+L2)
- **Timing**: Compile time / Before Build
- **Core Engine**: Typedown Runtime + Spec System
- **Checks**:
  - **Graph Resolution**: Ensures all references point to existing entities.
  - **Selector Binding**: Run `spec` blocks.
  - **Complex Rules**: Validate cross-entity constraints or complex domain-specific rules.
  - **Goal**: Internal Consistency. **Never** initiates network requests.

### L4: External Verification

- **Command**: `td test`
- **Timing**: CI / Release
- **Core Engine**: Oracles
- **Checks**:
  - **Oracle Interaction**: Call external oracles (Government API, CRM, DNS, etc.).
  - **Reality Check**: Verify consistency between data and the real world.
  - **Goal**: External Consistency. **Has side effects**.

## 2. Isolation Principle

To ensure development efficiency and local safety, Typedown strictly enforces **Environment Isolation**:

- **Fast Loop (L1/L2)**: Purely local, millisecond-level response. IDE plugins should execute in real-time.
- **Safe Loop (L3)**: Purely local, second-level response. Mandatory before build and commit.
- **Trusted Loop (L4)**: Executed only in trusted environments (CI/CD) or with explicit authorization. Involves external interaction.

## 3. Standard Build

In addition to the validation hooks above, Typedown defines a `build` hook for artifact generation.

- **Command**: `td build`
- **Responsibility**: Idempotently output JSON Schema, SQL, HTML, and other deliverables.
- **Precondition**: Usually requires passing L3 (validate) checks.

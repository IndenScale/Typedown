---
title: Introduction
---

# Typedown

> **Markdown Type System**

**Typedown** is a structured documentation tool based on Markdown, designed to transform loose text into structured data through a semantic layer.

## Why Typedown?

Markdown is the universal standard for technical documentation, but three types of errors are inevitable at scale:

| Error Type | Problem Description | Typedown Solution |
|------------|---------------------|-------------------|
| **Schema Errors** | Inconsistent data formats: `Status: Active` vs `status: active`, missing required fields | **Model** - Define data structures with Pydantic, validate at compile time |
| **Broken References** | Link rot: `[[./old-path]]` points to non-existent locations after moving files | **Reference** - Content-hash-based addressing, automatically track entity changes |
| **Business Logic Violations** | Rules broken: admin without MFA enabled, inventory exceeding limits | **Spec** - Executable business rules, real-time validation of complex constraints |

Through these three semantic layers, Typedown transforms Markdown from "loose text" into a "verifiable knowledge base".

## Core Concepts

### 1. Structure (Schema)

Define data structures using Python (Pydantic):

````typedown
```model:User
class User(BaseModel):
    name: str
    role: Literal["admin", "member"]
```
````

### 2. Space (Graph)

Establish links between entities using **ID** or **content hash**:

```typedown
This report was written by [[user-alice-v1]].
```

### 3. Logic (Validation)

Three-layer validation, from single fields to global aggregation:

````typedown
# 1. Field-level - @field_validator
class User(BaseModel):
    @field_validator('email')
    def check_email(cls, v):
        assert '@' in v, "Invalid email format"
        return v

# 2. Model-level - @model_validator
class Order(BaseModel):
    @model_validator(mode='after')
    def check_dates(self):
        assert self.end > self.start, "End time must be later than start"
        return self

# 3. Global-level - spec
```spec:check_inventory
@target(type="Item", scope="global")
def check_total_weight(subject):
    total = sql("SELECT sum(weight) FROM Item")[0]['total']
    assert total <= 10000, "Total weight exceeds limit"
```
````

## Installation

### VS Code Extension (Recommended)

- [**VS Code Marketplace**](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)
- [**Open VSX**](https://open-vsx.org/extension/Typedown/typedown-vscode)

### CLI Tool

```bash
# Run instantly (no installation needed)
uvx typedown check

# Global installation
uv tool install typedown
```

### Developers

```bash
git clone https://github.com/IndenScale/typedown.git
```

## Next Steps

👉 [Quick Start Tutorial](./tutorial) - Build your first model

---
title: Model Definition
---

# Model Definition (Model)

The `model` block is used to define the structure (Schema) of data. It is the cornerstone of the Typedown system, determining the shape and constraints that entities must follow.

## Syntax Signature

```markdown
```model:<ClassName>
class <ClassName>(BaseModel):
    ...
```
```

- **Keyword**: `model`
- **Identifier**: `<ClassName>` must match the Pydantic class name defined inside the code block exactly.
- **Content**: Standard Python code, with `pydantic`, `typing`, `typedown.types` and other base libraries preloaded.

## Pydantic Integration

Typedown's model layer is built entirely on top of [Pydantic V2](https://docs.pydantic.dev/). You can use all features of Pydantic:

### Basic Fields

```python
class User(BaseModel):
    name: str
    age: int = Field(..., ge=0, description="Age must be non-negative")
    is_active: bool = True
    tags: List[str] = []
```

### Validators

You can use `@field_validator` and `@model_validator` to define more complex constraints.

```python
class Order(BaseModel):
    item_id: str
    quantity: int
    price: float

    @field_validator('quantity')
    @classmethod
    def check_qty(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v
```

## Reference Types

Typedown introduces a special generic `Reference[T]` to handle links between entities. This is the key to building a knowledge graph.

### Single Type Reference

```python
class Task(BaseModel):
    # assignee must point to an entity of type User
    assignee: Reference["User"]
```

### Polymorphic Reference (Union Reference)

```python
class AccessLog(BaseModel):
    # subject can be User or ServiceAccount
    subject: Reference["User", "ServiceAccount"]
```

### Self Reference

```python
class Node(BaseModel):
    parent: Optional[Reference["Node"]] = None
```

> **Note**: When defining a Reference, if the target type is not yet defined (or defined later), please use the string form of Forward Reference (e.g., `"User"`).

## Scope

- Classes defined in a `model` block are registered in the **current file**'s symbol table.
- If you need to reuse the model in other files, that file must be located in the same directory or a subdirectory (following lexical scoping rules).

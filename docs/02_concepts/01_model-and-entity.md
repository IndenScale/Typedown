---
title: Model and Entity
---

# Model and Entity

Typedown's data layer consists of two core concepts: **Model** defines structure, **Entity** carries data.

## Code Block Signature Specification

> **Signature Strictness Requirements**
>
> - **Signature Consistency**: Code block ID must **exactly match** the internal class/function name
> - **Character Restrictions**: ID can only contain letters, numbers, underscores `_`, hyphens `-`, and dots `.`
> - **Whitespace Insensitive**: `model:User`, `model : User`, `model: User` are equivalent

## Model

`model` code blocks define data structures and are the foundation of the Typedown system.

### Syntax

````typedown
```model:<ClassName>
class <ClassName>(BaseModel):
    ...
```
````

### Pydantic Integration

Based on [Pydantic V2](https://docs.pydantic.dev/), supports all native features:

```python
class User(BaseModel):
    name: str
    age: int = Field(..., ge=0, description="Age must be non-negative")
    is_active: bool = True
    tags: List[str] = []
```

### Validators

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

### Reference Types

Use `Ref[T]` to establish relationships between entities:

```python
class Task(BaseModel):
    # Single type reference
    assignee: Ref["User"]
    
    # Polymorphic reference
    subject: Ref["User", "ServiceAccount"]
    
    # Self-reference
    parent: Optional[Ref["Node"]] = None
```

> **Note**: Use string-based forward references `"User"` to avoid circular dependencies.

### Import Restrictions

`model` blocks **forbid explicit imports**, only preloaded symbols can be used:
- All core `pydantic` classes
- Common `typing` generics
- Typedown-specific types like `Ref`

Complex logic should be moved to `spec` blocks.

---

## Entity

`entity` code blocks are the primary way to instantiate data; each entity is a node in the knowledge graph.

### Syntax

````typedown
```entity <TypeName>: <SystemID>
<YAML Body>
```
````

- **TypeName**: Must be a Model class name defined in the current context
- **SystemID**: Globally unique identifier (primary key)

### ID Rules

- **Character Restrictions**: Only letters, numbers, `_`, `-`, `.` allowed
- **Naming Style**: Recommend using `slug-style` (e.g., `user-alice-v1`)
- **Global Uniqueness**: Must be unique across the entire project

### Body (YAML)

Uses **strict YAML** format:

```yaml
name: 'Alice'
age: 30
role: 'admin'
```

### Reference Syntactic Sugar

`List[Ref[T]]` fields support simplified list syntax:

```yaml
# Model: friends: List[Ref[User]]
friends:
  - [[bob]]
  - [[charlie]]

# Inline style
reviewers: [[[bob]], [[alice]]]
```

The compiler automatically parses `[[bob]]` into a `Ref` object.

### Evolution Declaration

Use the `former` field to declare historical versions:

```yaml
former: [[user-alice-v0]]
name: 'Alice (Updated)'
```

See [Evolution Semantics](./evolution) for details.

---

## Scope

- Model classes are registered in the **current file's** symbol table
- To reuse in other files, the target file must be in the same directory or subdirectory (lexical scope rules)

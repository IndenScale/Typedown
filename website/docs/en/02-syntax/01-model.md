# Model Definition (Model)

The `model` block is used to define the structure (Schema) of data. It is the cornerstone of the Typedown system, determining the shape and constraints that entities must follow.

## Syntax Signature (Block Signature)

````typedown
```model:<ClassName>
class <ClassName>(BaseModel):
    ...
```
````

### Signature Strictness Requirements

In version v0.2.13+, Typedown has strengthened the block signature validation logic:

- **Signature Consistency**: The **Block ID** (`ClassName`) must **exactly match** the Pydantic class name defined on the first line of the Python code within the block. This ensures a strong binding between the document structure and code logic.
- **ID Character Restrictions**: Identifiers are only allowed to contain letters, numbers, underscores `_`, and hyphens `-` (regex: `[a-zA-Z0-9_\-]+`).
- **Space Insensitivity**: Spaces between the keyword `model` and the colon `:`, and between the colon and the ID, are no longer sensitive. For example, `model:User`, `model : User`, and `model: User` are all considered equivalent and compliant.

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

## Import Restrictions

To ensure the purity and portability of the data schema, `model` blocks enforce **strict import restrictions**:

- **No explicit `import`**: You cannot use `import` statements within a `model` block.
- **Preloaded Environment**: Typedown automatically injects common symbols for you:
  - All core `pydantic` classes (e.g., `BaseModel`, `Field`).
  - Frequently used generics from `typing` (e.g., `List`, `Optional`, `Dict`, `Union`).
  - Typedown-specific types (e.g., `Reference`).

If some logic is too complex and requires external libraries, move it to a `spec` block or consider using specific injection mechanisms in `config.td` (if supported).

## Scope

- Classes defined in a `model` block are registered in the **current file**'s symbol table.
- If you need to reuse the model in other files, that file must be located in the same directory or a subdirectory (following lexical scoping rules).

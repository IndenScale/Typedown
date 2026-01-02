# Core Blocks

Typedown enhances Markdown's Code Blocks, treating them as semantic containers. these blocks are the fundamental units for building the Typedown language.

## 1. Model Blocks (`model`)

The `model` block allows you to define data schemas directly within the document using Pydantic syntax. This implements "Progressive Formalization"—evolving from loose textual descriptions to strict type definitions.

````markdown
```model:UserAccount
class UserAccount(BaseModel):
    name: str
    age: int = Field(..., ge=0)
    # Use Reference[T] to define relationships
    manager: Optional[Reference["UserAccount"]] = None
    friends: List[Reference["UserAccount"]] = []
```
````

- **Runtime Environment**: Executed in a Python environment pre-installed with `pydantic` and `typing`.
- **Scope**: Models defined here are registered to the file's local scope. The ID currently after the colon (e.g., `UserAccount`) serves as the primary identifier for the model.
- **Naming Constraint**: To ensure parser efficiency, the ID in the Info String **MUST** exactly match the Pydantic class name defined inside the code block. See [03-identifiers.md](03-identifiers.md) for details.

## 2. Entity Blocks (`entity`)

The `entity` block is the primary way to declare "data" in Typedown. We adopt a strategy of separating **Handle** and **Logical ID**.

````markdown
<!-- UserAccount is the type reference, alice is the instance Handle -->

```entity UserAccount: alice
# 1. Logical ID (Slug): Explicitly defined business primary key for version evolution (former)
id: "users/alice-v1"

# 2. Body: Standard YAML format
name: "Alice"
age: 30

# 3. Reference Syntax Sugar: Looks like a reference list, compiler automatically unboxes
friends:
  - [[bob]]
  - [[charlie]]
```
````

- **Syntax**: `entity <Type>: <Handle>`.
- **Identifier System**:
  - **Handle**: The `alice` in the code block header is a local handle.
  - **Slug**: The `id: "..."` inside the code block is a global logical ID.
  - See [03-identifiers.md](03-identifiers.md) for more details.
- **Body**: **Strict YAML**.
- **Data Constraints**:
  - **No Nested Lists**: Due to the smart unboxing mechanism, Typedown **strictly prohibits the use of two-dimensional arrays** (List of Lists) in entity definitions. This is considered an anti-pattern indicating that the data structure should be encapsulated as an independent Model.

## 3. Config Blocks (`config`)

The `config` block is used to dynamically configure the compilation context, typically found in `config.td` files.

````markdown
```config:python
import sys
# Inject path
sys.path.append("./src")
```
````

- **Execution Timing**: Executed during the "Linking Phase".
- **Function**: Exports Python symbols for use by `model` or `spec` blocks in the same directory.

## 4. Spec Blocks (`spec`)

The `spec` block contains test logic. We uniformly use the colon syntax to define specifications and their IDs.

````markdown
```spec:check_adult
# Declaration: This test automatically applies to all entities of type UserAccount
@target(type="UserAccount")
def validate_age(subject: UserAccount):
    # Assert directly against the single instance; subject is the parsed instance
    assert subject.age >= 18, f"User {subject.name} applies underage"
```
````

- **Syntax**: `spec:<Details>`. `Details` is the **Handle** for this specification.
- **@target Decorator**: Declares the scope of entities this logic applies to (supports filtering by Type or Tag).
- **Parameter Injection**: The runtime automatically finds matching entities and injects them one by one into the `subject` parameter for execution.

## 5. Front Matter

Typedown files support standard YAML Front Matter for defining file-level metadata and shortcut scripts.

```yaml
---
tags: [documentation, core]
# Define local shortcut scripts
scripts:
  test: "td test --tag=core"
  lint: "td lint ."
---
```

- **Metadata**: Metadata like `tags`, `author` can be indexed by the query system.
- **Scripts**: Defines shortcut commands capable of running in this context, invoked via `td run <script_name>`.

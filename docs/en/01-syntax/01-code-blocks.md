# Core Blocks

> **"You don't know it until you model it."**

Typedown redefines Markdown's **Code Blocks**.

In standard Markdown, code blocks are just for display. In Typedown, they are elevated to **Semantic Containers**. They act as the four pillars of system construction:

1.  **Class**: Defining data structures (`model`)
2.  **Data**: Instantiating specific objects (`entity`)
3.  **Spec**: Defining logic verification rules (`spec`)
4.  **Context**: Constructing runtime environments (`config`)

## 1. Block Signatures

To distinguish these purposes, Typedown uses the first line (Info String) of the code block as the **Block Signature**. There is no single universal format; instead, specific patterns exist for each intent:

| Container  | Keyword  | Signature Example    | Role                                      |
| :--------- | :------- | :------------------- | :---------------------------------------- |
| **Model**  | `model`  | `model:User`         | **Definition**: Wraps a Pydantic Class    |
| **Entity** | `entity` | `entity User: alice` | **Instantiation**: Wraps YAML Data        |
| **Spec**   | `spec`   | `spec:check_age`     | **Verification**: Wraps a Pytest Function |
| **Config** | `config` | `config:python`      | **Configuration**: Wraps a Setup Script   |

> **Naming Constraint**: Identifiers in signatures must strictly **avoid slashes `/` or spaces** (except for the Entity separator). **Snake_Case** or **PascalCase** is recommended.

## 2. Model Blocks (`model`)

The `model` block allows you to define data schemas directly within the document using Pydantic syntax. This implements "Progressive Formalization"—evolving from loose textual descriptions toward strict type definitions.

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
- **Scope**: Models defined here are registered to the file's local scope. The ID after the colon (e.g., `UserAccount`) serves as the primary identifier for the model.
- **Naming Constraint**: To ensure parser efficiency, the ID in the Info String **MUST** exactly match the Pydantic class name defined inside the code block. See [03-identifiers.md](03-identifiers.md) for details.

## 2. Entity Blocks (`entity`)

The `entity` block is the primary way to declare "data" in Typedown. We adopt a strategy of separating the **Handle** from the **Logical ID**.

````markdown
<!-- UserAccount is the type reference; alice is the instance Handle -->

```entity UserAccount: user-alice-v1
# 1. Signature as Identity:
# ID is injected from the Header; do not repeat 'id' in the Body.

# 2. Body: Standard YAML format
name: "Alice"
age: 30

# 3. Reference Syntax Sugar: Looks like a reference list; the compiler automatically unboxes it
friends:
  - [[bob]]
  - [[charlie]]
```
````

- **Syntax**: `entity <Type>: <Identifier>`
- **Identifier**: The `<Identifier>` after the colon is the unique index key for the block. It can follow two styles:
  - **Name Style**: e.g., `alice`. Suitable for local context, acting as an L2 Handle.
  - **Slug Style**: e.g., `user-alice-v1`. Suitable for global definition, acting directly as an L1 System ID. Please use hyphens `-` as separators.
- **Body**: Uses **Strict YAML** format to define data content.
- **Constraints**:
  - **Single Source of Truth**: Defining `id` in the Body is strictly Forbidden. The Entity's unique identifier is defined exclusively by the **Block Signature**.
  - **No Nested Lists**: Two-dimensional arrays (List of Lists) are strictly prohibited in entity definitions. Data structures should be encapsulated as independent Models.

## 3. Config Blocks (`config`)

The `config` block is used to dynamically configure the compilation context, typically found in `config.td` files.

````markdown
```config:python
import sys
# Inject path
sys.path.append("./src")
```
````

- **Execution Timing**: Executed during the "Linking Phase."
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

- **Metadata**: Metadata like `tags` and `author` can be indexed by the query system.
- **Scripts**: Defines shortcut commands capable of running in this context, invoked via `td run <script_name>`.

# Basic Syntax

Typedown uses standard Markdown syntax and extends its functionality through specific code block identifiers.

## 1. Model Definition

To support "Progressive Formalization," Typedown allows defining data models directly within Markdown documents. This is typically used during the initial or testing phases (Inception Phase).

Use the `model` tag on code blocks. The content supports standard Python syntax. You can optionally provide an `id`.

````markdown
```model id=UserAccount
class User(BaseModel):
    name: str
    age: int = Field(..., ge=0)
```
````

### Features

1. **Multi-Class Definition**: You can define multiple related classes within a single `model` block.
2. **Auto-imports**: To reduce boilerplate, the execution environment pre-loads the following symbols by default:
   - **Pydantic**: `BaseModel`, `Field`, `validator`, `model_validator`, `PrivateAttr`
   - **Typing**: `List`, `Dict`, `Optional`, `Union`, `Any`, `ClassVar`
   - **Enum**: `Enum`
3. **Override Mechanism**: Classes defined here are automatically registered to the current document's context. If a name conflicts with an existing model, the new definition overrides the old one.

Use the `entity:<ClassName>` tag. You must specify an `id` in the header.

````markdown
```entity:User id=alice
name: "Alice"
age: 30
```
````

## 3. Spec Definition (Testing & Logic)

Typedown supports two ways to define specifications or tests:

### 3.1 Python Specs (`spec` or `spec:python`)

Use standard Python code (typically Pytest functions) to verify complex logic.

````markdown
```spec id=check_user_age
def test_users_are_adults(workspace):
    users = workspace.get_entities_by_type("User")
    for user in users:
        assert user.age >= 18
```
````

### 3.2 YAML Specs (`spec` or `spec:yaml`)

Use declarative YAML to define simple rules or check execution parameters.

````markdown
```spec id=rule_evidence_required
target: Control
check: compliance.checks.has_evidence
severity: error
params:
  min_count: 1
```
````

## 4. Code Block Metadata

You can attach arbitrary metadata to any code block header using `key=value` syntax. The compiler parses these attributes and stores them in the AST.

````markdown
```entity:User id=alice status=active priority=high
...
```
````

## 5. Context Configuration

Typedown uses flexible **Executable Configuration Scripts** to manage context configuration.

In a `config.td` file (or any document), use the `config:python` tag. This script is executed before loading the document, used to inject environment variables or import models.

````markdown
# config.td

```config:python
import sys
from pathlib import Path

# 1. Inject custom library paths
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root / "src"))

# 2. Explicitly import models
# These models are automatically registered to the context of the current directory and its subdirectories
from my_app.models import Product, Order
```
````

### Auto-injection Policy

To maintain context clarity and avoid unexpected naming conflicts, Typedown **defaults to OFF** for automatically scanning and loading `.py` files in the directory.

- **Default Behavior**: Only models explicitly imported (`import`) or defined (`class ...`) within `config:python` are loaded.
- **Prelude (Global Imports)**: You can also define globally available symbols (like a standard library) in `typedown.toml` under the `[linker.prelude]` section. These symbols are automatically available in all scripts.
- **Future Expansion**: Automatic injection for specific directories may be enabled via a global CLI configuration file (e.g., `pyproject.toml`) using a whitelist/blacklist pattern.

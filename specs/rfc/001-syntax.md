# Basic Syntax

Typedown uses standard Markdown syntax and extends its functionality through specific code block identifiers.

## 1. Model Definition

To support "Progressive Formalization," Typedown allows defining data models directly within Markdown documents. This is typically used during the initial or testing phases (Inception Phase).

Use the `model` tag on code blocks. The content supports standard Python syntax but is enhanced with pre-loaded common type definitions.

````markdown
```model
# No need to manually import BaseModel, Field, List, etc.
class Address(BaseModel):
    city: str
    zip_code: str

class User(BaseModel):
    name: str
    age: int = Field(..., ge=0)
    role: str = "guest"
    address: Optional[Address] = None
```
````

### Features

1.  **Multi-Class Definition**: You can define multiple related classes within a single `model` block.
2.  **Auto-imports**: To reduce boilerplate, the execution environment pre-loads the following symbols by default:
    - **Pydantic**: `BaseModel`, `Field`, `validator`, `model_validator`, `PrivateAttr`
    - **Typing**: `List`, `Dict`, `Optional`, `Union`, `Any`, `ClassVar`
    - **Enum**: `Enum`
3.  **Override Mechanism**: Classes defined here are automatically registered to the current document's context. If a name conflicts with an existing model, the new definition overrides the old one.

## 2. Entity Instantiation

Use the `entity:<ClassName>` tag on code blocks to declare an instance of that class (data).

````markdown
# This is an Entity code block, instantiating the User class above

```entity:User
name: "Alice"
age: 30
role: "admin"
```
````

## 3. Context Configuration

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
- **Future Expansion**: Automatic injection for specific directories may be enabled via a global CLI configuration file (e.g., `pyproject.toml`) using a whitelist/blacklist pattern.

# Class Context & Imports

Typedown needs to know which Python Pydantic model corresponds to `ClassName` when `entity:ClassName` is used. We call this the **Class Context**.

To maintain speed and predictability, Typedown uses **Explicit Imports** rather than implicit directory scanning.

## 1. Global Prelude (`typedown.toml`)

For models used across the entire project, define them in the `typedown.toml` manifest under the `[linker]` section.

```toml
# typedown.toml
[linker]
# These symbols are automatically pre-loaded into every document's context
prelude = [
    "models.schema.User",       # Individual class
    "models.constants",         # Entire module
    "@lib.common.Workflow"      # Mapped dependency symbol
]
```

**Advantages**:

- **Single Source of Truth**: Centralized dependency management.
- **Zero Boilerplate**: Common models are available everywhere without extra code.
- **Performance**: Only specifically requested modules are loaded.

## 2. Directory-Level Configuration (`config.td`)

For localized requirements, use `config:python` blocks in a `config.td` file. Subdirectories inherit the context of their parent's `config.td`.

````markdown
# config.td

```config:python
# 1. Local specialized inheritance
from models.schema import Project as BaseProject

class Project(BaseProject):
    budget_code: str  # Specialized for this directory tree

# 2. Manual imports
from my_utils import Helpers
```
````

## 3. Inline Prototyping

You can define models directly within any document using a `model` block. This is ideal for rapid prototyping.

````markdown
```model id=DraftModel
class Draft(BaseModel):
    note: str
```
````

---

## Best Practices

1. **Production Models**: Keep in standard `.py` files and register via `prelude` in `typedown.toml`.
2. **Contextual Specialization**: Use `config.td` to override or extend base models for specific sub-projects.
3. **Avoid Implicit Scanning**: Typedown does **not** automatically scan directories for models to ensure deterministic builds and improve performance.

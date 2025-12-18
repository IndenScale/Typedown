# Class Context & Imports

Typedown needs to know which Python Pydantic model corresponds to `ClassName` when `entity:ClassName` is used in the current Markdown document. We call this the **Class Context**.

From v0.1.0, Typedown introduced **Executable Configuration Scripts**, allowing flexible definition of contexts by writing standard Python code in `config.td`.

## Mechanism: Executable Configuration Scripts

In a `config.td` file in any directory, you can use code blocks tagged with `config:python`. Typedown executes these code blocks when parsing documents.

**Core Features:**

1.  **Auto-discovery**: All `pydantic.BaseModel` subclasses defined in or imported into the script's namespace are automatically registered to the current class context.
2.  **Cascading Context**: Subdirectories inherit the environment after the execution of parent directory scripts. This allows you to define general models in the root directory and perform specific extensions in subdirectories.

## Best Practices and Patterns

We recommend the following three usage patterns, corresponding to different development stages and needs.

### 1. Standard Import (Recommended)

This is the **best practice** for production environments and long-term maintenance projects.

- **Approach**: Define models in the `models/` package in the project root directory (standard `.py` files), then import them in `config.td`.
- **Advantages**: Enjoy full IDE support (autocomplete, refactoring, type checking); models can be reused by backend code.

````markdown
# config.td

```config:python
import sys
from pathlib import Path

# Tip: Add project root to sys.path to allow importing models
# Note: Typedown runtime usually handles paths automatically, but explicit addition is more robust
sys.path.append(str(Path(__file__).parent / "../../"))

from models.user import User
from models.order import Order
```
````

````

### 2. Inline Prototyping

Suitable for quickly validating ideas or defining temporary structures meaningful only in the current directory.

*   **Approach**: Define Pydantic classes directly in the `config:python` code block of `config.td`.
*   **Advantages**: Extremely fast, no need to create extra `.py` files, keeps thinking coherent.

```markdown
# config.td


```config:python
from pydantic import BaseModel

# Define directly here, immediately usable in sibling Markdown files
class MeetingNote(BaseModel):
    attendees: list[str]
    summary: str
````

````

### 3. Inherit & Specialize

This is where Python configuration scripts are most powerful. You can import generic models and then modify them according to the context needs of the current directory.

*   **Scenario**: There is a global generic `Project` definition, but in the `finance/` directory, all projects need extra budget fields.

```markdown
# use_cases/finance/config.td


```config:python
from common.models import Project as BaseProject

# Inherit and extend
class Project(BaseProject):
    budget_code: str
    is_audited: bool = False

# In this directory, entity:Project refers to this subclass
# The original BaseProject is still available, but the default Project symbol is overridden
````

```


```

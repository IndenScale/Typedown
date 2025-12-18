# Syntax Guide

Typedown combines standard Markdown with executable code blocks to create a "literate modeling" environment.

## 1. Defining Models (`model`)

Use the `model` block to define the structure (Schema) of your data. This uses standard **Python** syntax with **Pydantic**.

**Key Features:**
*   **Auto-Imports:** `BaseModel`, `Field`, `List`, `Optional`, etc., are pre-imported.
*   **Validation:** You can use Pydantic validators directly.

````markdown
```model
class RPGCharacter(BaseModel):
    name: str
    level: int = Field(default=1, ge=1, le=100)
    tags: List[str] = []

    @validator('name')
    def name_must_be_capitalized(cls, v):
        if not v[0].isupper():
            raise ValueError("Name must start with a capital letter")
        return v
```
````

## 2. Instantiating Entities (`entity`)

Use the `entity:<Type>` block to create data instances. The content is **YAML** (or JSON).

**Key Features:**
*   **Type Binding:** `<Type>` must match a class defined in a `model` block (or imported via `config`).
*   **ID:** Every entity needs a unique `id`. If omitted, some implementations might auto-generate one, but explicit is better.

````markdown
```entity:RPGCharacter
id: "hero_01"
name: "Aragorn"
level: 10
tags: ["ranger", "human"]
```
````

### Evolution (`former` / `derived_from`)
Typedown supports tracking the evolution of data over time.

*   `former`: This entity replaces a previous version.
*   `derived_from`: This entity is a transformation of another entity.

````markdown
```entity:RPGCharacter
id: "hero_01_v2"
former: "hero_01"  # This block supersedes "hero_01"
name: "King Aragorn"
level: 50
```
````

## 3. References (`[[...]]`)

You can reference other entities or their properties using double square brackets.

*   **Syntax:** `[[EntityID]]` or `[[EntityID.property]]`
*   **Usage:** Can be used in normal Markdown text to create hyperlinks (supported by the LSP).

> The character [[hero_01]] is the main protagonist.

## 4. Configuration (`config`)

Use `config:python` to set up the environment, import libraries, or load external models.

````markdown
```config:python
import math
from my_lib.models import Weapon
```
````

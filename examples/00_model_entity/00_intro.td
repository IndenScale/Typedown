# Hello Typedown

Welcome to your first Typedown project. This file demonstrates the core concept: **Model + Entity**.

## 1. Define Data Structure (Model)

We use `model` block (powered by Pydantic) to define the shape of our data.

```model: Greeting
from pydantic import BaseModel, Field
from datetime import datetime

class Greeting(BaseModel):
    """A simple greeting message."""
    message: str = Field(..., description="The content of the greeting")
    target: str = Field(..., description="Who we are greeting")
    created_at: datetime = Field(default_factory=datetime.now)
```

## 2. Create Instance (Entity)

We use `entity` block to create an instance of the model defined above.

```entity Greeting: hello-world
message: "Hello"
target: "Typedown Developer"
# created_at will be auto-generated
```

## 3. Verify

Run `td inspect` to see the parsed data!

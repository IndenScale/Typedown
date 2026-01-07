# Example 00: Hello World

This is the minimal reliable example of a Typedown project. It demonstrates how to define a data model and instantiate it using Typedown syntax.

## Contents

- `00_intro.td`: Contains both the Pydantic model definition and an entity instance.

## How to Run

You can use the `td` CLI (or `uvx td`) to interact with this example.

### 1. Inspect the Entity

Parse the file and inspect the structured data:

```bash
# Using installed td
td inspect examples/00_hello_world/00_intro.td

# Or using uvx (no installation required)
uvx td inspect examples/00_hello_world/00_intro.td
```

### 2. Validate

Check if the entity matches the model definition:

```bash
td check examples/00_hello_world/00_intro.td
```

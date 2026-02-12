---
title: Quick Start
---

# Quick Start

This tutorial will guide you through Typedown's core workflow: **Write Markdown, get instant feedback**.

## 1. Installation

### Install CLI

Requires Python 3.14+, install using [uv](https://docs.astral.sh/uv/):

```bash
uv tool install typedown
```

### Install VS Code Extension

Search for `Typedown` in the VS Code marketplace and install.

## 2. Hello World

Create a new directory and a `hello.td` file (Typedown uses `.td` extension, fully compatible with Markdown):

### Step 1: Define Model

In Typedown, everything starts with a **Model**. Tell the system what a `User` should look like:

````typedown
```model:User
class User(BaseModel):
    name: str
    role: str
```
````

Here we use a `model` code block to define the `User` class in Pydantic style.

### Step 2: Create Entity

After the model is defined, you can instantiate data:

````typedown
```entity User: user-alice-v1
name: "Alice"
role: "admin"
```
````

Use an `entity` code block to create an entity of type `User` with ID `user-alice-v1`.

## 3. Get Feedback

Run the check in terminal:

```bash
uv run typedown check .
```

Seeing **No errors found** 🎉 means validation passed!

This is Typedown's core philosophy: **Strongly-typed Markdown**.

If you try to modify `user-alice-v1`'s `age` (undefined field) or change `name` to a number, `typedown check` will immediately report an error.

## 4. Add Validation Rules

Define a `spec` to check complex rules:

````typedown
```spec:check_admin_mfa
@target(type="User", scope="local")
def check_admin_mfa(user: User):
    if user.role == "admin":
        assert user.mfa_enabled, f"Admin {user.name} must enable MFA"
```
````

Now if `user-alice-v1` has role `admin` but no `mfa_enabled` field, an error will be reported.

## 5. Next Steps

You've mastered Typedown's core loop: **Define Model → Create Entity → Validation Feedback**.

- 👉 [Model and Entity](../concepts/model-and-entity) - Deep dive into data structures
- 👉 [Validation Rules](../concepts/validation) - Learn to write complex validation logic

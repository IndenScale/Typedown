---
title: Quick Start
---

# Quick Start

Welcome to Typedown. This tutorial will guide you through the core workflow of Typedown: **Write Markdown, get instant feedback**.

## 1. Installation

Typedown provides a Command Line Interface (CLI) and a VS Code extension.

### Install CLI

Requires Python 3.12+.

```bash
pip install typedown
```

### Install VS Code Extension

Search for `Typedown` in the VS Code Marketplace and install it.

## 2. Hello World

Create a new directory and a new file named `hello.td` (Typedown uses the `.td` extension, fully compatible with Markdown).

### Step 1: Define Model

In Typedown, everything starts with a **Model**. We need to tell the system what a `User` looks like.

Enter the following content in `hello.td`:

````markdown
```model:User
class User(BaseModel):
    name: str
    role: str
```
````

Here we used a `model` block to define a simple `User` class using Pydantic style.

### Step 2: Create Entity

With the model defined, we can now instantiate data. Add the following to the same file:

````markdown
```entity User: alice
name: "Alice"
role: "admin"
```
````

Here we used an `entity` block to create an entity of type `User` with the ID `alice`.

## 3. Get Feedback

Run the check in your terminal:

```bash
td check .
```

You will see Typedown scan the current directory and report: **No errors found**. 🎉

This is the core experience of Typedown: **Strongly Typed Markdown**.

If you try to modify `alice`'s `age` (an undefined field), or change `name` to a number, `td check` will report an error immediately.

## 4. Next Steps

You have mastered the core loop of Typedown: **Define Model -> Create Entity -> Validate Feedback**.

👉 Go to [Syntax Basics](/en/docs/syntax/code-blocks) to learn more details.

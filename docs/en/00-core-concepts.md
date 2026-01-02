# Core Concepts

Typedown is not just about adding data support to Markdown; it is a methodology for **Model Evolution**. During the design process, we made several key trade-offs. This document explains the "Reference as Query" philosophy behind these design choices.

## 0. Definition

Typedown is a **Consensus Modeling Language (CML)**.

It is designed to model the **Truth** within an organization.

- **Non-Goals**: It is **not** a note-taking language, nor is it a general-purpose data serialization format. Do not use it for unstructured scribbles or storing large matrices of data.

## 1. Why "Reference as Query"?

In traditional programming languages or configurations, a reference is usually an **Address**, such as a file path `../db/config.json` or a memory pointer.

Typedown chooses to treat `[[...]]` as a **Query Intent**.

- **Decoupling**: When you write `[[db]]`, you are expressing "I need the thing called db", not "go load the file at path X".
- **Late Binding**: The specific resolution logic is deferred until runtime. This means the same `app.td` file points to the production database when placed in the `prod/` directory, and to the test database when placed in `dev/`.
- **Environmental Polymorphism**: This is the cornerstone of "Write Once, Run Anywhere".

## 2. Why No Nested Lists?

Typedown **strictly prohibits** the use of two-dimensional arrays (List of Lists) within the Entity Body.

**Reason: Separation of Concerns and Data Boundaries.**

Any data requiring more than one dimension (like matrices or tensors) should not appear in Typedown. This is not only to support the syntactical sugar of "Smart Unboxing" for `manager: [[alice]]`, but also to force developers to use the correct data carrier.

**If you need matrix data, please use CSV or JSON. Just don't write it in Typedown.**

## 3. Why Embrace "Fragility" and Tooling?

Many systems pursue "Robustness", meaning files automatically work after being moved. Typedown does the opposite; we **Embrace Fragility** and regard **Tool Dependency** as a core feature.

### 3.1 Simulating Natural Language

We simulate the ambiguity of natural language. Implicit context makes the source code read as fluently as natural language, but it also brings polysemy. This ambiguity is, all in all, no worse than natural language, and must be resolved with a powerful toolchain (Git, LSP, Compiler).

- **Source**: The source code is for humans to read and allows for ambiguity.
- **Artifact**: Ideally, the published documentation must be **Materialized**, perhaps even referencing Hashes. The compiler is responsible for collapsing fuzzy intents into absolute, immutable truth.

### 3.2 Context as Field

Other languages use explicit imports to hardcode dependencies; Typedown uses **Implicit Context**. This creates a powerful "Field":

- **Location determines Destiny**: The physical location of a file determines the "Semantic Field" (Schema constraints, available configs, Handle mappings) it resides in.
- **Moving is Refactoring**: When you move a file from directory A to directory B, you are actually changing the field it inhabits.

### 3.3 Error as Feedback

We do **not** want the system to silently adapt to the new environment. Instead, we want it to **crash immediately**:

- **Explosive Feedback**: If the moved file no longer conforms to the constraints of the new environment (e.g., referencing a Handle that does not exist in the new environment), CI and the Compiler should immediately report dozens of errors.
- **Forced Alignment**: This intense friction forces the developer to stop and explicitly run `get block query` or use the **LSP Code Lens** to re-examine the current context field.
- **Deliberate Rewrite**: Every movement of documentation is a recalibration of cognition. To pass CI, you must deliberately rewrite the code to adapt to the new field.

This design rejects "Silent Misunderstanding" in favor of "Loud Correction". In a Typedown project, passing local tests (`td test`) means you truly understand the field you are in.

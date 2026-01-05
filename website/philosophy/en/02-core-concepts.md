---
title: Core Concepts
---

# Core Concepts

Typedown is more than just adding data support to Markdown; it is a methodology for **Model Evolution**. This document outlines the foundational philosophy of "Reference as Query" and the design trade-offs that make Typedown a powerful tool for complex systems.

## 0. Definition: A Consensus Modeling Language

Typedown is a **Consensus Modeling Language (CML)**.

It is designed to model the **Truth** within an organization—not just raw data, but the shared understanding that binds teams together.

- **Non-Goals**: Typedown is **not** a note-taking language, nor is it a general-purpose data serialization format like JSON. Do not use it for unstructured scribbles or for storing massive, high-dimensional datasets.

## 1. Reference as Query

In traditional programming or configuration, a reference is typically an **Address**—a file path (`../db/config.json`) or a memory pointer.

Typedown treats every reference `[[...]]` as a **Query Intent**.

- **Decoupling**: When you write `[[db]]`, you are declaring, "I need the entity known as db," not "load the file at path X."
- **Late Binding**: Resolution logic is deferred until runtime. The same `app.td` file might resolve to a production database when placed in the `prod/` folder, and to a mock database when in the `dev/` folder.
- **Environmental Polymorphism**: This is the cornerstone of Typedown. It allows models to be reused across different environments while maintaining strict local correctness.

## 2. The Rule of Flat Lists: Why No Nesting?

Typedown **strictly prohibits** two-dimensional arrays (List of Lists) within an Entity Body.

**The Rationale: Separation of Concerns.**

Any data requiring more than one dimension (like matrices or tensors) suggests a complexity that should be modeled as an independent Entity or Model. By enforcing flat lists, we support "Smart Unboxing" (e.g., `manager: [[alice]]` resolving directly to an object) and force developers to choose the appropriate data carrier.

**If you need a matrix, use CSV or JSON. If you need a model, use Typedown.**

## 3. Embracing "Fragility": The Tooling Advantage

While most systems pursue "Robustness" (files that work regardless of where they are moved), Typedown **Embraces Fragility**. We view **Tool Dependency** as a core feature, not a bug.

### 3.1 Simulating Natural Language

Typedown mimics the ambiguity of natural language. Implicit context allows code to read as fluently as a conversation, but it also introduces polysemy. This ambiguity is resolved by our powerful toolchain (Git, LSP, and the Compiler).

- **The Source**: For humans to read, allowing for fluid, contextual expression.
- **The Artifact**: The published truth must be **Materialized**, often referencing immutable content hashes. The compiler is responsible for collapsing fuzzy intent into absolute, objective truth.

### 3.2 Context as Field

In other languages, dependencies are hardcoded via explicit imports. Typedown uses **Implicit Context**, creating a powerful "Semantic Field":

- **Location determines Destiny**: The physical location of a file dictates the "Field" (Schema constraints, configurations, and Handle mappings) it inhabits.
- **Moving is Refactoring**: Relocating a file from directory A to directory B is a fundamental refactor of its meaning.

### 3.3 Error as High-Fidelity Feedback

We do **not** want files to silently adapt to new environments. We want the system to **crash loudly**:

- **Explosive Feedback**: If a moved file violates the constraints of its new environment (e.g., it references a Handle that no longer exists), the Compiler and CI will immediately report dozens of errors.
- **Forced Alignment**: This friction forces the developer to explicitly re-examine the context using **LSP Code Lenses** or direct queries.
- **Deliberate Rewrite**: Every movement of documentation is a recalibration of cognition. To pass CI, you must deliberately align your code with the new environment.

This design rejects "Silent Misunderstanding" in favor of "Loud Correction." In Typedown, passing `td test` means you have achieved true alignment with your project's field of truth.

# Core Concepts of Typedown

The original intention of Typedown design is to reduce the mental resistance during the "progressive formalization" process. It is not meant to replace Markdown, but to enhance it.

## What is "Progressive Formalization"?

In the early stages of a project, our ideas are often divergent and unstructured. At this time, Markdown is the best carrier. As the project advances, we need to constrain, verify, and associate these ideas.

Typedown provides not just data support for Markdown, but a **methodology for model evolution**:

1.  **Inception: Document as Definition**
    Initially, you can define Schema (data models) directly within Typedown documents. This allows for rapid iteration of data structures without leaving the documentation environment.

2.  **Stabilization: Migration to Code**
    Once the model structure stabilizes, you can migrate it to standard Python code. This process is transparent to the data layer—the execution results remain identical—but grants you the full power of version control and IDE support.

3.  **Iteration: Safe Override Mechanism**
    When introducing new features, you don't need to modify production Python code immediately. Typedown allows you to **override** existing definitions by temporarily defining a class with the same name in the document. This enables you to test the impact of new models or constraints on existing data in a sandbox environment, clearly understanding the side effects before formal refactoring.

## Three Core Elements

1.  **Markdown (Host)**: Provides human-readable context.
2.  **Pydantic (Structure)**: Provides data validation and type definition.
3.  **Pytest (Logic)**: Provides cross-file referential integrity checks and complex logic validation.

## Key Terms

### Data Structure
*   **Model**: The blueprint defining the data structure, usually represented by a Pydantic class. It determines what fields exist and their types.
*   **Entity**: A specific instance of a Model. These exist as Markdown code blocks within the document, carrying the actual content.

### Processing
*   **Desugar**: The process where the compiler resolves relationships between Entities (like `former`, `derived_from`) and expands references into complete, independent objects.
*   **Materialize**: An optional step. It involves writing the desugared, complete data back into the Markdown source to enhance self-explanation and readability.

### Validation Levels
*   **Validator**: **Focuses on internal correctness.** Implemented via Pydantic validators, it checks if the Entity's own fields are valid (e.g., score cannot be negative, date format must be correct). This is for common-sense logic.
*   **Specification**: **Focuses on system-level correctness.** This involves complex business logic that requires access to the global Entity Table to evaluate (e.g., ensuring a monster's drop item ID actually exists in the Item table). This requires Fixtures and Test-cases to express.

### Execution Environment
*   **Context**: Determines the set of Model definitions available to the current document. It uses a **layered injection and override** mechanism. The loading order is as follows (later definitions of the same name override earlier ones):
    1.  **Python Code**: Base definitions.
    2.  **Root `config.td`**: Project-level overrides.
    3.  **Nested Directory `config.td`**: Directory-level overrides.
    4.  **Current File `model` block**: File-level temporary definitions or overrides for testing.

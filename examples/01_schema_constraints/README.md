# Example 01: Schema Constraints (Validation)

In Typedown, validation starts **inside the model**. You don't always need to write external rules (`spec`) if you can define the constraint directly in the structure.

## Concepts

1.  **`Field`**: Pydantic's way to add metadata and simple constraints (min/max, regex).
2.  **`@field_validator`**: Auto-correcting or validating a single field.
3.  **`@model_validator`**: Validating relationships between multiple fields (e.g., A < B).

## How to Run

1.  **Check Validation**:

    ```bash
    td check --path examples/01_schema_constraints
    ```

    You will see the entity `bad_pricing` failing because `discount_price` is higher than `price`.

2.  **Inspect Auto-Correction**:

    ```bash
    td query "SELECT * FROM Book" --path examples/01_schema_constraints --sql
    ```

    Notice that the title "the hitchhiker's guide to the galaxy" has been automatically converted to "The Hitchhiker's Guide To The Galaxy".

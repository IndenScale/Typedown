# Example 03: Simple Rules (Local Logic)

Sometimes, static schema validation isn't enough. You need **Business Logic** or **Contextual Validation**. In Typedown, we use `spec` blocks for this.

## Concepts

1.  **`spec`**: A block containing a Python function to validate data.
2.  **`@target`**: A decorator that tells Typedown which entities to check.
3.  **Authentication**: The function receives the entity instance as `subject`.

## How to Run

```bash
td check --path examples/03_simple_rules
```

The check will fail for `future_book` because its publication date is in 2099.

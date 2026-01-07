# Example 02: Inheritance (Structural Reuse)

Typedown supports Object-Oriented Modeling. You can create a base model and extend it to create specialized versions. This helps in keeping your schema "DRY" (Don't Repeat Yourself).

## Concepts

1. **Inheritance**: `class Child(Parent):` syntax.
2. **Polymorphism**: The `Child` model has all fields from `Parent` plus its own.

## How to Run

```bash
td query "SELECT * FROM EBook" --path examples/02_inheritance --sql
```

You will see that `digital_dune` contains both the fields from `Book` (title, author) and `EBook` (file_size_mb, format).

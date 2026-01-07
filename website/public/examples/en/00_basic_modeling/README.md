# Example 00: Basic Modeling (Structure)

Welcome to the **Structure Phase**. In this first step, you will learn the core concept of Typedown: **Model + Entity**.

Think of a `Model` as a **Cookie Cutter** (Class/Schema), and an `Entity` as the **Cookie** (Instance/Data).

## Concepts

1. **`model`**: Defines the shape and type of your data using Python (Pydantic).
2. **`entity`**: Creates actual data that strictly follows that model.

## How to Run

```bash
# Inspect the parsed data
td query "SELECT * FROM Book" --path examples/en/00_basic_modeling --sql
```

You should see that `is_available` is automatically set to `true` because of the default value.

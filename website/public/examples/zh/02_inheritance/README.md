# 示例 02: 继承 (结构复用)

Typedown 支持面向对象建模。你可以创建一个基础模型并对其进行扩展，以创建专门的版本。这有助于保持你的 Schema 符合 "DRY" (Don't Repeat Yourself / 避免重复代码) 原则。

## 核心概念

1.  **继承 (Inheritance)**: 使用 `class Child(Parent):` 语法。
2.  **多态 (Polymorphism)**: `Child` 模型拥有 `Parent` 的所有字段，并加上它自己的字段。

## 如何运行

```bash
td query "SELECT * FROM EBook" --path examples/zh/02_inheritance --sql
```

你会看到 `digital_dune` 同时包含来自 `Book` 的字段 (title, author) 和来自 `EBook` 的字段 (file_size_mb, format)。

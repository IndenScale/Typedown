# 示例 03: 简单规则 (局部逻辑)

有时候，静态的 Schema 校验是不够的。你需要 **业务逻辑 (Business Logic)** 或 **上下文校验 (Contextual Validation)**。在 Typedown 中，我们使用 `spec` 块来实现这一点。

## 核心概念

1. **`spec`**: 包含用于校验数据的 Python 函数的代码块。
2. **`@target`**: 一个装饰器，告诉 Typedown 需要检查哪些实体。
3. **Authentication**: 该函数接收实体实例作为 `subject` 参数。

## 如何运行

```bash
td check --path examples/zh/03_simple_rules
```

你会看到 `future_book` 检查失败，因为它的出版日期是 2099 年。

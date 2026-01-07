# 示例 04: 上下文交互 (计算属性)

Typedown 中的模型不仅仅是数据容器；它们是标准的 Python 类。你可以为它们添加方法和属性。这些计算属性随后可以在你的 Spec 中使用。

## 核心概念

1.  **`@property`**: 在你的 Model 中定义计算字段。
2.  **代码复用**: 复杂的逻辑可以封装在 Model 中，使 Spec 更加简洁。

## 如何运行

```bash
td check --path examples/zh/04_context_interaction
```

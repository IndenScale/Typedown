# 示例 00: 基础建模 (Structure)

欢迎来到 **结构定义阶段**。在第一步中，你将学习 Typedown 的核心概念：**Model (模型) + Entity (实体)**。

可以将 `Model` 想象为 **模具** (类/Schema)，而将 `Entity` 想象为 **饼干** (实例/数据)。

## 核心概念

1. **`model`**: 使用 Python (Pydantic) 定义数据的形状和类型。
2. **`entity`**: 创建严格遵循该模型定义的实际数据。

## 如何运行

```bash
# 查看解析后的数据
td query "SELECT * FROM Book" --path examples/zh/00_basic_modeling --sql
```

你应该看到 `is_available` 字段自动设置为 `true`，这是因为默认值生效了。

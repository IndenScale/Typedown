# 示例 05: 全局治理 (系统逻辑)

目前为止，我们只校验了单个实体。但如果一个规则依赖于 **所有** 实体的 **集合** 呢？这就是 `scope="global"` 发挥作用的地方。

## 核心概念

1.  **`scope="global"`**: Spec 对整个数据集运行一次，而不是对每个实体运行。
2.  **`sql()`**: 像操作数据库一样查询实体的强大方式。
3.  **聚合 (Aggregation)**: 对查询结果使用 Python 的 `sum`, `max`, `min` 等函数。
4.  **`blame()`**: 当全局规则失败时，你可以指向某个具体实体，以便在 IDE 中高亮显示它。

## 如何运行

```bash
td check --path examples/zh/05_global_governance
```

检查将会失败，因为单单 `huge_atlas` 就超过了图书馆的限制。注意，由于使用了 `blame()`，错误信息会归咎于 `huge_atlas`。

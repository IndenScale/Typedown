# 示例 01: Schema 约束 (Validation)

在 Typedown 中，校验始于 **模型内部**。如果可以直接在数据结构中定义约束，就不必总是编写外部规则 (`spec`)。

## 核心概念

1.  **`Field`**: Pydantic 用于添加元数据和简单约束（最大/最小值、正则）的方法。
2.  **`@field_validator`**: 对单个字段进行自动修正或校验。
3.  **`@model_validator`**: 校验多个字段之间的关系（例如 A < B）。

## 如何运行

1.  **检查校验结果**:

    ```bash
    td check --path examples/zh/01_schema_constraints
    ```

    你会看到 `bad_pricing` 实体报错，因为 `discount_price` 高于 `price`。

2.  **查看自动修正**:

    ```bash
    td query "SELECT * FROM Book" --path examples/zh/01_schema_constraints --sql
    ```

    注意这里的标题 "the hitchhiker's guide to the galaxy" 会被自动修正为标题大写格式 "The Hitchhiker's Guide To The Galaxy"。

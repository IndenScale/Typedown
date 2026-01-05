# 华东区 2025 Q1 预算草案 (Python-backed)

状态：**起草中**
负责人：Alice

这里演示了如何直接引用 Python 定义的 `DepartmentBudget` 模型，并在此基础上添加灵活说明。


表明这是一个由 Python 支持的模型，实际模型定义已在全局配置中。

```entity DepartmentBudget: draft_budget_sales_east_2025_v2
year: 2025
department_code: "SALES_EAST"
lines:
  - category: "Travel"
    limit:
        amount: 1500000
        currency: "CNY"
    description: "For Shanghai Expo"
  - category: "Marketing"
    limit:
        amount: 800000
        currency: "CNY"
```

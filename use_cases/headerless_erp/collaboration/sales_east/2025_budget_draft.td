# 华东区 2025 Q1 预算草案 (Python-backed)

状态：**起草中**
负责人：Alice

这里演示了如何直接引用 Python 定义的 `DepartmentBudget` 模型，并在此基础上添加灵活说明。

```config:python
import sys
import os
# Hack: Add the project root to sys.path so we can import the models package
# Assuming we run 'td test' from the project root.
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)
```

```model
from use_cases.headerless_erp.models.finance.budget import DepartmentBudget as _DB

class DepartmentBudget(_DB):
    pass
```

```entity:DepartmentBudget
id: "draft_budget_sales_east_2025_v2"
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

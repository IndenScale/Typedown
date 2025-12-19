# 财务部治理标准 (Finance Governance)

## 预算模型 (Budget Model)

定义了什么是合法的预算编制。

```config:python
import sys
import os
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)
```

```model
from use_cases.headerless_erp.models.finance.budget import DepartmentBudget as _PyDB

class DepartmentBudget(_PyDB):
    """
    Inherits validation logic (Cap < 10M) from Python model.
    """
    pass
```

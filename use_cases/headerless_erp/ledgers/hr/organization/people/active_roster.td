# 人员花名册 (Active Employee Roster)

记录当前在职的正式员工信息。

```config:python
import sys
import os
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.org.structure import Employee
```

## 职能部门负责人 (Functional Heads)

```entity:Employee
id: "emp_hr_head_001"
name: "Sarah Connors"
email: "sarah.c@corp.com"
title: "HR Director"
department_id: "dept_hr_main"
level: 15
```

```entity:Employee
id: "emp_fin_head_001"
name: "Gordon Gekko"
email: "gordon.g@corp.com"
title: "Chief Financial Officer"
department_id: "dept_finance_main"
level: 18
```

```entity:Employee
id: "emp_pmo_head_001"
name: "Neo Anderson"
email: "neo.a@corp.com"
title: "Head of PMO"
department_id: "dept_pmo_main"
level: 14
```

## 生产中心 - Alpha 小组 (Team Alpha Members)

```entity:Employee
id: "emp_alpha_lead_001"
name: "Rick Deckard"
email: "rick.d@corp.com"
title: "Team Lead"
department_id: "unit_prod_alpha"
level: 10
```

```entity:Employee
id: "emp_alpha_mem_001"
name: "K"
email: "k@corp.com"
title: "Senior Engineer"
department_id: "unit_prod_alpha"
level: 8
```

```entity:Employee
id: "emp_alpha_mem_002"
name: "Luv"
email: "luv@corp.com"
title: "Engineer"
department_id: "unit_prod_alpha"
level: 6
```

```entity:Employee
id: "emp_alpha_mem_003"
name: "Mariette"
email: "mariette@corp.com"
title: "Junior Engineer"
department_id: "unit_prod_alpha"
level: 4
```

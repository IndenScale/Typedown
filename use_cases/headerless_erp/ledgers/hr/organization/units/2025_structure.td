# 组织架构 - 部门记录 (Organizational Units Ledger)

此账本记录了公司当前生效的组织架构单元。

```config:python
import sys
import os
# Ensure project root is in path
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.org.structure import FunctionalDepartment, BusinessUnit
```

## 职能部门 (Functional Departments)

```entity:FunctionalDepartment
id: "dept_hr_main"
name: "Human Resources"
code: "FUNC_HR"
head_id: "emp_hr_head_001"
domain_responsibility: ["Recruiting", "Employee Relations", "Payroll"]
```

```entity:FunctionalDepartment
id: "dept_finance_main"
name: "Finance Department"
code: "FUNC_FIN"
head_id: "emp_fin_head_001"
domain_responsibility: ["Accounting", "Audit", "Treasury"]
```

```entity:FunctionalDepartment
id: "dept_pmo_main"
name: "Project Management Office"
code: "FUNC_PMO"
head_id: "emp_pmo_head_001"
domain_responsibility: ["Project Governance", "Delivery Assurance"]
```

## 业务部门 (Business Units)

```entity:BusinessUnit
id: "unit_prod_global"
name: "Global Production Center"
code: "PROD_GLOBAL"
head_id: "emp_prod_head_001" # 假设的生产总监
cost_center_code: "CC_PROD_001"
```

```entity:BusinessUnit
id: "unit_prod_alpha"
name: "Production Team Alpha"
code: "PROD_ALPHA"
head_id: "emp_alpha_lead_001"
parent_unit_id: "unit_prod_global"
cost_center_code: "CC_PROD_ALPHA"
```

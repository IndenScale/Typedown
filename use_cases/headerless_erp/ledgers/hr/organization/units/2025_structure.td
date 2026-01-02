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

```entity FunctionalDepartment: dept_hr_main
id: "dept_hr_main"
name: "Human Resources"
code: "FUNC_HR"
head: [[emp_hr_head_001]]
domain_responsibility: ["Recruiting", "Employee Relations", "Payroll"]
```

```entity FunctionalDepartment: dept_finance_main
id: "dept_finance_main"
name: "Finance Department"
code: "FUNC_FIN"
head: [[emp_fin_head_001]]
domain_responsibility: ["Accounting", "Audit", "Treasury"]
```

```entity FunctionalDepartment: dept_pmo_main
id: "dept_pmo_main"
name: "Project Management Office"
code: "FUNC_PMO"
head: [[emp_pmo_head_001]]
domain_responsibility: ["Project Governance", "Delivery Assurance"]
```

## 业务部门 (Business Units)

```entity BusinessUnit: unit_prod_global
id: "unit_prod_global"
name: "Global Production Center"
code: "PROD_GLOBAL"
head: [[emp_prod_head_001]] # 假设的生产总监
cost_center_code: "CC_PROD_001"
```

```entity BusinessUnit: unit_prod_alpha
id: "unit_prod_alpha"
name: "Production Team Alpha"
code: "PROD_ALPHA"
head: [[emp_alpha_lead_001]]
parent_unit: [[unit_prod_global]]
cost_center_code: "CC_PROD_ALPHA"
```

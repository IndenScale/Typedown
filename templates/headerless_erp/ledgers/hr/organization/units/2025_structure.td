# 组织架构 - 部门记录 (Organizational Units Ledger)

此账本记录了公司当前生效的组织架构单元。

## 职能部门 (Functional Departments)

```entity FunctionalDepartment: dept_hr_main
name: "Human Resources"
code: "FUNC_HR"
head: [[emp_hr_head_001]]
domain_responsibility: ["Recruiting", "Employee Relations", "Payroll"]
```

```entity FunctionalDepartment: dept_finance_main
name: "Finance Department"
code: "FUNC_FIN"
head: [[emp_fin_head_001]]
domain_responsibility: ["Accounting", "Audit", "Treasury"]
```

```entity FunctionalDepartment: dept_pmo_main
name: "Project Management Office"
code: "FUNC_PMO"
head: [[emp_pmo_head_001]]
domain_responsibility: ["Project Governance", "Delivery Assurance"]
```

## 业务部门 (Business Units)

```entity BusinessUnit: unit_prod_global
name: "Global Production Center"
code: "PROD_GLOBAL"
head: [[emp_prod_head_001]] # 假设的生产总监
cost_center_code: "CC_PROD_001"
```

```entity BusinessUnit: unit_prod_alpha
name: "Production Team Alpha"
code: "PROD_ALPHA"
head: [[emp_alpha_lead_001]]
parent_unit: [[unit_prod_global]]
cost_center_code: "CC_PROD_ALPHA"
```

```entity BusinessUnit: unit_sales_emea
name: "EMEA Sales Region"
code: "SALES_EMEA"
head: [[emp_emea_vp_001]]
cost_center_code: "CC_SALES_EMEA"
```

# 人员花名册 (Active Employee Roster)

记录当前在职的正式员工信息。

## 职能部门负责人 (Functional Heads)

```entity Employee: emp_hr_head_001
name: "Sarah Connors"
email: "sarah.c@corp.com"
title: "HR Director"
department: [[dept_hr_main]]
level: 15
```

```entity Employee: emp_fin_head_001
name: "Gordon Gekko"
email: "gordon.g@corp.com"
title: "Chief Financial Officer"
department: [[dept_finance_main]]
level: 18
```

```entity Employee: emp_pmo_head_001
name: "Neo Anderson"
email: "neo.a@corp.com"
title: "Head of PMO"
department: [[dept_pmo_main]]
level: 14
```

## 生产中心 - Alpha 小组 (Team Alpha Members)

```entity Employee: emp_alpha_lead_001
name: "Rick Deckard"
email: "rick.d@corp.com"
title: "Team Lead"
department: [[unit_prod_alpha]]
level: 10
```

```entity Employee: emp_alpha_mem_001
name: "K"
email: "k@corp.com"
title: "Senior Engineer"
department: [[unit_prod_alpha]]
level: 8
```

```entity Employee: emp_alpha_mem_002
name: "Luv"
email: "luv@corp.com"
title: "Engineer"
department: [[unit_prod_alpha]]
level: 6
```

```entity Employee: emp_alpha_mem_003
name: "Mariette"
email: "mariette@corp.com"
title: "Junior Engineer"
department: [[unit_prod_alpha]]
level: 4
```

## 生产与销售领导层 (Production & Sales Leadership)

```entity Employee: emp_prod_head_001
name: "Roy Batty"
email: "roy.b@corp.com"
title: "Production Director"
department: [[unit_prod_global]]
level: 16
```

```entity Employee: emp_emea_vp_001
name: "Hans Gruber"
email: "hans.g@corp.com"
title: "VP EMEA Sales"
department: [[unit_sales_emea]]
level: 16
```

```entity Employee: emp_1001
name: "Eldon Tyrell"
email: "eldon.t@corp.com"
title: "Senior Consultant"
department: [[unit_prod_global]]
level: 20
```

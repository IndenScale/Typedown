# 员工资质证书记录 (Competency Ledger)

记录员工持有的专业资格证书。

```config:python
import sys
import os
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.hr.competency import EmployeeCertification
```

## PMO 团队

```entity:EmployeeCertification
id: "cert_pmp_neo"
employee_id: "emp_pmo_head_001" # Neo Anderson
type: "PMP"
cert_number: "PMP-1029384"
issue_date: "2018-05-20"
expiry_date: "2027-05-19"
issuing_body: "PMI"
```

## Alpha 生产小组

```entity:EmployeeCertification
id: "cert_pmp_rick"
employee_id: "emp_alpha_lead_001" # Rick Deckard
type: "PMP"
cert_number: "PMP-9982731"
issue_date: "2020-03-15"
expiry_date: "2026-03-14"
issuing_body: "PMI"
```

```entity:EmployeeCertification
id: "cert_sixsigma_k"
employee_id: "emp_alpha_mem_001" # K
type: "Lean Six Sigma"
cert_number: "LSS-BB-1122"
issue_date: "2022-11-01"
issuing_body: "ASQ"
```

## 财务部

```entity:EmployeeCertification
id: "cert_cpa_gordon"
employee_id: "emp_fin_head_001" # Gordon Gekko
type: "CPA"
cert_number: "CPA-NY-001"
issue_date: "1995-09-01"
issuing_body: "AICPA"
```

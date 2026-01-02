# 外部人员 (External Contacts)

记录外部审计、顾问等人员。

```config:python
import sys
import os
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.org.structure import Employee
```

```entity Employee: ext_auditor_pwc_009
id: "ext_auditor_pwc_009"
name: "Sherlock Holmes"
email: "sherlock@pwc.com"
title: "Lead Auditor"
department: [[dept_finance_main]] # Reporting to Finance
level: 15
```

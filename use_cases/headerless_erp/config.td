```config:python
import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
current_file = Path(__file__).resolve()
# use_cases/headerless_erp/config.td -> use_cases/headerless_erp -> use_cases -> root
project_root = current_file.parent.parent.parent

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Export Common Models (Registers them in Typedown Model Registry)
from use_cases.headerless_erp.models.org.structure import Employee, FunctionalDepartment, BusinessUnit
from use_cases.headerless_erp.models.pmo.project import Project
from use_cases.headerless_erp.models.pmo.documents import AcceptanceReport, Contract, RFI, FeasibilityStudy, DesignDocument
from use_cases.headerless_erp.models.core.primitives import Money
from use_cases.headerless_erp.models.finance.budget import DepartmentBudget
from use_cases.headerless_erp.models.infra.physical import Rack, NetworkDevice, CablingRecord
from use_cases.headerless_erp.models.hr.competency import EmployeeCertification
```
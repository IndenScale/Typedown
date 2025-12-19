from typing import List, Dict
from datetime import date
from ...models.pmo.project import Project
from ...models.hr.competency import EmployeeCertification, CertificateType

def validate_project_manager_qualification(project: Project, certs: List[EmployeeCertification]):
    """
    Business Rule: All Project Managers must hold a valid PMP certification.
    """
    # 1. Start with the assumption that the PM is NOT qualified
    has_valid_pmp = False
    
    # 2. Iterate through all certifications to find a match
    for cert in certs:
        # Check if cert belongs to the project manager
        if cert.employee_id == project.manager_id:
            # Check if it is PMP
            if cert.type == CertificateType.PMP:
                # Check if it is expired
                if cert.expiry_date and cert.expiry_date < date.today():
                    print(f"Warning: PM {project.manager_id} has PMP but it expired on {cert.expiry_date}")
                    continue
                
                has_valid_pmp = True
                break
    
    # 3. Assert the rule
    if not has_valid_pmp:
        raise ValueError(
            f"Governance Violation: Project Manager {project.manager_id} for Project {project.code} "
            f"does not hold a valid PMP certification."
        )
    
    return True

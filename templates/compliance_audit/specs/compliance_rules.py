from models.audit_schema import Status, RiskLevel

def check_mitigation_plan(entity, context, params):
    """
    Control with HIGH or CRITICAL risk must have a mitigation plan.
    Target: Control
    """
    ctrl = entity.resolved_data
    risk_level = ctrl.get('risk_level')
    mitigation_plan = ctrl.get('mitigation_plan')
    
    # We need to map string back to Enum if Pydantic didn't do it in resolved_data yet,
    # or just compare strings. resolved_data is usually a dict of primitives or Pydantic objects?
    # Based on Desugar logic, it might be dict.
    
    critical_risks = ["HIGH", "CRITICAL", RiskLevel.HIGH.value, RiskLevel.CRITICAL.value]
    
    if risk_level in critical_risks:
        if not mitigation_plan:
            return False, f"Control {ctrl.get('id')} is {risk_level} risk but has no mitigation plan!"
            
    return True, "OK"

def check_compliance_status(entity, context, params):
    """
    Warn if item is NON_COMPLIANT.
    Target: Control
    """
    ctrl = entity.resolved_data
    status = ctrl.get('status')
    
    if status in ["NON_COMPLIANT", Status.NON_COMPLIANT.value]:
        # This will be raised as the severity defined in spec (e.g. Warning)
        return False, f"Control {ctrl.get('id')} is marked as NON_COMPLIANT."
        
    return True, "OK"

def check_evidence_existence(entity, context, params):
    """
    COMPLIANT items must have evidence.
    Target: Control
    """
    ctrl = entity.resolved_data
    status = ctrl.get('status')
    evidence = ctrl.get('evidence', [])
    
    if status in ["COMPLIANT", Status.COMPLIANT.value]:
        if not evidence or len(evidence) == 0:
            return False, f"Control {ctrl.get('id')} is marked COMPLIANT but provided no evidence!"
            
    return True, "OK"

# Compliance Audit Specifications

This file contains the Python-based spec blocks for the compliance audit use case,

```spec
from models.audit_schema import Status, RiskLevel # Import necessary enums

def test_mitigation_plan_required_for_high_critical_risks(workspace):
    """
    Test: High/Critical risk controls must have mitigation plans.
    """
    # Assuming the workspace has loaded entities of type 'Control'
    controls = workspace.get_entities_by_type("Control")

    for ctrl_entity in controls:
        ctrl = ctrl_entity.resolved_data # Get the Pydantic model instance
        if ctrl.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            assert ctrl.mitigation_plan is not None and ctrl.mitigation_plan.strip() != "", \
                f"Control {ctrl.id} is {ctrl.risk_level.value} risk but has no mitigation plan!"

def test_no_non_compliant_controls_flagged(workspace):
    """
    Test: Flag Non-Compliant controls.
    """
    controls = workspace.get_entities_by_type("Control")

    for ctrl_entity in controls:
        ctrl = ctrl_entity.resolved_data
        if ctrl.status == Status.NON_COMPLIANT:
            # This test should fail if a non-compliant control is found
            # In a real scenario, this might be a warning or a different type of assertion
            # For now, we assert that no NON_COMPLIANT controls exist for a passing test.
            # Or if it's meant to *flag*, then the test should check if the flagging mechanism works.
            # For the purpose of migration to spec block, a failure means it's flagged.
            assert False, f"Control {ctrl.id} is marked as NON_COMPLIANT and should be flagged."

def test_evidence_required_for_compliant_controls(workspace):
    """
    Test: Compliant controls must have evidence.
    """
    controls = workspace.get_entities_by_type("Control")

    for ctrl_entity in controls:
        ctrl = ctrl_entity.resolved_data
        if ctrl.status == Status.COMPLIANT:
            assert ctrl.evidence is not None and len(ctrl.evidence) > 0, \
                f"Control {ctrl.id} is marked COMPLIANT but provided no evidence!"
```

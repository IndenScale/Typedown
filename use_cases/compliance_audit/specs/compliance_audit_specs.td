# Compliance Audit Specifications

This file contains the Python-based spec blocks for the compliance audit use case,

```spec
from models.audit_schema import Status, RiskLevel, Control

# Use @target to bind specs to Control entities
@target(type="Control")
def test_mitigation_plan_required_for_high_critical_risks(subject: Control):
    """
    Test: High/Critical risk controls must have mitigation plans.
    """
    if subject.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        assert subject.mitigation_plan is not None and subject.mitigation_plan.strip() != "", \
            f"Control {subject.id} is {subject.risk_level.value} risk but has no mitigation plan!"

@target(type="Control")
def test_no_non_compliant_controls_flagged(subject: Control):
    """
    Test: Flag Non-Compliant controls.
    """
    if subject.status == Status.NON_COMPLIANT:
         # In pytest, a failure indicates non-compliance.
         assert False, f"Control {subject.id} is marked as NON_COMPLIANT."

@target(type="Control")
def test_evidence_required_for_compliant_controls(subject: Control):
    """
    Test: Compliant controls must have evidence.
    """
    if subject.status == Status.COMPLIANT:
        assert subject.evidence is not None and len(subject.evidence) > 0, \
            f"Control {subject.id} is marked COMPLIANT but provided no evidence!"
```

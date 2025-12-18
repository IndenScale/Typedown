# Audit Rules

Global constraints for compliance process.

```spec:Rule
id: "rule_mitigation_plan_required"
description: "High/Critical risk controls must have mitigation plans."
target: "entity:Control"
check: "specs.compliance_rules.check_mitigation_plan"
severity: "error"
```

```spec:Rule
id: "rule_no_non_compliant"
description: "Flag Non-Compliant controls."
target: "entity:Control"
check: "specs.compliance_rules.check_compliance_status"
severity: "warning"
```

```spec:Rule
id: "rule_evidence_required"
description: "Compliant controls must include evidence."
target: "entity:Control"
check: "specs.compliance_rules.check_evidence_existence"
severity: "error"
```

# 应用代码审计

针对加密模块的检查。

针对 [[req_iso_10_1_1]]，我们发现旧版 API 中存在硬编码密钥。

```entity Control: ctrl_app_hardcoded_keys
requirement_id: "req_iso_10_1_1"
owner: "Dave (Dev Lead)"
status: "COMPLIANT"
risk_level: "LOW"
mitigation_plan: "Keys rotated and migrated to Vault. Ticket: JIRA-1234"
evidence:
  - uri: "jira://PROJ/JIRA-1234"
    description: "Key Rotation Ticket"
```

# 应用代码审计

针对加密模块的检查。

针对 [[req_iso_10_1_1]]，我们发现旧版 API 中存在硬编码密钥。

```entity:Control
id: "ctrl_app_hardcoded_keys"
requirement_id: "req_iso_10_1_1"
owner: "Dave (Dev Lead)"
status: "NON_COMPLIANT"
risk_level: "CRITICAL"
mitigation_plan: "立即轮换密钥并迁移到 Vault。Ticket: JIRA-1234"
```

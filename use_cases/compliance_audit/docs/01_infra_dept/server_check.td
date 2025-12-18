# 基础设施服务器审计

审计员: Bob
日期: 2025-10-12

## 访问控制检查

针对 [[req_iso_9_1_1]] (访问控制策略)，我们检查了生产环境的堡垒机配置。

```entity:Control
id: "ctrl_infra_bastion_access"
requirement_id: "req_iso_9_1_1"
owner: "Alice (Ops Lead)"
status: "COMPLIANT"
risk_level: "HIGH"
evidence:
  - uri: "s3://audit-logs/bastion-config-202510.json"
    description: "堡垒机配置文件快照"
    collected_at: "2025-10-12"
```

## 用户注销流程

针对 [[req_iso_9_2_1]]，发现虽然有流程文档，但自动化脚本在某些情况下会失败。

```entity:Control
id: "ctrl_infra_user_offboarding"
requirement_id: "req_iso_9_2_1"
owner: "Alice (Ops Lead)"
status: "IN_PROGRESS"
risk_level: "MEDIUM"
mitigation_plan: "正在修复 LDAP 同步脚本，预计 2025-11-01 完成。"
```

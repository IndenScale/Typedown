# 全球 CRM 迁移项目 (Titan CRM)

## 1. 危机与重生

这是一场被逼出来的“技术长征”。

2023 年 10 月，Salesforce 通知我们将现有合约续签费用上调 35%，这也意味着我们的年度 CRM 许可支出将突破 200 万美元大关。对于一个利润率正在被通过挤压的制造企业，这是不可接受的。

CTO 决定启动 "Project Titan"，基于开源技术栈自研 CRM，彻底摆脱厂商锁定。这不仅是一次技术替代，更是对全球销售流程的一次梳理与重构。

## 2. 项目核心定义

```config:python
import sys
import os
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.pmo.project import Project
```

```entity:Project
id: "proj_2024_crm_migration"
name: "Global CRM Migration"
code: "PROJ-2024-088"
manager_id: "emp_pmo_head_001"
status: "Warranty"
budget:
    amount: 1200000
    currency: "USD"
```

## 3. 质保期概况 (Warranty Phase)

系统已于上月（2025 年 1 月）正式上线。目前进入为期 3 个月的质保与爬坡期。

*   **北美区**: 运行平稳，Adoptation Rate 达到 92%。
*   **EMEA 区**: **[红色警报]** 德国和法国分公司反馈数据同步存在严重延迟（> 15分钟）。初步排查是法兰克福节点的 Kafka 消费积压所致。
*   **亚太区**: 销售团队抱怨移动端 App 在弱网环境下经常 Crash，研发团队正在紧急 Patch。

## 4. 财务影响

预计本项目将在 1.5 年内收回成本，之后每年为公司节省约 180 万美元 OPEX。

# Typedown Cookbook

本目录包含 Typedown 的学习资源与实战案例，按难度和用途分层组织。

## 目录结构

```
cookbook/
├── 01_getting_started/     # 入门教程
│   ├── en/                 # 英文版
│   │   ├── 00_basic_modeling/     # 基础建模
│   │   ├── 01_schema_constraints/ # 模式约束
│   │   ├── 02_inheritance/        # 继承
│   │   ├── 03_simple_rules/       # 简单规则
│   │   ├── 04_context_interaction/# 上下文交互
│   │   ├── 05_global_governance/  # 全局治理
│   │   └── 06_modular_project/    # 模块化项目
│   └── zh/                 # 中文版
│       └── ... (与 en/ 对应)
├── 02_use_cases/           # 完整用例
│   ├── bid_agent/          # 智能评标系统
│   ├── pmo_saas/           # PMO SaaS 项目管理
│   ├── rpg_campaign/       # RPG 战役管理
│   ├── headerless_erp/     # 无头 ERP
│   └── compliance_audit/   # 合规审计
└── 03_best_practices/      # 最佳实践 (预留)
```

## 使用指南

### 入门学习

如果你是 Typedown 新手，请按顺序学习 `01_getting_started/` 中的示例：

```bash
cd cookbook/01_getting_started/en/00_basic_modeling
td check
```

### 实战参考

如果你需要参考完整项目实现，查看 `02_use_cases/`：

| 用例 | 描述 | 复杂度 |
|------|------|--------|
| `bid_agent` | 招投标评标辅助系统 | ⭐⭐⭐⭐⭐ |
| `pmo_saas` | PMO 项目管理 SaaS | ⭐⭐⭐⭐ |
| `rpg_campaign` | 游戏战役管理 | ⭐⭐ |
| `headerless_erp` | 无头 ERP 系统 | ⭐⭐⭐⭐⭐ |
| `compliance_audit` | 合规审计系统 | ⭐⭐⭐ |

## 从旧路径迁移

原 `examples/` → `cookbook/01_getting_started/`  
原 `templates/` → `cookbook/02_use_cases/`

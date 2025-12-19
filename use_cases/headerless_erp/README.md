# Headerless ERP (无头 ERP)

这是一个基于 Typedown 构建的、面向未来的超大规模“无头”企业资源规划 (ERP) 系统原型。

它不仅是一个软件演示，更是一种**企业数字资产的治理架构**。

## 核心哲学

传统的 ERP 以“功能模块”和“UI 界面”为中心。
Headerless ERP 以**“数据模型 (Ontology)”**、**“治理规则 (Governance)”** 和 **“业务流 (Ledger)”** 为中心。

一切业务行为皆为 Commit。一切业务规则皆为 Compile Error。

## 目录结构设计

本系统将企业架构严格映射为文件系统目录：

### 1. `models/` (模型层)

> **对应现实**：公司内部的常识、公理与基础定义。

这里只有“真理”。它是整个企业的“物理定律”。

- `common/`: 基础类型（货币、单位、时间格式）。
- `org/`: 组织架构定义（员工、角色、层级）。

### 2. `governance/` (治理层)

> **对应现实**：职能部门 (Functional Departments) 与垂直管理条线。

这里存放的是**规则 (Specs)** 和 **模板 (Templates)**。

- 职能部门（如财务部、法务部、HR）在这里定义“什么是一张合法的发票”、“什么是一个合规的合同”。
- 这里只定义规则，不产生具体的业务数据。

### 3. `ledgers/` (账本层)

> **对应现实**：企业的业务流 (Business Flow) 与“生效的”历史记录。

这里是企业最核心的**不可变记录 (Immutable Log)**。

- 目录结构通常映射 `governance` 中的职能分类。
- 只有通过了 `governance` 中 Spec 校验的数据，才有资格被合并 (Merge) 进这里。
- 它是企业的“单一事实来源 (Single Source of Truth)”。

### 4. `collaboration/` (协作区)

> **对应现实**：业务部门 (Business Units) 的日常工作台。

这里是**尚未归档的工作区 (Workspace)**，是充满“噪音”和“草稿”的地方。

- 映射具体业务单元（如：华东销售大区、研发一部）。
- **宽松约束**：在这里，用户可以自由引入不同程度的约束。
- **工作流**：
  1. 团队在这里协作、起草业务单据（如：草拟合同、填写报销单）。
  2. 尝试将草稿针对 `governance` 中的规则进行验证。
  3. 验证通过后，提交 PR 或 Commit 进入 `ledgers`。
  4. 协作区仅保留对 `ledgers` 中已归档数据的引用 (`[[...]]`)。

### 5. `discussions/` (讨论区)

> **对应现实**：会议室、RFC 评审、决策记录。

- 记录针对业务逻辑变更的讨论。
- 每一条新的 Spec 诞生前，都应先在这里进行充分的讨论。

### 6. `scaffolding/` (脚手架)

> **对应现实**：企业 IT 部门、自动化工具。

- `generators/`: 自动生成目录结构的脚本。
- `marketplace/`: 自动导入外部的通用 Models 和 Specs。
- `visualization/`: 基于工单模板的 SPA (Single Page Application) 配置，用于生成可视化的操作界面。

## 运行方式

```bash
# 验证协作区的数据是否合规
td test collaboration/sales/drafts/contract_001.td

# 验证整个账本的一致性
td test ledgers/
```

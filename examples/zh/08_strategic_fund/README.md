# 08 战略基金治理 (Strategic Fund Governance)

这个示例展示了 **"Enterprise Governance" (企业级治理)** 的完整图景。
它不仅仅校验单个文件，而是跨文件校验**资金、人员、项目**三者的逻辑一致性。

## 目录结构

- `model.td`: 定义数据标准 (Fund, Specialist, Project)。
- `ledger.td`: **事实账本**。定义了企业的客观事实（资金池总额、专家库名单、已批准项目）。这些通常来自 ERP/HR 系统。
- `spec.td`: **治理规则**。定义了业务红线（预算穿透检测、人员资质门槛）。
- `report_artifact.td`: **(演示重点)** 用户正在编写的可行性报告。

## 演示剧本 (Demo Script)

打开 `report_artifact.td`，您将看到一个名为 `gen_ai_cluster` 的新项目申请。

### 场景 1：资金穿透 (Fund Solvency Check)

当前配置：

- 基金总额: 1 亿 (在 `ledger.td`)
- 已批准项目 (Proj-001): 4000 万 (在 `ledger.td`)
- **当前申请**: 7000 万

**结果**: 4000 + 7000 = 1.1 亿 > 1 亿。
Typedown 会在 `report_artifact.td` 的 `requested_budget_cny` 处显示红色波浪线错误：

> `ValueError: 基金穿透风险！当前申请批准后将导致超支 1000.00 万元。`

### 场景 2：资质围栏 (Qualification Gate)

尝试修改 `applicant_id`：
将 `Li Qiang` 改为 `Wang Xiao`。

**结果**:
Wang Xiao 在 `ledger.td` 中被标记为学历仅本科且有不良记录。
Typedown 会报错：

> `ValueError: 申请人 'Wang Xiao' 存在不良信用记录，申请驳回。`
> 或者虽然没有不良记录，对于 >1000 万 的项目，会提示 `资质不足`。

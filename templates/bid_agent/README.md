# Bid Agent - 智能评标辅助系统

这是一个基于 `typedown` 的评标辅助系统用例。旨在解决招投标过程中非结构化信息处理难、合规性检查繁琐、专家打分偏差难控等问题。

## 目录结构

*   `models/`: 核心数据模型 (Pydantic)
    *   `core.py`: 项目、供应商、专家基础信息。
    *   `evidence.py`: **证据链模型**。包括资质、业绩、人员及其审核状态 (ValidationStatus)。
    *   `review.py`: **评审模型**。包括评分条款、专家打分、响应项映射。
*   `templates/`: ETL 过程产生的中间态文件示例。
    *   `01_tender_parsing.td`: 招标文件 -> 结构化评分标准。
    *   `02_bid_evidence_mapping.td`: 投标文件 -> 评分项与证据的映射。
*   `specs/`: 业务规则。
    *   `deviation_check.py`: 专家打分偏差分析算法。

## 核心流程

1.  **解析 (Parsing)**: 系统解析招标文件，生成 `ScoringItem` (见 `templates/01...`)。
2.  **提取 (Extraction)**: 解析投标文件，提取 `Certificate`, `Achievement`, `Person` 等实体，生成 `BidResponseItem` (见 `templates/02...`)。
3.  **验证 (Verification)**:
    *   自动：调用外部接口 (如信用中国) 更新 `ValidationStatus`。
    *   人工：专家比对 `DocLocation` 指向的原始扫描件与结构化数据。
4.  **评审 (Review)**: 专家基于 `BidResponseItem` 进行打分 `ExpertScoreEntry`。
5.  **风控 (Risk Control)**: 运行 `specs/deviation_check.py` 检测打分偏差。

## 扩展性

*   **领域模型**: 修改 `ProjectDomain` 枚举并在 `models/evidence.py` 中继承 `BaseQualification` 添加特定行业的资质（如医疗器械注册证）。

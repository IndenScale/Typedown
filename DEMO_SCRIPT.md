# Typedown 深度演示：构建企业级数字神经系统

**核心叙事**：
本演示不展示“功能列表”，而是展示**一套软件工程方法论**。
我们演示企业如何通过**定义本体 (Ontology)**、**编写规范 (Specs)** 和 **管理流转 (Workflow)**，将混乱的业务活动转化为有序的数字资产。

---

## 故事一：本体定义 (The Ontology)

**—— 描绘企业内部知识的物理结构**

**角色**：领域架构师 (Domain Architect)
**场景**：定义企业内不可动摇的基础共识：“什么是钱？”“什么是预算？”

**本质**：
在 Typedown 中，我们不画 UML 图，我们写 Python 代码。这不仅是数据结构，这是可执行的知识定义。

**演示操作**：

1. **查看基础图元**：

   ```bash
   cat use_cases/headerless_erp/models/core/primitives.py
   ```

   _解说_：“看，这里定义了 `Money` 和 `Currency`。这不是文档里的文字，而是强类型的代码。全公司所有的业务系统都将复用这个定义。”

2. **查看业务模型**：
   ```bash
   cat use_cases/headerless_erp/models/finance/budget.py
   ```
   _解说_：“这里定义了 `DepartmentBudget`。它规定了一个合法的预算必须包含年份、部门代码和条目。这是企业的‘物理定律’。”

---

## 故事二：治理即编译器 (The Compiler)

**—— 部署自动化的合规防线**

**角色**：合规官 (Governance Officer)
**场景**：CFO 要求严格控制预算上限。在传统企业，这需要发红头文件；在这里，只需要部署一个 Validator。

**本质**：
业务规则 = 编译错误。我们将“合规检查”从耗时的人工审计，变成了毫秒级的自动化编译过程。

**演示操作**：

1. **查看治理规则**：

   ```bash
   cat use_cases/headerless_erp/governance/finance/budget.td
   ```

   _解说_：“请注意 `validate_total_not_exceed_cap` 函数。这几行代码就是我们的审计员。它不睡觉，不犯错，对每一份预算文档进行 100% 的全量审计。”

2. **(可选) 模拟违规**：
   可以在文件中修改阈值，展示系统如何拒绝不合规的数据。

---

## 故事三：流转与归档 (The Workflow)

**—— 从自由协作到不可变账本**

**角色**：一线业务人员 (Operator) & 审计员 (Auditor)
**场景**：业务数据的生命周期管理。

**本质**：
解决“影子 IT”的核心不是禁止 Excel，而是提供一个**“从 协作区(Collaboration) 到 账本区(Ledger)”**的标准晋升路径。

- **协作区**：允许 Markdown 的自由，方便 AI 生成，方便人机协作。
- **账本区**：只有通过“编译”的数据才能进入，保证数据可信、可追责。

**演示操作**：

1. **查看工作草稿**：

   ```bash
   cat use_cases/headerless_erp/collaboration/sales_east/2025_budget_draft.td
   ```

   _解说_：“这是销售总监的草稿。它是 Markdown，读起来像文档，写起来像笔记。AI 也可以轻松生成它。”

2. **执行审计（编译）**：
   ```bash
   uv run td test use_cases/headerless_erp/collaboration/sales_east/2025_budget_draft.td
   ```
   _解说_：“这一步是关键。系统正在加载所有的 Models 和 Specs，对这份草稿进行深度扫描。
   - **Passed**: 意味着数据结构正确，且符合财务部的所有合规性校验。
   - 只有 Passed 的数据，才有资格被合并（Git Merge）到 `ledgers/` 目录中归档。”

---

## 总结：数据治理的最终形态

通过这三个环节，我们实现了：

1.  **数据可用 (Available)**：Markdown + Python 保证了极致的互操作性，AI 友好。
2.  **数据可信 (Trusted)**：强类型与 Validator 保证了数据质量。
3.  **数据可追责 (Accountable)**：Git 记录了每一次变更。

这就是 **Headerless ERP**：用构建顶级软件项目的方式，构建您的企业业务系统。

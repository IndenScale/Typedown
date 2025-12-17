# 0009. Specs 目录与设计精化

日期: 2025-12-16

## 状态

已接受

## 背景

项目初期的文档和核心概念散布在 `README.md`、`docs/` 和 `dev-docs/adr/` 中。尽管这提供了一个大致的概览，但它缺乏一个正式的、机器可读且与语言无关的 Typedown 标准规范。随着模型定义、上下文管理和测试方法复杂性的增长，需要对“Typedown 标准”进行更清晰、更健壮的定义，并使其与 Python 实现分离。

此外，几个关键概念及其实现细节要么规定不足，要么命名模糊，要么应用不一致，可能导致混淆，并阻碍未来的多语言实现。

## 决策

我们决定通过在项目根目录引入专用的 `specs/` 目录来形式化 Typedown 规范。该目录将作为 Typedown 标准的单一真实来源，涵盖其语法、核心概念、架构和测试机制。

与此同时，我们对 Typedown 的核心设计原则和术语进行了全面的提炼和澄清，特别解决了以下问题：

1. **创建 `specs/` 目录**：

   - **目的**：存放 Typedown 语法、演进、结构、导入机制、引用、测试以及核心架构数据模型的正式规范 (RFC)。
   - **结构**：组织为 `meta/` (核心概念)、`rfc/` (各类功能的征求意见稿) 和 `architecture/` (内部编译器数据模型)。
   - **多语言支持**：在 `specs_zh/` 中镜像，用于中文文档。

2. **术语澄清**：

   - **Model 与 Entity**：明确定义“Model”为类蓝图（Pydantic），“Entity”为其在 Markdown 中的实例（数据）。
   - **Validator 与 Specification**：区分了内部基于 Pydantic 的验证（Validator）和使用 Pytest 进行的复杂跨实体业务逻辑验证（Specification）。
   - **Desugar 与 Materialize**：澄清了它们在数据处理流程中的作用。
   - **Context (上下文)**：定义了模型定义的层级注入与覆盖机制（Python 代码 -> 根目录 `config.td` -> 逐级目录 `config.td` -> 本地 `model` 块）。

3. **模型/上下文定义语法的完善**：

   - **`model` 块简化**：`model:<ClassName>` 语法已被更简单的 `model` 块取代，允许在一个块中定义多个类，并自动注入常用的 Pydantic/Typing 符号，减少了样板代码。
   - **`config:python` 用于上下文**：将 `config.td`（以及其他 Markdown 文件）中的 `config:python` 块形式化为动态上下文注入和外部模型导入的主要机制，并废弃了 Front Matter 中的 YAML `imports`。
   - **自动注入策略**：默认关闭自动扫描 `.py` 文件的功能，强调通过 `config:python` 进行显式导入。

4. **集成 Pytest 进行规范测试**：

   - **`spec` 块作为 Python 测试代码**：`spec` 块现在明确定义为包含 Pytest 测试函数的标准 Python 代码块，完全取代了任何先前基于 DSL 的 `spec` 定义。
   - **Pytest Fixture 与 Marker**：利用 Pytest 原生特性，如 `session`（自动注入的项目上下文 Fixture）和 `@pytest.mark`，实现灵活的测试组织和执行。
   - **`check` 块**：引入了作为针对特定 Entity 的可选内联断言机制。

5. **归档旧 ADRs**：
   - 现有的 `dev-docs/adr/` 内容已移至 `dev-docs/legacy/adr/`，以保留历史思维过程，同时避免与当前正式规范混淆。

## 后果

- **更清晰的标准**：Typedown 现在拥有一个正式的、集中的规范，极大地提高了用户、工具开发者和未来维护者的清晰度。
- **增强的开发者体验**：简化的 `model` 定义和明确的 `config:python` 机制简化了 Typedown 文档的编写。
- **健壮的测试框架**：与 Pytest 的深度集成提供了一个强大、熟悉且灵活的框架，用于定义和执行复杂的业务规则和验证。
- **改进的多语言支持**：并行的 `specs/` 和 `specs_zh/` 目录确保了跨语言规范定义的一致性。
- **维护开销**：初期更新现有文档和代码以符合新规范会带来开销，但从长远来看，在一致性和可维护性方面受益。

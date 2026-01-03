# 代码化 Agent 技能 (Agent Skills as Code)

本示例展示了如何使用 Typedown 以**像写代码一样严谨**的方式来定义 **Agent Skills** (或 Tools)。

## 问题背景

在大多数 Agent 框架 (Swarm, LangChain, fastai) 中，Skill 通常定义于：

1. **原始 Markdown/YAML**: 灵活但容易出错。`properties` 画错一个缩进就会导致 JSON Schema 解析失败。
2. **代码 (Python/TS)**: 对非工程师不友好，且难以脱离实现细节进行独立版本控制。

## 解决方案：Typedown Skills

通过将 Skill 定义为 **Typedown 实体 (Entities)**，你将获得：

1. **严格的 Schema 校验**: 你无法定义一个违反 `Skill` 模型（定义在 `meta/skill_schema.td`）的技能。
2. **业务逻辑检查**: `definition.td` 中的 `spec` 块会自动验证最佳实践（例如：“所有参数必须有描述”）。
3. **LSP 支持**: 编写 Prompt 或 Examples 时，享受代码补全的快感。

## 文件结构

- **[meta/skill_schema.td](./meta/skill_schema.td)**: "元模型 (Metamodel)"。定义了什么是 Skill。用它来强制执行公司范围的标准（例如：“所有技能必须有 'author' 字段”）。
- **[skills/browser_mock/definition.td](./skills/browser_mock/definition.td)**: Skill 的实例。这是真理的源头。

## 工作流

1. **编写**: 在 `.td` 文件中编写技能定义。
2. **验证**: 使用 `td check` 或 VS Code 插件进行校验。
3. **编译**: 将其（概念上）编译为 LLM 需要的格式：
   - _导出为 JSON Schema_: 用于 OpenAI Function Calling。
   - _导出为 Prompt Markdown_: 用于 Claude System Prompts。

```bash
# 验证你的技能是否符合质量标准
uvx typedown check examples/zh/02_agent_skills
```

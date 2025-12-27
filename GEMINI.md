# Typedown AI Guidance

## 核心定义 (Language Core)

Typedown 是 **Organization Modeling Language (OML)**。

> **三位一体 (The Trinity)**:
>
> 1. **Markdown**: 界面层。人类可读的文档。
> 2. **Pydantic**: 结构层。定义数据的 Schema (`class User(BaseModel): ...`)。
> 3. **Pytest**: 逻辑层。定义全局约束和引用完整性。

## 配置体系 (Configuration Hierarchy)

Typedown 支持三层配置，从动态到静态：

1. **Inline Model** (` ```model `): 在 `.td` 文件内部定义，仅对当前文件或后续代码块可见。最灵活，适合原型。
2. **`config.td`**: 目录级配置。通过 `config:python` 注入 Python 类或全局变量。子目录自动继承。
3. **Front Matter**: 文件级静态元数据 (YAML)。

## 演进语义 (Evolution Semantics)

Typedown 的杀手级特性是**追踪时间**。

- **`former: "id"`**: 表示当前实体是旧实体的“下一版本”。编译器会自动合并旧字段。
- **`derived_from: "id"`**: 表示继承关系（即 OOP 的继承）。

## 交互语言

你可以自由选择推理语言，但是必须使用中文汇报。

## 多语言支持

- 根目录文档（README.md）需有对应 `_ZH.md`。
- 其他文档应有多语言目录。

## Markdown 嵌套

注意正确使用嵌套的 Markdown 代码块（如 4 个反引号包裹 3 个反引号）。

## 运行

使用 `uv run td` 来运行程序。技能手册参见 `../.gemini/skills.md`。

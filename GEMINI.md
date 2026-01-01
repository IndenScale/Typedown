# Typedown AI Guidance

## 核心定义 (Language Core)

Typedown 是一门 **共识建模语言 (Consensus Modeling Language - CML)**。详见：[核心理念](docs/zh/00-核心理念.md) | [宣言](docs/zh/manifesto.md)

> **三位一体 (The Trinity)**:
>
> 1. **Markdown**: **界面层**。保留自然语言的表达力，承载思想的流动。
> 2. **Pydantic**: **结构层**。通过 `model` 块定义严谨的数据架构（Schema）。
> 3. **Pytest**: **逻辑层**。通过 `spec` 块定义业务逻辑与断言，锚定真理边界。

## 核心块类型 (Block Types)

Typedown 通过增强 Markdown 的代码块来将其视为语义单元。详见：[核心代码块](docs/zh/01-语法/01-代码块.md)

- **`model`**: 使用 Pydantic 定义数据架构。类名需与块 ID 一致。
- **`entity`**: 声明数据实例。支持 `entity <Type>: <Handle>` 语法。
- **`config`**: 动态配置环境或注入 Python 符号（常用于 `config.td`）。
- **`spec`**: 定义测试与校验逻辑，采用“选择器绑定”模式（`@target`）。

## 配置体系与作用域 (Context & Scoping)

Typedown 采用**词法作用域 (Lexical Scoping)**，符号解析遵循层级递进。详见：[上下文与作用域](docs/zh/02-语义/02-上下文与作用域.md)

1. **Local Scope**: 当前文件的 `model`、`entity` (Handles)。
2. **Directory Scope**: `config.td` 导出的符号（子目录自动继承）。
3. **Parent Scopes**: 递归向上直到 `typedown.yaml` 全局配置。

## 引用即查询 (Reference as Query)

`[[...]]` 代表**查询意图**，通过 **三重解析 (Triple Resolution)** 坍缩为真理。详见：[引用规范](docs/zh/01-语法/02-引用.md)

1. **Hash Check**: 匹配内容哈希 `[[sha256:...]]` (L0 - 绝对鲁棒)。
2. **Handle Lookup**: 匹配当前上下文的局部句柄 `[[alice]]` (L1 - 开发体验)。
3. **ID Lookup**: 匹配全局逻辑 ID `[[users/alice-v1]]` 或 UUID `[[550e84...]]` (L2/L3 - 跨系统版本控制)。

## 演进语义 (Evolution Semantics)

Typedown 追踪时间与结构演进。详见：[演进语义](docs/zh/02-语义/01-演变语义.md)

- **`former: "id"`**: **版本演进**。用于同一个对象的不同状态。ID 必须使用全局稳定标识符（Slug ID, Hash, UUID），禁止使用局部 Handle。
- **`derived_from: "id"`**: **结构继承**。子实体继承父实体的结构，但身份独立。ID 约束同上。
- **合并规则**: 对象递归合并，列表**原子替换**。

## 质量控制 (QC Pipeline)

Typedown 质量控制体系遵循分层原则。详见：[质量控制](docs/zh/03-运行/02-质量控制.md)

1. **L1 (Lint)**: 语法与格式检查（`td lint`）。
2. **L2 (Check)**: Pydantic Schema 合规性检查（`td check`）。
3. **L3 (Validate)**: 图解析、Selector Binding、业务逻辑校验（`td validate`）。
4. **L4 (Test)**: 外部事实核验 (Oracle Interaction)（`td test`）。

## 开发约束与最佳实践

- **禁止嵌套列表**: 严禁在 Entity Body 使用嵌套数组。详见：[核心理念 #2](docs/zh/00-核心理念.md#2-为什么禁止多层列表)
- **显式 ID 晋升**: 稳定后的实体应从 Handle 晋升为 Slug ID（`id: "..."`）。详见：[身份管理](docs/zh/04-最佳实践/01-身份管理.md)
- **环境即场域**: 文件的物理位置决定其语义。移动文件即重构。
- **脚本系统**: 通过 Front Matter 定义可执行脚本。详见：[脚本系统](docs/zh/03-运行/01-脚本系统.md)

## Run help

uv run td --help

### Or use the alias

uv run typedown --help
使用 `uv run td` 或 `uv run typedown` 执行核心逻辑。技能手册参见 `.gemini/skills.md`。

## 任务管理规范 (Task Management)

- **独立任务文件**: 每一轮显著的逻辑运行或任务阶段，必须在 `todos/` 目录下创建独立的任务文件。
- **命名规范**: 使用精确到分钟的时间戳命名，格式为 `YYYY-MM-DD_HHMM.md`（例如 `2026-01-01_2130.md`）。
- **内容要求**: 任务文件需包含任务目标、具体待办事项清单（TODOS）、验收标准以及本轮执行的思考过程（Thought in Chinese）。

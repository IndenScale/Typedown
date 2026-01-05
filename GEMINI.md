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
- **`entity`**: 声明数据实例。支持 `entity <Type>: <Identifier>` 语法。Identifier 即为 System ID。
- **`config`**: 动态配置环境或注入 Python 符号（常用于 `config.td`）。
- **`spec`**: 定义测试与校验逻辑，采用“选择器绑定”模式（`@target`）。

## 配置体系与作用域 (Context & Scoping)

Typedown 采用**词法作用域 (Lexical Scoping)**，符号解析遵循层级递进。详见：[上下文与作用域](docs/zh/02-语义/02-上下文与作用域.md)

1. **Local Scope**: 当前文件的 `model`、`entity` (L2 Handles)。
2. **Directory Scope**: `config.td` 导出的符号（子目录自动继承）。
3. **Parent Scopes**: 递归向上直到 `typedown.yaml` 全局配置。

## 引用即查询 (Reference as Query)

`[[...]]` 代表**查询意图**，通过 **三重解析 (Triple Resolution)** 坍缩为真理。详见：[引用规范](docs/zh/01-语法/02-引用.md)

1. **L0 Hash Check**: 匹配内容哈希 `[[sha256:...]]` (绝对鲁棒)。
2. **L1 Exact Match**: 匹配全局 System ID `[[user-alice-v1]]` (精确索引)。
3. **L2 Context Match**: 匹配当前上下文的局部 Handle `[[alice]]` (模糊查找)。

## 演进语义 (Evolution Semantics)

Typedown 追踪时间与结构演进。详见：[演进语义](docs/zh/02-语义/01-演变语义.md)

- **`former: "id"`**: **版本演进**。用于同一个对象的不同状态。ID 必须使用全局稳定标识符（Slug ID, Hash, UUID），禁止使用局部 Handle。
- **合并规则**: 对象递归合并，列表**原子替换**。

## 质量控制 (QC Pipeline)

Typedown 质量控制体系遵循分层原则。详见：[质量控制](docs/zh/03-运行/02-质量控制.md)

1. **L1 (Lint)**: 语法与格式检查（`td lint`）。
2. **L2 (Check)**: Pydantic Schema 合规性检查（`td check`）。
3. **L3 (Validate)**: 图解析、Selector Binding、业务逻辑校验（`td validate`）。
4. **L4 (Test)**: 外部事实核验 (Oracle Interaction)（`td test`）。

## 开发约束与最佳实践

- **禁止嵌套列表**: 严禁在 Entity Body 使用嵌套数组。详见：[核心理念 #2](docs/zh/00-核心理念.md#2-为什么禁止多层列表)
- **ID 风格晋升**: 稳定后的实体应从 Name 风格（`alice`）晋升为 Slug 风格（`user-alice-v1`），修改 Block Signature 即可。
- **环境即场域**: 文件的物理位置决定其语义。移动文件即重构。
- **脚本系统**: 通过 Front Matter 定义可执行脚本。详见：[脚本系统](docs/zh/03-运行/01-脚本系统.md)

## Run help

uv run td --help

### Or use the alias

uv run typedown --help
使用 `uv run td` 或 `uv run typedown` 执行核心逻辑。技能手册参见 `.gemini/skills.md`。

## 任务管理规范 (Task Management)

Monoco 采用 **"Task as Code"** 的管理哲学，将任务视为可持久化、可追踪的代码资产。

### 1. 目录结构 (Directory Structure)

任务文件不再堆积于根目录，而是按**语言 (Language)** 与 **状态 (Status)** 分层管理：

```text
TODOS/
├── zh/                     # 主要工作语言 (Language Scope)
│   ├── active/             # 进行中 (In Progress)
│   └── archive/            # 已完成/已归档 (Done/Archived)
└── legacy_timestamped/     # 遗留的时间戳文件 (Read-only)
```

### 2. 命名与格式 (Naming & Format)

- **ID 系统**: 采用全局递增的 `TASK-XXXX` 编号（例如 `TASK-0123`）。**注意：Agent 必须在创建前扫描 `active/` 和 `archive/` 目录以获取当前最大 ID，严禁依赖本文件中的示例 ID。**
- **文件命名**: `TASK-{ID}-{slug}.md`（例如 `TASK-0123-new-feature.md`）。
- **元数据**: 必须包含 YAML Front Matter。

```yaml
---
id: TASK-XXXX # 必须是当前最大 ID + 1
type: task
status: active # active | done | cancelled
title: "任务标题"
created_at: YYYY-MM-DD
author: Monoco Agent
---
```

### 3. 工作流 (Workflow)

1. **事实检索**: 在开始任何动作前，首先 `list_dir` 扫描 `TODOS/zh/active/` 与 `TODOS/zh/archive/`，确认最新进度与下一个可用 ID。
2. **Session != Task**: 对话 (Session) 是流动的，任务 (Task) 是永恒的。Agent 应主动将 Session 中的意图转化为 Task 文件。
3. **创建 (Create)**: 在 `active/` 目录创建新任务，通过扫描目录结果分配下一个可用 ID。
4. **开发 (Develop)**: 任务文件是 "Source of Truth"，记录 Context, Objectives, Plan 和 Thought。
5. **归档 (Archive)**: 任务完成后，更新状态为 `done` 并移动至 `archive/` 目录。不要删除任务文件。

## 发布流程 (Release Workflow)

Monoco 采用自动化流水线管理 Typedown 的多渠道发布。

- **触发条件**: 当以 `v*` 开头的标签 (e.g., `v1.2.3`) 被推送到仓库时触发。
- **Action 职责**:
  - `publish-pypi.yml`: 构建并发布 Python 包到 PyPI。
  - `vscode-extension.yml`: 并行构建并发布插件到 VS Code Marketplace 和 Open VSX Registry。
- **一致性**: 该流程确保核心编译器 (PyPI) 与编辑器插件 (VSX/OVSX) 版本始终保持同步。
- **发布指令**:

  ```bash
  git tag vX.Y.Z
  git push --tags
  ```

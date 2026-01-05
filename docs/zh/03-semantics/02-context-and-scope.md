---
title: 上下文与作用域
---

# 上下文与作用域 (Context & Scoping)

Typedown 的执行依赖于一个强大的上下文环境。理解上下文的构成和解析顺序，是掌握 Typedown 模块化能力的关键。

## 1. 上下文 (Context) 定义

**上下文**指的是在解析特定 Typedown 文件（如 `.td` 或 `.md`）时，运行时环境中可见的**符号（Symbols）**集合。

主要符号类型：

- **Handles (句柄)**: 实体在当前作用域内可用的模糊匹配名称（L2）。
- **Models (模型)**: Pydantic 类定义。
- **Variables (变量)**: 通过 `config` 块注入的 Python 对象。

## 2. 作用域层级 (Scope Hierarchy)

Typedown 采用**词法作用域 (Lexical Scoping)**。解析器按照以下顺序查找符号（优先级从高到低）：

1. **Local Scope (本文件)**:
   - 当前文件定义的 `model`, `entity` (L2 Handles)。
   - Inline `config` 块导入的符号。
2. **Directory Scope (当前目录)**:
   - `config.td` 导出的符号。
3. **Parent Scopes (父级目录)**:
   - 向上递归直到根目录的 `config.td`。
   - _Shadowing_: 子目录定义的 Handle 会遮蔽父目录的同名 Handle。
4. **Global Scope (全局预设)**:
   - `typedown.yaml` 定义的全局配置。
   - 运行时内置符号 (Built-ins)。

```mermaid
graph BT
    Global[Global Scope (typedown.yaml)]
    Parent[Parent Directory (config.td)] -->|Inherits| Global
    Dir[Current Directory (config.td)] -->|Overrides| Parent
    Local[Local File] -->|Extends| Dir
```

## 3. 符号解析策略 (Resolution Strategy)

当编译器遇到 `[[ref]]` 时，它不仅查找上下文，还涉及全局索引和内容寻址。

详见 [引用规范](../syntax/references) 中的 **Triple Resolution** 机制：

1. **L0 Hash Check**: 是否为内容摘要？(`sha256:...`)
2. **L1 Exact Match**: 在全局索引中精确查找 **System ID**。
3. **L2 Context Match**: 在当前作用域链中进行模糊匹配查找 **Handle**。

## 4. 句柄 vs 标识符 (Handle vs System ID)

为了支持环境隔离和多态配置，Typedown 严格区分实体的**引用句柄**与**系统标识**。

| 概念               | 术语    | 示例               | 作用域                       | 职责                                                      |
| :----------------- | :------ | :----------------- | :--------------------------- | :-------------------------------------------------------- |
| **Handle (L2)**    | 句柄    | `db_primary`       | **Lexical** (随文件位置变化) | **依赖注入 (DI)**。允许代码引用抽象的名字，而非具体实例。 |
| **System ID (L1)** | 系统 ID | `infra/db-prod-v1` | **Global** (全局唯一)        | **版本控制**。指向特定的、不可变的实体演进流。            |

### 场景：环境覆盖 (Environment Overlay)

通过在不同目录下定义各异的 `config.td`，我们可以实现同一套业务逻辑在不同环境下的复用。

```text
/
├── config.td          -> entity Database: db (定义生产库句柄)
└── staging/
    ├── config.td      -> entity Database: db (定义测试库句柄)
    └── app.td         -> 引用 [[db]]
```

- 在 `/app.td` 中，`[[db]]` 解析为生产库句柄。
- 在 `/staging/app.td` 中，`[[db]]` 解析为测试库句柄。
- **无需修改代码**，只需改变运行上下文。

## 5. 可观测性与对齐 (Observability & Alignment)

为了理解和调试上下文，开发者可以使用以下工具。

### 核心工具

- **LSP Doc Lens (文档透镜)**:
  - 在编辑器中，Lens 应实时显示当前 Block 所处的 Environment 叠加状态（Inherited Configs, Available Handles）。

- **`td get block query`**:
  - 当你对当前 Block 的上下文产生疑惑时，运行此命令。
  - 它会模拟编译器的解析逻辑，输出当前 Block 在三重解析下的最终指向。
  - **工作流**: 编写 -> Query -> 修正。

### 调试建议

如果你不确定 `[[Ref]]` 指向哪里，或者不确定当前生效的 Schema 是什么，请使用工具查询。

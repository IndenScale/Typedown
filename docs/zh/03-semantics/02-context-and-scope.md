# 上下文与作用域 (Context & Scoping)

Typedown 的执行依赖于一个强大的上下文环境。理解上下文的构成和解析顺序，是掌握 Typedown 模块化能力的关键。

## 1. 上下文 (Context) 定义

**上下文**指的是在解析特定 Typedown 文件（如 `.td` 或 `.md`）时，运行时环境中可见的**符号（Symbols）**集合。

主要符号类型：

- **ID**: 实体在当前作用域内可用的名称。
- **Models (模型)**: Pydantic 类定义。
- **Variables (变量)**: 通过 `config` 块注入的 Python 对象。

## 2. 作用域层级 (Scope Hierarchy)

Typedown 采用**词法作用域 (Lexical Scoping)**。解析器按照以下顺序查找符号（优先级从高到低）：

1. **Local Scope (本文件)**:
   - 当前文件定义的 `model`, `entity`。
   - Inline `config` 块导入的符号。
2. **Directory Scope (当前目录)**:
   - `config.td` 导出的符号。
3. **Parent Scopes (父级目录)**:
   - 向上递归直到项目根目录或文件系统根目录的 `config.td`。
   - **项目边界 (Project Boundary)**: `.tdproject` 文件标记项目边界，阻断向上继承。
   - _Shadowing_: 子目录定义的 ID 会遮蔽父目录的同名 ID。
4. **Global Scope (全局预设)**:
   - `typedown.yaml` 定义的全局配置。
   - **运行时内置符号 (Built-ins)**:
     - ~~`query()`~~: **(已弃用)** 全局符号查找（支持 ID 和 属性路径）。请使用列表推导式替代：
       ```python
       # 替代方案：使用列表推导式进行符号查询
       # 查找所有以 "db_" 开头的符号
       [s for s in symbols if s.id.startswith("db_")]
       
       # 按类型和名称过滤
       [s for s in symbols if s.type == "Model" and s.name == target]
       
       # 从 context.ids 字典查询
       [v for k, v in context.ids.items() if k.startswith("prefix")]
       ```
     - `sql()`: (仅限 Spec 块) 基于 DuckDB 的全域 SQL 查询。
     - `blame()`: (仅限 Spec 块) 诊断错误归因。

```mermaid
graph BT
    Global[Global Scope (typedown.yaml)]
    Parent[Parent Directory (config.td)] -->|Inherits| Global
    Boundary[.tdproject Boundary] -->|Blocks| Parent
    Dir[Current Directory (config.td)] -->|Overrides| Boundary
    Local[Local File] -->|Extends| Dir
```

## 3. 符号解析策略 (Resolution Strategy)

当编译器遇到 `[[ref]]` 时，它首先判断引用类型：

- **Hash 引用** (`sha256:...`): 直接在全局哈希索引中查找。
- **ID 引用**: 在当前作用域链中按名称查找，若未找到则回退到全局索引。

详见 [引用规范](../syntax/references)。

## 4. 作用域解析 vs 全局解析

为了支持环境隔离和多态配置，Typedown 区分**作用域内 ID**与**全局 ID**。

| 概念 | 示例 | 作用域 | 职责 |
| :--- | :--- | :--- | :--- |
| **Scoped ID** | `db_primary` | **Lexical** (随文件位置变化) | **依赖注入 (DI)**。允许代码引用抽象的名字，而非具体实例。 |
| **Global ID** | `infra/db-prod-v1` | **Global** (全局唯一) | **版本控制**。指向特定的、不可变的实体。 |

### 场景：环境覆盖 (Environment Overlay)

通过在不同目录下定义各异的 `config.td`，我们可以实现同一套业务逻辑在不同环境下的复用。

```text
/
├── config.td          -> entity Database: db (定义生产库)
└── staging/
    ├── config.td      -> entity Database: db (定义测试库)
    └── app.td         -> 引用 [[db]]
```

- 在 `/app.td` 中，`[[db]]` 解析为生产库。
- 在 `/staging/app.td` 中，`[[db]]` 解析为测试库。
- **无需修改代码**，只需改变运行上下文。

### 场景：项目边界隔离 (Project Boundary Isolation)

使用 `.tdproject` 文件实现多项目共存，解决全局命名空间冲突。

```text
workspace/
├── project-a/
│   ├── .tdproject     # 项目边界标记
│   ├── config.td
│   └── models.td      -> entity User: alice
└── project-b/
    ├── .tdproject     # 项目边界标记
    ├── config.td
    └── models.td      -> entity User: bob  # 同名 ID 不会冲突
```

**边界规则**:
- **文件扫描**: 遇到 `.tdproject` 停止向子目录递归扫描
- **作用域继承**: `.tdproject` 所在目录作为项目根，阻断向上继承父目录的 `config.td`
- **多项目安全**: 允许在同一工作区中独立开发多个项目，无需担心 ID 冲突

**典型用例**: cookbook 案例、monorepo 中的多个服务、多语言（en/zh）同名示例。

## 5. 可观测性与对齐 (Observability & Alignment)

为了理解和调试上下文，开发者可以使用以下工具。

### 核心工具

- **LSP Doc Lens (文档透镜)**:
  - 在编辑器中，Lens 应实时显示当前 Block 所处的 Environment 叠加状态（Inherited Configs, Available IDs）。

- **`td get block query`**:
  - 当你对当前 Block 的上下文产生疑惑时，运行此命令。
  - 它会模拟编译器的解析逻辑，输出当前 Block 的最终指向。
  - **工作流**: 编写 -> Query -> 修正。

### 调试建议

如果你不确定 `[[Ref]]` 指向哪里，或者不确定当前生效的 Schema 是什么，请使用工具查询。

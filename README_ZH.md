# Typedown: 组织建模语言

**Typedown** 是一种开源的**组织建模语言 (Organizational Modeling Language, OML)**，旨在弥合自由形式的人类意图与严格的机器执行之间的鸿沟。

虽然它使用 **Markdown** 作为载体语法，但 Typedown 不仅仅是一种文档格式。它是实现 **Organization as Code (OaC)** 的核心语言。

## 什么是 OML?

正如 **Terraform (HCL)** 对基础设施建模，**SQL** 对数据建模一样，**Typedown** 对组织本身进行建模。

- **实体**: 人员、角色、资产、项目。
- **规则**: 权限、工作流、约束。
- **关系**: 谁向谁汇报？哪个预算资助了这个项目？

它集成了 **Markdown**、**Pydantic**、**Pytest** 和 **Assets**，降低了“渐进式形式化”过程中的认知摩擦。

## 愿景

> **You don't know it until you model it.** (直到你建立了模型，你才真正了解它。) — [**阅读完整的 Typedown 宣言**](docs_zh/manifesto.md)

在软件工程和复杂系统设计中，知识通常从模糊的概念演变为严格的规范。当前的工具迫使我们在非结构化文本（Markdown/Google Docs）和僵硬的结构（数据库/JSON/代码）之间做出二元选择。

Typedown 允许您将 Markdown 作为主要界面，同时通过 Python 的生态系统逐步施加约束：

1. **Markdown**: 主体语言。
2. **Pydantic**: 定义结构（Schema）和局部验证。
3. **Pytest**: 定义全局约束和关系验证。

## 理论基础：软物质信息学

Typedown 的设计基于一种全新的 **“数据材料学”** 视角。我们认为，不同的数据形式对应着物理学中不同的物质状态：

| 数据形式     | 物理对应物                           | 特性                                                  | AI 亲和力                      | 缺陷                                                        |
| :----------- | :----------------------------------- | :---------------------------------------------------- | :----------------------------- | :---------------------------------------------------------- |
| **自由文本** | **简单液体** <br> (Simple Liquid)    | 仅由弱**表面张力**主导。极高流动性，随容器形状而变。  | **极高** <br> (原生栖息地)     | **高熵**。无法承载复杂逻辑，无法支撑高层建筑。              |
| **Markdown** | **聚合物流体** <br> (Polymer Fluid)  | **局部有序**（通过标题/列表形成链段），**长程无序**。 | **高** <br> (RAG 主要食粮)     | **缠结效应**。文档过长时逻辑链缠绕打结，难以解构。          |
| **JSON**     | **羟基磷酸钙** <br> (Hydroxyapatite) | 骨骼成分。**可塑但坚固**，具有精确的微观结构。        | **中** <br> (Function Calling) | **死物质**。只能被动承受压力，无代谢能力，不可自我修复。    |
| **DB / CSV** | **金属晶体** <br> (Metal Crystal)    | 原子严格周期性排列。**极度有序，周期极短**。          | **低** <br> (Text2SQL 损耗大)  | **脆性断裂**。稍有不慎（Schema Change）就会导致灾难性崩塌。 |

### 结论：Typedown 是“生命物质”

Typedown 不仅仅是上述形式的混合，它是一种 **“活性软物质” (Active Soft Matter)**。

1.  **相变能力**: 它允许信息在文档内部发生**相变**。一段自由文本（液体）经过 Agent 的思考，可以在原位结晶为 Pydantic Model（骨骼）；反之，僵化的规则也可以被“酶解”回自然语言。
2.  **吞噬与代谢**: 它可以像单细胞生物一样，将外部的 CSV、JSON 甚至非结构化文本包裹进自己的细胞质中，并利用 **Janitor**（生命维持系统）不断泵入负熵，维持有序状态。
3.  **真正的 AI 载体**: 它是唯一一种既能让 AI 感到舒适（Like Text），又能让机器感到安全（Like Code）的介质。

## 核心概念

### 1. 三位一体：Markdown + Pydantic + Pytest

- **Markdown**: 人类可读的层。
- **Pydantic**: 模式层。定义类和字段级别的验证。
- **Pytest**: 逻辑层。定义需要访问全局变量表（例如，“引用的 ID 必须存在”）的约束。

### 2. 定义与配置

Typedown 提供了三个层级的配置机制，支持从原型到生产的平滑过渡：

- **Model 代码块** (`model`): **内联模式定义**。允许直接在 Markdown 中编写 Pydantic 类。无需切换文件即可快速定义数据结构，完美契合“渐进式”理念。
- **`config.td`**: **作用域上下文**。每个目录可以包含一个配置文件，使用 `config:python` 脚本批量导入 Python 类或注入环境变量。子目录会自动继承父目录的上下文。
- **Front Matter**: **静态元数据**。仅用于记录文档标题、作者、状态等非逻辑信息。

### 3. 实体与数据块

变量使用具有特定语言标识符的代码块来表达：`entity:<class_name>`。

````markdown
# 用户定义

这里我们定义管理员用户。

```model
class User(BaseModel):
    id: str
    name: str
    role: str
```

```entity:User id=u_001
name: "Alice"
role: "admin"
```
````

### 4. 演变与派生（“脱糖”过程）

Typedown 支持以最小化书写来表达数据的演变。

- **`former`**: 代表同一实体（概念上）在不同时间点或状态下的形式。
- **`derived_from`**: 代表基对象的一个变体。

**输入（语法糖）：**

````markdown
# 版本 2

```entity:User
former: "u_001"  # 引用上一个对象
email: "alice@example.com" # 只需新增/修改的字段
```
````

**输出（脱糖/物化）：**
编译器将前一个状态与新字段合并，以创建完整的对象进行验证。

### 5. 编译与物化

CLI 支持“编译”操作，可以：

- **验证**: 检查所有 Pydantic 模型和 Pytest 约束。
- **物化**: 重写文档，用 `former` 或 `derived_from` 源中的完整字段填充缺失字段，从而优化消费者的阅读体验，同时保持编写体验的最小化。

### 6. 目录结构

一个标准的 Typedown 项目结构如下：

```text
.
├── docs/       # 内容。Markdown 文件 (.md / .td)
│   ├── arch/
│   │   ├── config.td  # 该目录的作用域配置
│   │   └── design.md
│   └── ...
├── models/     # 模式。Python Pydantic 类
│   └── user.py
├── specs/      # 约束。Pytest 文件
│   └── test_consistency.py
└── assets/     # 图片、图表、静态文件
```

## 文档与参考

更多详细信息，请查阅以下目录：

- **[规格说明书 (Specs)](specs_zh/)**: 形式化的语言规范、RFCs 和数据模型定义。
- **[用户文档 (Docs)](docs_zh/)**: 普通功能特性介绍和使用指南。
- **[开发文档 (Dev Docs)](dev-docs_zh/)**: 架构决策记录 (ADRs) 和实现细节。

## 架构与工具链

生态系统由几个解耦的组件组成：

### 1. Typedown 编译器 (`tdc`)

负责处理项目的核心库。

- **分析**: 解析 Markdown 抽象语法树（AST），解析导入，构建符号表，并处理 `config.td` 继承。
- **脱糖**: 解析 `former`（时间维度）和 `derived_from`（继承维度）链接，将数据扁平化为纯 Pydantic 实例。
- **Lint**: 静态分析，检查断开的链接、未使用的导入和样式约定。
- **验证**: 执行 Pydantic 验证器，并在提取的数据集上调用 Pytest 运行器。

### 2. Typedown CLI (`td`)

终端的用户界面。

- `td init`: 脚手架一个新项目。
- `td build`: 将文档编译成静态 HTML/PDF（可选集成）。
- `td check`: 运行完整的验证管道。
- `td materialize`: 更新源文件以扩展“糖化”的代码块。

### 3. Typedown LSP (语言服务器)

提供 IDE 体验（VS Code 扩展）。

- **自动补全**: 基于 Pydantic 定义的 `entity:Class` 字段。

- **跳转到定义**: 从 Markdown 中的使用处跳转到 Python 类定义。

- **实时诊断**: 直接在 Markdown 编辑器中显示验证错误（红色波浪线）。

## 安装与使用

Typedown 基于 Python 构建。我们强烈推荐使用 `uv` 进行闪电般的环境管理。

### 方法 1: 使用 `uvx` 直接运行

你可以无需手动安装，直接通过 `uvx`（`uv` 工具链的一部分）运行 Typedown CLI。这非常适合尝鲜或运行一次性命令。

```bash

# 在任意目录下运行

uvx typedown check

```

### 方法 2: 开发环境配置

如果你想参与贡献或在本地项目中使用：

1. **安装 `uv`**:

   ```bash

   curl -LsSf https://astral.sh/uv/install.sh | sh

   ```

2. **初始化虚拟环境并安装**:

   ```bash

   # 在项目根目录下

   uv sync

   ```

3. **运行 CLI**:

   ```bash
   uv run td --help
   ```

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

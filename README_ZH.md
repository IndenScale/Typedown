# Typedown: 共识建模语言 (CML)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**Typedown** 是一门为 **文学建模 (Literate Modeling)** 而生的语言。它旨在弥合思想的流动性（Markdown）与工程的严谨性（Pydantic + Pytest）之间的鸿沟。

> **"Until you model it, you don't know it."** (直到你建立了模型，你才真正了解它。) — [宣言](docs/zh/manifesto.md)

---

## 中文文档资源

- **[核心理念](docs/zh/00-核心理念.md)**: 为什么选择“引用即查询”和“环境即场域”。
- **[语法指南](docs/zh/01-语法/01-代码块.md)**: `model`, `entity`, `spec`, `config` 的详细用法。
- **[运行手册](docs/zh/03-运行/02-质量控制.md)**: 了解 L1-L4 的质量控制流水线。

---

## 三位一体 (The Trinity)

Typedown 将 Markdown 视为 **共识即代码 (Consensus as Code - CaC)** 的一等公民语言，构建在三大支柱之上：

1. **Markdown (界面层)**: 保留自然语言的表达力。它是人类思考与 AI 协作的原生场域。
2. **Pydantic (结构层)**: 通过 `model` 块定义严谨的数据架构。
3. **Pytest (逻辑层)**: 通过 `spec` 块强制执行业务规则与逻辑断言。

## 核心理念：活性软物质 (Active Soft Matter)

在 Typedown 的世界观里，数据是有“物态”的：

| 数据形式     | 物理对应       | 特性                                   | 缺陷                             |
| :----------- | :------------- | :------------------------------------- | :------------------------------- |
| **自由文本** | **简单液体**   | 极高流动性，随容器而变。               | **高熵**。无法承载复杂逻辑。     |
| **JSON/SQL** | **金属晶体**   | 严格有序，坚硬且脆。                   | **死物质**。Schema 变更即崩塌。  |
| **Typedown** | **活性软物质** | **具备相变能力**。可在原位结晶或酶解。 | 需要工具链（LSP/Compiler）支持。 |

Typedown 允许信息在同一个文档内发生**相变**：从模糊的笔记（液体）逐步“原位结晶”为受限制的模型（骨骼）。这种 **渐进式形式化** 是应对组织复杂性的终极武器。

## 核心特性

- **引用即查询 (Reference as Query)**: `[[ref]]` 不只是指针，它是对真理的查询意图。
- **三重解析 (Triple Resolution)**: 自动根据 **Content Hash** (L0)、**Handle** (L1) 和 **Logical ID** (L2) 坍缩真理。
- **演进语义 (Evolution)**: 使用 `former` 记录时间流转，使用 `derived_from` 表达结构继承。
- **环境即场域 (Context as Field)**: 文件的物理位置决定其语义。通过 `config.td` 实现层级化的配置注入。
- **分层 QC 流水线**: 从语法 Lint 到外部事实 Test 的严格防御守卫。

## 快速上手

### 1. 定义模型

直接在 Markdown 中使用 Python Pydantic 语法定义 Schema：

````markdown
```model:UserAccount
class UserAccount(BaseModel):
    name: str
    age: int = Field(..., ge=18)
    role: str = "member"
```
````

### 2. 声明实体

使用具有“语法糖”的 YAML 声明数据：

````markdown
```entity UserAccount: alice
id: "iam/user/alice-v1"
name: "Alice"
age: 30
role: "admin"
```
````

### 3. 定义规范

针对特定类型的实体编写自动化测试：

````markdown
```spec id=check_roles
@target(type="UserAccount")
def validate_admin(subject: UserAccount):
    if subject.role == "admin":
        assert subject.age >= 25, "管理员必须具备足够的资历"
```
````

## 命令行操作 (CLI)

`td` 工具是您开发循环的最佳伴侣：

- **`td lint`**: (L1) 检查 Markdown 语法与 YAML 格式。
- **`td check`**: (L2) 执行 Pydantic 模型合规性检查。
- **`td validate`**: (L3) 运行引用寻址与 `spec` 内部逻辑校验。
- **`td test`**: (L4) 运行外部事实核验（调用 API/预言机）。
- **`td run <script>`**: 运行定义在 Front Matter 中的快捷脚本。

## 安装

Typedown 深度集成于 [uv](https://github.com/astral-sh/uv) 生态。

```bash
# 克隆并同步环境
git clone https://github.com/IndenScale/Typedown.git
cd Typedown
uv sync

# 查看帮助
uv run td --help
```

---

## 许可证

MIT © [IndenScale](https://github.com/IndenScale)

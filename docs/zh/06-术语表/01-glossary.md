---
title: 术语表
---

# 术语表 (Glossary)

本文档汇总了 Typedown 生态系统中的核心术语与定义。

## 1. 结构与验证 (Structure & Validation)

### Model (模型)
- **Block Signature**: ` ```model:<Type> ``` `
- **定义**: 数据结构的蓝图，对应一个 Pydantic 类。它是所有实体的模板，定义了数据的形状（Schema）和内在逻辑。

### Entity (实体)
- **Block Signature**: ` ```entity <Type>: <Identifier> ``` `
- **定义**: Typedown 中的基本数据单元。它是 Model 的一个具体实例（Instance），包含符合 Schema 定义的 YAML 数据。

### Spec (规格说明)
- **Block Signature**: ` ```spec:<Identifier> ``` `
- **定义**: 基于 Pytest 编写的测试用例，用于描述需要访问**全局符号表**的复杂逻辑约束。Spec 通过 `tags` 与 Entity 进行绑定，验证实体在整个知识图谱中的一致性。

### Model Schema (模型架构)
定义数据形状（Shape）的规范。它规定了实体必须包含哪些字段以及字段的类型。

### Model Validator (模型验证器)
定义在 Model Schema 内部的校验逻辑，用于确保单体数据的完整性（不依赖外部上下文）。
- **Field Validator (字段验证器)**: 针对单个字段值的校验（如：邮箱格式检查）。
- **Model Validator (整体验证器)**: 针对模型实例多字段间的联合校验（如：`end_time` 必须晚于 `start_time`）。

### Oracle (预言机)
*(尚未实现)* Typedown 系统外部提供可信陈述的信息来源（如 ERP、政务数据接口）。它们作为真理的参考系，用于验证文档内容与现实世界的一致性。

## 2. 标识符与引用 (Identifiers & References)

### 引用 (Reference)
在文档中使用 `[[target]]` 语法指向另一个实体的行为。引用是构建知识图谱（Graph）的基础。

### System ID (系统标识)
**L1 标识符**。实体的全局唯一名称，通常反映其在文件系统中的位置或逻辑路径。用于版本控制和持久化引用。

### Handle (句柄)
**L2 标识符**。在特定作用域（Scope）内使用的别名。用于依赖注入（Dependency Injection）和多态配置，允许在不同环境中使用相同的名字指向不同的实体。

### Slug
一种 URL 友好的字符串标识符格式，通常用作 System ID。

### 三重解析 (Triple Resolution)
编译器解析引用时的查找机制，优先级从高到低：
1. **L0: Content Hash (内容哈希)**: 基于内容的不可变寻址（如 `sha256:...`）。
2. **L1: System ID (系统 ID)**: 全局唯一的、版本化的标识符（如 `infra/db-prod-v1`）。
3. **L2: Handle (句柄)**: 上下文相关的、可变的名字（如 `db_primary`）。

## 3. 运行时与作用域 (Runtime & Scoping)

### Context (上下文)
解析特定文件时可见的符号（Symbols）集合，包括可用的 Models、Handles 和 Variables。

### Scope (作用域)
符号的可见范围。Typedown 采用词法作用域（Lexical Scoping），层级如下：
1. **Local Scope**: 当前文件。
2. **Directory Scope**: 当前目录（由 `config.td` 定义）。
3. **Parent Scopes**: 父级目录递归。
4. **Global Scope**: 项目全局配置 (`typedown.yaml`)。

### Config Block (配置块)
- **Block Signature**: ` ```config:python ``` `
- **定义**: 用于动态配置编译上下文的代码块，通常仅允许出现在 `config.td` 文件中。可以在其中导入 Schema、定义全局变量或注册脚本。

### Environment Overlay (环境叠加)
通过在不同目录层级定义 `config.td`，实现对下层目录上下文的修改或覆盖。这允许同一套文档代码在不同环境（如 Production vs Staging）中表现出不同的行为。

## 4. 工具链 (Toolchain)

### Compiler (编译器)
Typedown 的核心引擎，负责解析 Markdown、执行 Python 代码、构建符号表并运行验证逻辑。

### LSP (Language Server Protocol)
Typedown 提供的编辑器服务协议实现，为 VS Code 等编辑器提供代码补全、跳转定义、实时诊断等功能。

### Doc Lens (文档透镜)
IDE 中的一种可视化辅助工具，用于实时显示当前代码块的上下文信息（如继承的配置、解析后的引用目标），帮助开发者可视化上下文状态。

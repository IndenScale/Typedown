---
title: 术语表
---

# 术语表 (Glossary)

本文档汇总了 Typedown 生态系统中的核心术语与定义。

## 1. 结构与验证 (Structure & Validation)

### Model (模型)

- **Block Signature**: ` ```model:<Type>``` `
- **定义**: 数据结构的蓝图，对应一个 Pydantic 类。它是所有实体的模板，定义了数据的形状（Schema）和内在逻辑。

### Entity (实体)

- **Block Signature**: ` ```entity <Type>: <ID> ``` `
- **定义**: Typedown 中的基本数据单元。它是 Model 的一个具体实例（Instance），包含符合 Schema 定义的 YAML 数据。

### Spec (规格说明)

- **Block Signature**: ` ```spec:<ID> ``` `
- **定义**: 基于 Pytest 编写的测试用例，用于描述需要访问**全局符号表**的复杂逻辑约束。Spec 通过 `tags` 与 Entity 进行绑定，验证实体在整个知识图谱中的一致性。

### Model Schema (模型架构)

定义数据形状（Shape）的规范。它规定了实体必须包含哪些字段以及字段的类型。

### Field Validator (字段验证器)

定义在 Model Schema 内部、针对单个字段值的校验逻辑。

- **用途**: 单个字段的格式检查与转换（如：邮箱格式、日期解析、字符串规范化）。
- **示例**: 确保邮箱为小写、验证手机号格式。

### Model Validator (模型验证器)

定义在 Model Schema 内部的跨字段校验逻辑，用于验证模型实例多字段间的一致性。

- **用途**: 局部逻辑校验，确保单体数据完整性（不依赖外部上下文）。
- **示例**: `end_time` 必须晚于 `start_time`、总金额等于各子项之和。

## 2. 标识符与引用 (Identifiers & References)

### 引用 (Reference)

在文档中使用 `[[target]]` 语法指向另一个实体的行为。引用是构建知识图谱（Graph）的基础。

### ID (标识符)

实体的名称。ID 在作用域内唯一，用于引用实体。

- **格式**: 任何不以 `sha256:` 开头的字符串。
- **示例**: `alice`, `user-alice-v1`, `users/alice`

### Content Hash (内容哈希)

基于实体内容计算的 SHA-256 哈希值，用于内容寻址。

- **格式**: `sha256:` 前缀 + 64 位十六进制字符串。
- **用途**: 不可变引用、版本锁定、历史追踪。

### Slug

一种 URL 友好的字符串标识符格式，通常用作 ID。

## 3. 运行时与作用域 (Runtime & Scoping)

### Context (上下文)

解析特定文件时可见的符号（Symbols）集合，包括可用的 Models、IDs 和 Variables。

### Scope (作用域)

符号的可见范围。Typedown 采用词法作用域（Lexical Scoping），层级如下：

1. **Local Scope**: 当前文件。
2. **Directory Scope**: 当前目录（由 `config.td` 定义）。
3. **Parent Scopes**: 父级目录递归向上查找，直到遇到项目边界或文件系统根目录。
4. **Project Boundary**: `.tdproject` 文件标记项目边界，阻断向上继承父目录的 `config.td`。
5. **Global Scope**: 项目全局配置 (`typedown.yaml`) 和运行时内置符号。

### Config Block (配置块)

- **Block Signature**: ` ```config python ``` `
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

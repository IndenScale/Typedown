---
title: 术语表
---

# 术语表

## 结构与验证

### Model（模型）
- **签名**: `model:<Type>`
- **定义**: 数据结构蓝图，对应 Pydantic 类

### Entity（实体）
- **签名**: `entity <Type>: <ID>`
- **定义**: Typedown 基本数据单元，Model 的具体实例

### Spec（规格说明）
- **签名**: `spec:<ID>`
- **定义**: 基于 Pytest 的测试用例，验证全局约束

### Oracle（预言机）
- **定义**: 外部可信信息源（如 ERP、政务接口），用于验证文档与现实一致性

## 标识符与引用

### Ref（引用）
使用 `[[target]]` 语法指向另一实体的行为

### ID（标识符）
实体的全局唯一名称，用于版本控制和精确引用

## 运行时与作用域

### Context（上下文）
解析文件时可见的符号集合

### Scope（作用域）
符号可见范围，采用词法作用域：
1. Local Scope: 当前文件
2. Directory Scope: 当前目录
3. Parent Scopes: 父目录递归
4. Global Scope: 项目全局

### Config Block（配置块）
- **签名**: `config python`
- **定义**: 配置编译上下文的代码块

## 工具链

### Compiler（编译器）
解析 Markdown、执行 Python、构建符号表的核心引擎

### LSP（Language Server Protocol）
为编辑器提供补全、跳转、诊断等功能的协议实现

### Doc Lens（文档透镜）
IDE 中显示代码块上下文信息的可视化工具

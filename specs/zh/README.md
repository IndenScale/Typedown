# Typedown 技术规范 (Specifications)

Typedown 是一个面向未来的组织建模语言 (OML)。本目录包含其完整的技术规范文档。

## 1. 概念 (Concepts)

理解 Typedown 设计哲学的必读文档。

- [00-核心理念.md](00-核心理念.md): 解释核心设计决策，包括“引用即查询”、“禁止多层列表”与“隐式上下文”背后的思考。

## 2. 语法 (Syntax)

定义 Typedown 的物理形态与书写规则。

- [01-代码块.md](01-语法/01-代码块.md): 定义 `model`, `entity`, `config`, `spec` 等核心代码块的语法。
- [02-引用.md](01-语法/02-引用.md): 阐述 `[[...]]` 引用语法及其**三重解析 (Triple Resolution)** 机制。

## 3. 语义 (Semantics)

定义 Typedown 的逻辑模型与符号行为。

- [01-演变语义.md](02-语义/01-演变语义.md): 解释 `former` (时间演变) 与 `derived_from` (结构派生) 的区别。
- [02-上下文与作用域.md](02-语义/02-上下文与作用域.md): 详解词法作用域、配置继承与 **Handle vs Logical ID** 的分离设计。

## 4. 运行 (Runtime)

定义 Typedown 的执行模型、验证流水线与质量控制体系。

- [01-脚本系统.md](03-运行/01-脚本系统.md): 介绍 Front Matter 中的 `scripts` 定义、环境变量注入及作用域继承。
- [02-质量控制.md](03-运行/02-质量控制.md): 建立 **L1-L4 分层质量模型**，明确 `lint`, `check`, `validate`, `test` 的边界与职责。

## 5. 最佳实践 (Best Practices)

- [01-身份管理.md](04-最佳实践/01-身份管理.md): 关于 Entity ID 命名、版本控制与 Handle 使用的指导原则。

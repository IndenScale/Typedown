---
title: 演变语义
---

# 演变语义 (Evolution)

Typedown 不将数据视为静态产物，而是一个不断进化的时间线。

## 1. 线性演变 (`former`)

`former` 关键字将一个新实体状态链接到其上一个版本。

- **语法**: 在实体主体中使用 `former: [[QueryString]]`。
- **约束**: **必须使用全局寻址 (Global Addressing)**。
  - 🚫 **禁止**: 局部 Handle (如 `alice`)。演变关系必须跨越文件和上下文保持稳定。
  - 🚫 **禁止**: 纯字符串 ID (如 `"slug-id"`)。根据最新的 Typedown 规范，必须使用显式引用语法。
  - ✅ **允许**:
    - **Slug ID Reference**: `[[user-alice-v1]]` (最常用)
    - **UUID Reference**: `[[550e84...]]` (机器生成的唯一标识)
    - **Block Fingerprint**: `[[sha256:8f4b...]]` (基于内容的哈希，最精确)
- **语义**:
  - **身份一致性**: 新实体在逻辑上代表同一个对象的不同时间点。
  - **纯指针 (Pure Pointer)**: `former` 仅作为一个元数据链接存在，用于构建时间线。编译器**不执行**数据合并。
  - **增量原则**: 新实体必须包含完整的属性定义（或由用户显式复制）。
  - **不可变性**: 旧 ID 依然是一个有效的、不可变的快照。一旦一个 Entity 被指向（由于其已成为历史），它就不应再被修改（Append Only）。

示例

````markdown
## 版本 1

```entity Feature: id=login_v1
status: planned
```

## 版本 2

```entity Feature: id=login_v2
former: [[login_v1]]
status: in_progress
```
````

## 2. 源码形态与物化 (Source vs. Materialized)

- **显式性**: 源码即真理。不要期待编译器在背后进行不可见的字段注入。
- **可追溯性**: 通过 `former` 链条，你可以利用工具（如 LSP 或 CLI）快速对比不同版本的差异。

---

## 3. 散敛规则

- **演变分叉 (错误)**: 一个 ID 不能成为两个不同实体的 `former`。时间线不可分裂。
- **演变收敛**: 多个旧版本可以演化为一个新版本（代表合并），但需谨慎处理语义冲突。

---
id: FEAT-0015
uid: f6f29f
type: feature
status: open
stage: review
title: 将 query() 迁移至列表推导式
created_at: '2026-02-13T11:00:27'
updated_at: '2026-02-13T11:01:43'
parent: EPIC-0000
dependencies: []
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FEAT-0015'
files:
- docs/en/03-semantics/02-context-and-scope.md
- docs/zh/03-semantics/02-context-and-scope.md
criticality: medium
solution: null # implemented, cancelled, wontfix, duplicate
opened_at: '2026-02-13T11:00:27'
---

## FEAT-0015: 将 query() 迁移至列表推导式

## Objective

Typedown 文档中 `query()` 作为内置符号查找函数的设计已显过时。列表推导式提供了更强大、更灵活且更符合 Python 习惯的符号查询方式。

本 Issue 旨在：
1. 将 `query()` 标记为弃用（deprecated）
2. 更新文档，推荐使用列表推导式作为替代方案
3. 提供清晰的迁移示例

## Acceptance Criteria

- [x] 文档 `02-context-and-scope.md` 中 `query()` 的描述已更新
- [x] 添加了列表推导式的使用示例
- [x] 明确标记 `query()` 为弃用状态

## Technical Tasks

- [x] 分析 `query()` 与列表推导式的差异
- [x] 更新 `docs/zh/03-semantics/02-context-and-scope.md` 中内置符号部分
- [x] 添加弃用说明和替代方案示例

## 迁移对比

### 旧方式（query）
```python
# 假设 query 的用法
results = query("db_*")  # 查找所有以 db_ 开头的符号
```

### 新方式（列表推导式）
```python
# 更灵活、表达能力更强
[s for s in symbols if s.id.startswith("db_")]
[s for s in symbols if s.type == "Model" and s.name == target]
[s for k, v in context.ids.items() if k.startswith("prefix")]
```

## Review Comments

### Self Review

- **变更范围**: 仅更新文档，不涉及代码逻辑变更
- **兼容性**: 标记为弃用而非删除，保持向后兼容
- **文档质量**: 提供了3种常见场景的列表推导式示例
- **双语同步**: 英文文档已同步更新

### Migration Path

对于现有使用 `query()` 的用户，建议迁移路径：
1. 简单前缀匹配: `query("prefix*")` → `[s for s in symbols if s.id.startswith("prefix")]`
2. 属性路径查询: `query("obj.prop")` → `[getattr(s, 'prop', None) for s in symbols if hasattr(s, 'prop')]`
3. 复杂条件: 利用列表推导式的完整 Python 表达式能力

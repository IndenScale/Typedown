---
id: FEAT-0005
uid: c1c300
type: feature
status: open
stage: doing
title: 'Error handling system: introduce error codes and分级 reporting'
created_at: '2026-02-11T21:54:44'
updated_at: '2026-02-11T22:12:41'
parent: EPIC-0000
dependencies:
- FEAT-0004
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FEAT-0004'
- '#FEAT-0005'
files: []
criticality: medium
solution: null # implemented, cancelled, wontfix, duplicate
opened_at: '2026-02-11T21:54:44'
---

## FEAT-0005: Error handling system: introduce error codes and分级 reporting

## Objective

当前错误处理存在错误类型分散、缺乏错误码、报告格式不一致的问题。本任务旨在建立统一的错误体系，支持机器可读和人工可读。

当前问题：
- TypedownError 基础类 + CycleError/ReferenceError 等特定错误
- 各阶段直接 Exception 捕获
- 缺乏机器可识别的错误标识

目标：建立统一的错误码体系，支持 CI/CD 集成和编辑器集成。

## Acceptance Criteria

- [ ] 所有错误包含可机器识别的错误码
- [ ] JSON 输出包含完整的错误码和结构化信息
- [ ] 错误分级明确：Error / Warning / Info / Hint
- [ ] 各编译阶段（L1-L4）错误处理一致
- [ ] 提供错误码文档对照表

## Technical Tasks

- [ ] 设计错误码体系
  - [ ] 定义错误码格式（如 E0101 = L1 语法错误）
  - [ ] 制定分类规则（E01xx=L1, E02xx=L2, E03xx=L3, E04xx=L4）
- [ ] 扩展 TypedownError
  - [ ] 添加 code: str 字段
  - [ ] 添加 level: ErrorLevel 枚举
  - [ ] 保持向后兼容
- [ ] 统一错误收集机制
  - [ ] 各编译阶段统一使用 diagnostics 列表
  - [ ] 实现错误聚合和去重
- [ ] 重构 L1 (Scanner) 错误处理
  - [ ] 为扫描错误分配错误码
  - [ ] 统一错误消息格式
- [ ] 重构 L2 (Linker) 错误处理
  - [ ] 为链接错误分配错误码
  - [ ] 统一错误消息格式
- [ ] 重构 L3 (Validator) 错误处理
  - [ ] 为验证错误分配错误码
  - [ ] 统一错误消息格式
- [ ] 重构 L4 (Spec) 错误处理
  - [ ] 为 Spec 错误分配错误码
  - [ ] 统一错误消息格式
- [ ] 更新 JSON 输出
  - [ ] 更新 commands/utils.py 的 json_serializer
  - [ ] 包含完整的错误码信息
- [ ] 测试
  - [ ] 添加错误码验证测试
  - [ ] 确保 JSON 输出包含所有字段
- [ ] 文档
  - [ ] 创建错误码对照表文档
  - [ ] 更新开发者文档

## 提议的错误码体系

```
E01xx: L1 扫描阶段错误
  E0101: 语法解析失败
  E0102: 配置块位置错误
  E0103: 嵌套列表反模式
  
E02xx: L2 链接阶段错误
  E0201: 模型执行失败
  E0202: 配置执行失败
  E0203: 类名不匹配
  E0204: 重复的 ID 定义
  
E03xx: L3 验证阶段错误
  E0301: 引用解析失败
  E0302: 循环依赖
  E0303: Schema 验证失败
  E0304: 类型不匹配（Ref[T]）
  
E04xx: L4 规范阶段错误
  E0401: Spec 执行失败
  E0402: Oracle 执行失败
```

## Reference

- src/typedown/core/base/errors.py
- src/typedown/commands/utils.py json_serializer

## Review Comments


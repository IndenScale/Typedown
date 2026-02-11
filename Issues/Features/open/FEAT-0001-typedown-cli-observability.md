---
id: FEAT-0001
type: feature
status: open
stage: draft
parent: EPIC-0000
title: Typedown CLI Observability
created_at: '2026-01-13T11:48:00'
opened_at: '2026-01-13T11:48:00'
updated_at: '2026-01-13T11:48:00'
dependencies: []
related: []
domains: []
tags:
- '#EPIC-0000'
- '#FEAT-0001'
- cli
- telemetry
---

## FEAT-0001: Typedown CLI Observability

## Objective

在 Typedown 编译器（CLI）中集成遥测机制，分析用户对 DSL 功能的使用偏好。

## Acceptance Criteria

- [ ] 追踪 `td check`, `td validate`, `td test` 等命令执行。
- [ ] 记录报错类型（Validation Error 类型），帮助优化编译器提示。

## Technical Tasks

- [ ] 寻找或复用 `monoco.core.telemetry` 的轻量级实现。
- [ ] 在 `Typedown` CLI 命令包装层注入埋点。

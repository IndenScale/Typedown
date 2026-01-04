---
name: task-expert
description: "‘任务即代码’ (Task as Code) 管理专家。负责维护 todos/ 目录下的任务文件，确保任务 ID 连续、状态清晰且符合规范。"
---

# 任务管理专家 (Task Expert)

本技能指导如何遵循 **Task as Code** 哲学。在该体系中，对话是流动的，而任务是持久的。所有非琐碎的变更都必须记录在任务文件中。

## 核心工作流

### 1. 任务识别与创建

当识别到一个明确的需求或 bug 时，应立即在 `todos/zh/active/` 目录下创建一个新任务。

- **ID 分配**：查找当前最大的 `TASK-XXXX` 编号，并加 1。
- **文件命名**：`TASK-{ID}-{slug}.md` (小写，连字符分隔)。
- **Frontmatter**：必须包含 `id`, `type`, `status`, `title`, `created_at`, `author`。

### 2. 开发与记录

在任务执行过程中，任务文件是“真理之源”：

- **Context**：在文件中记录背景信息。
- **Objectives**：定义清晰的可交付成果。
- **Plan**：在文件中维护任务清单（Checkbox）。
- **Thought**：记录关键的设计决策或技术转折。

### 3. 任务归档

当任务状态变为 `done` 或 `cancelled` 时：

- 更新 Frontmatter 中的 `status`。
- 将文件从 `active/` 移动到 `archive/`。

## 文件格式标准

任务文件必须使用以下结构：

```markdown
---
id: TASK-XXXX
type: task
status: active # active | done | cancelled
title: "任务标题"
created_at: 202X-XX-XX
author: [Your Name]
---

# TASK-XXXX: [任务标题]

## 背景

[简述为什么需要这个任务]

## 目标

- [ ] 目标 1
- [ ] 目标 2

## 工作流/笔记

[记录执行过程中的思考、命令输出或关键代码片段]
```

## 禁忌 (Antipatterns)

- **跳号**：严禁跳过 ID 编号。
- **遗忘**：严禁在未更新状态的情况下关闭对话。
- **杂乱**：严禁在 `active/` 目录堆积已完成的任务。
- **隐写**：严禁只在对话中讨论复杂逻辑，而不沉淀到任务文件中。

## 示例

- `todos/zh/active/TASK-0005-setup_skills_reference.md`
- `todos/zh/archive/TASK-0004-fix_pydantic_validation.md`

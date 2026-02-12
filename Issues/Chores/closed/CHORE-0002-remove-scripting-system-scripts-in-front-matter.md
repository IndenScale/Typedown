---
id: CHORE-0002
uid: de653b
type: chore
status: open
stage: doing
title: Remove scripting system (scripts in Front Matter)
created_at: '2026-02-12T13:31:03'
updated_at: '2026-02-12T13:31:19'
parent: EPIC-0000
dependencies: []
related: []
domains: []
tags:
- '#CHORE-0002'
- '#EPIC-0000'
files: []
criticality: low
solution: null # implemented, cancelled, wontfix, duplicate
opened_at: '2026-02-12T13:31:03'
---

## CHORE-0002: Remove scripting system (scripts in Front Matter)

## Objective
删除整个 scripting 系统，包括：
- Front Matter 中的 file-level scripts
- config.td 中的 directory-level scripts  
- typedown.toml 中的 project-level tasks
- 脚本执行引擎（ScriptRunner, ScriptService）
- `td run` CLI 命令

## Motivation
- 零生产环境使用（仅在测试和文档中出现）
- 与 package.json scripts、Makefile、taskfile.yml 等功能重叠
- 维护成本高（450+ 行代码），ROI 极低
- 偏离核心定位：Markdown 渐进式形式化

## Acceptance Criteria
- [ ] 所有 scripting 相关代码已删除
- [ ] 所有 scripting 相关文档已删除或更新
- [ ] 所有测试通过
- [ ] 代码库中无 'scripts' 引用（git 历史除外）

## Technical Tasks

### Phase 1: 删除核心代码
- [ ] 删除 `src/typedown/core/analysis/script_runner.py`
- [ ] 删除 `src/typedown/core/services/script_service.py`
- [ ] 删除 `src/typedown/commands/run.py`
- [ ] 从 `src/typedown/core/ast/document.py` 删除 `Document.scripts` 和 `Project.scripts` 字段
- [ ] 从 `src/typedown/core/base/config.py` 删除 `tasks` 和 `ScriptConfig`
- [ ] 从 `src/typedown/core/parser/typedown_parser.py` 删除 scripts 解析逻辑
- [ ] 从 `src/typedown/core/services/__init__.py` 删除 ScriptService 导出
- [ ] 从 `src/typedown/core/compiler.py` 删除 script_svc 和相关方法
- [ ] 从 `src/typedown/main.py` 删除 run 命令注册

### Phase 2: 更新文档
- [ ] 删除 `docs/zh/04-runtime/01-scripting.md`
- [ ] 删除 `docs/en/04-runtime/01-scripting.md`
- [ ] 更新 `docs/zh/02-syntax/05-front-matter.md` 删除 scripts 部分
- [ ] 更新 `docs/en/02-syntax/05-front-matter.md` 删除 scripts 部分
- [ ] 更新 `docs/zh/04-runtime/02-quality-control.md` 删除 scripts 示例
- [ ] 更新 `docs/en/04-runtime/02-quality-control.md` 删除 scripts 示例

### Phase 3: 更新测试和 Fixture
- [ ] 删除 `tests/fixtures/script_test.td`
- [ ] 更新 `tests/unit/04_config/test_front_matter.py` 删除 scripts 测试
- [ ] 更新其他相关测试

### Phase 4: 清理残留引用
- [ ] 搜索并清理代码中所有残留的 scripts 引用
- [ ] 运行完整测试套件确保无破坏

## Review Comments
<!-- Required for Review/Done stage. Record review feedback here. -->

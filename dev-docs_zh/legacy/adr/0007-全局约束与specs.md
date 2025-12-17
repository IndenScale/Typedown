# 0007. 全局约束与 Specs

日期: 2025-12-11

## 状态

已接受

## 背景

我们需要实现 **P2: 全局约束集成**。
目前，Typedown 执行 Schema 验证 (P1)，确保单个实体符合其 Pydantic 模型。然而，我们缺乏一种机制来验证 *跨* 实体的逻辑（例如，“BOSS 总数 < 3”）或强制执行复杂的业务规则（例如，“所有 NPC 必须有头像”）。

我们需要一个设计，能够：
1.  保持数据文件 (`docs/*.md`) 干净可读。
2.  允许灵活地将规则绑定到实体。
3.  支持上下文严重性（例如，规则在 Dev 环境是 Warning，但在 Release 环境是 Error）。

## 决策

### 1. Spec 作为一等公民
我们引入一种新的块类型：`spec:Rule`（或简称 `spec`）。
Specs 应该定义在专门的文件中，最好是在 `specs/` 目录下，以分离 **数据** 和 **约束**。

### 2. Spec 定义语法
Specs 使用基于 YAML 的配置将 Python 逻辑绑定到数据实体。

```yaml
```spec:Rule
id: "rule_boss_hp_limit"
description: "确保 Boss 拥有足够的 HP"

# Selector: 定义此规则应用于哪些实体。
# 这实现了控制反转 (Spec 选取 Data)。
target: "entity:Monster[type='Boss']" 

# Implementation: 指向 specs/ 目录下的 Python 函数
check: "specs.combat.check_min_hp"
params:
  threshold: 5000

# Contextual Severity: 逻辑级别取决于运行环境 (tags)
severity:
  default: "warning"   # 'td validate'
  release: "error"     # 'td validate --tags release'
  dev: "info"          # 'td validate --tags dev'
```
```

### 3. 实现逻辑 (Python)
约束被实现为纯 Python 函数，接受目标实体和上下文。

```python
# specs/combat.py
def check_min_hp(entity, context, params):
    # logic...
    return True, "OK"
```

### 4. 运行器逻辑
`validate` 命令将更新为：
1.  加载所有 `spec` 块。
2.  对于每个 spec，使用 `target` 选择器查询 `symbol_table`（例如，按类名或任意字段过滤）。
3.  对每个匹配的实体执行链接的 Python 函数。
4.  根据 CLI 标签 (`--tags`) 确定最终严重性。
5.  报告结果。

## 后果

1.  **新解析规则**: 解析器需要支持 `spec:` 代码块。
2.  **选择器引擎**: 我们需要一个简单的查询引擎来过滤实体（例如，通过类名或属性值）。
3.  **测试运行器**: `Workspace` 需要一个语义验证阶段，在 Pydantic 验证之后运行这些 specs。
4.  **关注点分离**: 数据保持纯净；规则集中管理。这极大地提高了可维护性。

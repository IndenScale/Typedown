---
title: 教程：RPG 战役
---

# 教程：RPG 战役 (The RPG Campaign)

欢迎来到 Typedown 教程。Typedown 是一门**共识建模语言 (Consensus Modeling Language - CML)**，旨在将流动的思想转化为可验证的数据。在本指南中，我们将通过建模一个简单的 RPG 战役来探索 Typedown 的核心支柱：

1. **定义 (Definitions)**: 建模概念并声明实体。
2. **引用 (References)**: 通过“意图”将世界连接在一起。
3. **演进 (Evolution)**: 随时间追踪世界的状态。

## 1. 设置：上下文场域 (The Context Field)

Typedown 反映了你工作区的物理结构。我们首先在 `config.td` 中配置环境。在这里，我们导入定义了角色 (Character)、物品 (Item) 和怪物 (Monster) 样貌的 Pydantic 模型 (Schemas)。

```python
# config.td
from models.schema import Character, Item, Monster
```

## 2. 定义世界 (手册)

在 `00_manual.td` 中，我们定义基础游戏资产。这是我们静态的“真理源头”。

### 基础物品

我们定义一瓶药水和一把剑。注意 `id` 字段——这是 **Slug**，一个稳定的、全局的标识符。

```entity Item: potion
name: "小型治疗药水"
weight: 0.5
value: 10
```

```entity Item: sword
name: "铁剑"
weight: 1.5
value: 50
```

### 怪物模板

接下来，我们定义一个哥布林。在 Typedown 中，我们更倾向于**显式表达 (Explicitness)**。我们不使用深层的继承树，而是使用 AI 或简单的模板来填充数据。

```entity Monster: goblin
name: "哥布林"
type: "类人生物"
hp: 30
attack: 5
loot:
  - [[item_sword_iron]]
```

> **关于引用的说明**: `[[item_sword_iron]]` 是一个**查询意图 (Query Intent)**。它的意思是“在当前上下文中寻找具有此 ID 或 Handle 的实体”。

## 3. 冒险小队

在 `01_party.td` 中，我们介绍我们的主角们。

```entity Character: valen
name: "瓦伦"
class_name: "战士"
hp: 100
max_hp: 100
inventory:
  - [[item_sword_iron]]
```

```entity Character: lyra
name: "莱拉"
class_name: "法师"
hp: 60
max_hp: 60
inventory:
  - [[item_potion_hp]]
```

## 4. 游戏会话 (演进)

随着游戏在 `02_session.td` 中展开，我们会遇到 Typedown 最强大的特性：**演进语义 (Evolution Semantics)**。

### 遭遇战

两只哥布林出现了！我们不需要复杂的“派生”逻辑，只需在这个特定的会话上下文中将它们声明为独立的实体即可。

```entity Monster: goblin_a
name: "疯狂的哥布林"
hp: 20
attack: 5
```

### 状态更新：时间线

在一场激烈的战斗后，瓦伦受伤了，莱拉消耗了一瓶药水。我们不会覆盖旧数据；而是让它演进。通过使用 `former` 关键字，我们将新状态链接到前一个状态，从而创建一个不可变的历史。

**瓦伦 V2**: 受伤了，但搜刮到了一把额外的剑。

```entity Character: valen_v2
former: "char_valen_v1"
name: "瓦伦"
class_name: "战士"
hp: 80
max_hp: 100
inventory:
  - [[item_sword_iron]]
  - [[item_sword_iron]]
```

**莱拉 V2**: 用掉了她的药水。

```entity Character: lyra_v2
former: "char_lyra_v1"
name: "莱拉"
class_name: "法师"
hp: 60
max_hp: 60
inventory: []
```

## 结论：场域的力量

通过使用 `former`，你创建了一个**可验证的时间线**。编译器现在可以：

- 追踪瓦伦的 HP 在不同会话中是如何变化的。
- 确保 `valen_v2` 仍然是一个有效的 `Character`。
- 在你的世界的过去和现在之间自由导航。

这就是 Typedown 的承诺：**通过建模的纪律实现认知的自由。**

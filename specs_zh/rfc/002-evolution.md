# 演变机制 (Evolution)

Typedown 允许以增量的方式描述数据的变化，这是其核心特性之一。

## 时间维度: `former` (线性演进)

当描述同一个实体在时间维度上的状态变化时，使用 `former` 指向该实体的上一个快照。

**核心规则：任何状态变化都必须创建一个新实体，并拥有独立的 `entity id`。**
这保证了每个 `entity id` 都是该实体在特定时间点的一个不可变快照。编译器在处理 `former` 时，会根据 `id` 历史自动合并字段。

````markdown
# V1.0: 初始状态

```entity:Feature
id: "feat_login_v1"
status: "planned"
priority: "high"
```

# V1.1: 状态变更 - 优先级调整

```entity:Feature
id: "feat_login_v2" # 新 ID
former: "feat_login_v1"
priority: "medium" # 仅需列出变化的字段
```

# V1.2: 状态变更 - 状态更新

```entity:Feature
id: "feat_login_v3" # 新 ID
former: "feat_login_v2"
status: "implemented"
```
````

### `former` 链条的发散 (Code Smell)

`former` 链条描述的是一个实体在单一时间线上的演进。因此，**`former` 链条的任何发散都被视为一种“坏味道”(Code Smell)**，这通常意味着语义上的不准确或使用不当。

- **一度发散 (Info)**: 同一个 `former` 被两个不同的实体引用。视为 `info` 级别提示，允许但需注意。例如：`A -> B` 和 `A -> C`。
- **二度发散 (Warning)**: 一个实体引用了两次已经一度发散的 `former`。视为 `warning` 级别提示。
- **三度及以上发散 (Error)**: 视为 `error` 级别错误，通常意味着严重的逻辑问题，应修改为 `derived_from`。

**何时避免发散：**
如果你发现需要为同一个 `former` 创建多个独立的后续状态，这很可能表示你正在描述的是一个新实体，而非同一个实体的演变，此时应使用 `derived_from` 或为新实体创建全新的 ID，中断 `former` 链。

## 类型维度: `derived_from` (树状派生)

当描述一个实体是另一个实体的变体，或在结构上继承自另一个实体时，使用 `derived_from`。`derived_from` 本身就意味着多样性和分叉，因此其链条发散是正常的。

**核心规则：派生实体也必须拥有独立的 `entity id`。**
`derived_from` 的语义更接近面向对象编程中的继承。派生实体会继承基实体的所有字段，并可以覆盖或添加新字段。

````markdown
```entity:Enemy
id: "goblin_base"
name: "哥布林"
hp: 100
attack: 10
type: "normal"
```

# 变体 1: 普通哥布林

```entity:Enemy
id: "goblin_grunt" # 新 ID
derived_from: "goblin_base"
name: "普通哥布林"
# hp, attack 继承自 goblin_base
```

# 变体 2: 哥布林首领 (覆盖属性并新增)

```entity:Enemy
id: "goblin_boss" # 新 ID
derived_from: "goblin_base"
name: "哥布林首领"
hp: 500  # 覆盖基类属性
attack: 30
loot: ["gold_key", "goblin_crown"] # 新增属性
```
````

---
title: 数据实体
---

# 数据实体 (Entity)

`entity` 块是 Typedown 中实例化数据的主要方式。每一个实体块都代表知识图谱中的一个节点。

## 语法签名

```markdown
```entity <TypeName>: <SystemID>
<YAML Body>
```
```

- **关键字**: `entity`
- **类型**: `<TypeName>` 必须是当前上下文中已定义的一个 Model 类名。
- **标识符**: `<SystemID>` 是该实体的全局唯一标识符（L1 ID）。
- **分隔符**: 类型与 ID 之间使用冒号 `:` 分隔。

## 标识符规则

System ID 是实体的**主键**。

- **推荐格式**: `slug-style` (例如 `user-alice-v1`)。
- **约束**:
  - 全局唯一。
  - 只能包含字母、数字、连字符 `-`、下划线 `_` 和点 `.`。
  - **禁止**包含空格或斜杠 `/`。

## 数据体 (YAML Body)

实体的内容部分采用 **Strict YAML** 格式。

```yaml
name: "Alice"
age: 30
role: "admin"
```

### 引用语法糖

当字段类型为 `List[Reference[T]]` 时，Typedown 支持简化的列表语法：

```yaml
# Model 定义: friends: List[Reference[User]]

# 推荐写法 (Block Style)
friends:
  - [[bob]]
  - [[charlie]]

# 行内写法 (Flow Style)
reviewers: [ [[bob]], [[alice]] ]
```

### 自动解包

编译器会自动处理 `[[ ]]` 语法。在底层，`[[bob]]` 会被解析为一个 `Reference` 对象，而不是简单的字符串。

## 演变 (Evolution)

使用 `former` 字段来声明实体的历史版本。

```yaml
former: [[user-alice-v0]]
name: "Alice (Updated)"
```

详见 [演变语义](/zh/docs/semantics/evolution)。

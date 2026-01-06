# 数据实体 (Entity)

`entity` 块是 Typedown 中实例化数据的主要方式。每一个实体块都代表知识图谱中的一个节点。

## 语法签名 (Block Signature)

````typedown
```entity <TypeName>: <SystemID>
<YAML Body>
```
````

- **关键字**: `entity`
- **类型**: `<TypeName>` 必须是当前上下文中已定义的一个 Model 类名。
- **标识符**: `<SystemID>` 是该实体的全局唯一标识符（L1 ID）。
- **空格不敏感**: 关键字、冒号与标识符之间的空格不再敏感。例如 `entity User:alice` 与 `entity User : alice` 等效。

## 标识符规则

System ID 是实体的**主键**，在 v0.2.13+ 中遵循以下严格限制：

- **字符限制**: 标识符仅允许包含字母、数字、下划线 `_` 和连字符 `-`（正则表达式：`[a-zA-Z0-9_\-]+`）。不再支持点 `.` 符号。
- **命名风格**: 推荐使用 `slug-style` (例如 `user-alice-v1`)。
- **全局唯一**: 在整个项目中必须唯一。
- **禁止字符**: 禁止包含空格、斜杠 `/` 或特殊符号。

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
reviewers: [[[bob]], [[alice]]]
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

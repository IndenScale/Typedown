---
title: 身份管理
---

# 身份管理最佳实践 (Identity Management)

在 Typedown 项目中，清晰的**身份策略**是管理复杂度的关键。

## 1. 两种引用形式

Typedown 支持两种标识符形式：**ID** 和 **Content Hash**。

| 形式 | 示例 | 性质 | 职责 |
| :--- | :--- | :--- | :--- |
| **ID** | `user-alice-v1` | **稳定** | **系统身份**。全局唯一的逻辑标识。用于日常开发和跨实体引用。 |
| **Content Hash** | `sha256:8f4b...` | **不可变** | **完整性锚点**。基于内容计算的确定性指纹。用于版本锁定和历史追踪。 |

## 2. 鲁棒性引用策略 (Robust Addressing)

虽然日常开发主要使用 **ID** 进行快速编写，但在高可靠场景下，**Content Hash** 提供了无与伦比的鲁棒性。

### 场景：基线快照 (Baseline Snapshots)

当发布一个"不可变配置包"时，不应依赖可能被修改的 ID，而应锁定内容 Hash。

```yaml
# 引用特定的、不可篡改的配置版本
# 即使 users/admin-v1 的定义被修改，这个引用依然指向旧的内容
base_policy: [[sha256:e3b0c442...]]
```

这通过一种**确定性算法 (Deterministic Algorithm)** 保证了引用永远不会指向被篡改的数据。

## 3. ID 分配工作流

### Phase 1: 原型期 (Prototyping)

开发者使用简短的 ID 快速编写草稿。

````markdown
```entity User: alice
name: "Alice"
```
````

### Phase 2: 固化期 (Hardening)

当实体的结构稳定，或者需要被外部引用时，应该**使用更明确的 ID**。
IDE 插件应当提供 `Fix ID` 功能，自动生成 Slug 风格的 ID。

````markdown
```entity User: user-alice-v1
name: "Alice"
```
````

### Phase 3: 演进期 (Evolution)

当需要修改实体时，通过 `former` 链接旧版本。

````markdown
```entity User: users-alice-v2
former: "user-alice-v1"
name: "Alice (Updated)"
```
````

## 4. ID 命名规范 (Naming Conventions)

推荐使用 **Hierarchical Slugs (层级式别名)** 作为 ID。

- **格式**: `domain-type-name-version`
- **示例**:
  - `iam-user-alice-v1`
  - `infra-db-primary-v3`
  - `content-post-hello-world-draft`

这种格式天然支持按目录结构进行 Namespace 管理，且在 Git Diff 中具有极佳的可读性。

## 5. 外部系统集成

如果 Typedown 是作为一个现有 SQL 数据库的配置源，数据库 UUID 可以存储在实体内容中。

```yaml
# Signature: entity User: user-alice-v1
# Body:
# 使用专门的扩展字段存储物理 ID
meta:
  db_uuid: '550e8400-e29b-41d4-a716-446655440000'
```

这样保持了 Typedown 文件的可读性，同时维持了与物理世界的锚点。

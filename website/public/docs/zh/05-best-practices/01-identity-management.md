---
title: 身份管理
---

# 身份管理最佳实践 (Identity Management)

在 Typedown 项目中，清晰的**身份分层 (Identity Layering)** 是管理复杂度的关键。

## 1. 身份层级 (The Identity Layers)

我们建议将身份划分为三个明确的层级，从最底层的物理哈希到最上层的逻辑句柄 (L0 - L2)。

| 层级   | 术语             | 示例             | 性质           | 职责                                                                                                              |
| :----- | :--------------- | :--------------- | :------------- | :---------------------------------------------------------------------------------------------------------------- |
| **L0** | **Content Hash** | `sha256:8f4b...` | **Immutable**  | **完整性锚点 (Integrity)**。基于内容计算的确定性指纹。无论 ID 如何变化，只要内容不变，Hash 就不变。               |
| **L1** | **System ID**    | `user-alice-v1`  | **Stable**     | **系统身份 (System Identity)**。全局唯一的逻辑标识 (Slug) 或机器标识 (UUID)。它是跨系统交互的稳定契约。           |
| **L2** | **Handle**       | `alice`          | **Contextual** | **开发体验 (DX)**。语义化、短小、局部有效。尽可能在代码中使用 Handle 进行依赖注入 (DI)，但在持久化时应固化为 L1。 |

## 2. 鲁棒性引用策略 (Robust Addressing)

虽然日常开发主要使用 **L2 (Handle)** 进行快速编写，但在高可靠场景下，**L0 (Content Hash)** 提供了无与伦比的鲁棒性。

### 场景：基线快照 (Baseline Snapshots)

当发布一个“不可变配置包”时，不应依赖可能被修改的 Slug ID，而应锁定内容 Hash。

```yaml
# 引用特定的、不可篡改的配置版本
# 即使 users/admin-v1 的定义被修改，这个引用依然指向旧的内容
base_policy: [[sha256:e3b0c442...]]
```

这通过一种**确定性算法 (Deterministic Algorithm)** 保证了引用永远不会指向被篡改的数据。

## 3. ID 晋升工作流 (The Promotion Workflow)

推荐使用 IDE 插件实现从 L2 (Handle) 到 L1 (System ID) 的平滑晋升。

### Phase 1: 原型期 (Prototyping)

开发者仅使用 Handle (L2) 快速编写草稿。

````markdown
```entity User: alice
name: "Alice"
```
````

此时实体没有显式 ID，编译器会临时生成一个不稳定的内部 ID。

### Phase 2: 固化期 (Hardening)

当实体的结构稳定，或者需要被外部引用时，应该**显式赋予 L1 ID**。
IDE 插件应当提供 `Fix ID` 功能，根据 Handle 自动生成 Slug。

````markdown
```entity User: user-alice-v1
# Uniquify: 赋予全局、稳定的逻辑 ID (L1)
# ID 已提升至 Block Signature，Body 中不再包含 id 字段
name: "Alice"
```
````

### Phase 3: 演进期 (Evolution)

当需要修改实体时，通过 `former` 链接旧版本。

````markdown
```entity User: users-alice-v2
# 升级 ID 至 v2
former: "user-alice-v1"  # 链接到旧的 L1 ID
name: "Alice (Updated)"
```
````

## 4. ID 命名规范 (Naming Conventions)

推荐使用 **Hierarchical Slugs (层级式别名)** 作为 Logical ID。

- **格式**: `domain-type-name-version`
- **示例**:
  - `iam-user-alice-v1`
  - `infra-db-primary-v3`
  - `content-post-hello-world-draft`

这种格式天然支持按目录结构进行 Namespace 管理，且在 Git Diff 中具有极佳的可读性。

## 5. UUID 映射 (UUID Mapping)

如果 Typedown 是作为一个现有 SQL 数据库的配置源，UUID 必不可少。
**不要将 UUID 写在 ID 字段中**。建议作为 hidden metadata 或专门字段。

```yaml
# Signature: entity User: user-alice-v1
# Body:
# 使用专门的扩展字段存储物理 ID
meta:
  db_uuid: "550e8400-e29b-41d4-a716-446655440000"
```

这样保持了 Typedown 文件的可读性，同时维持了与物理世界的锚点。

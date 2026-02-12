---
title: 最佳实践
---

# 最佳实践

## 身份分层

| 类型 | 示例 | 性质 | 用途 |
|------|------|------|------|
| **ID** | `user-alice-v1` | Stable | 系统身份，跨系统交互 |
| **Hash** | `sha256:8f4b...` | Immutable | 完整性锚点，不可变引用 |

## ID 规范

推荐使用 **层级式 Slug**：

- **格式**: `domain-type-name-version`
- **示例**:
  - `iam-user-alice-v1`
  - `infra-db-primary-v3`
  - `content-post-hello-world`

## 版本演进

修改实体时通过 `former` 链接旧版本：

````typedown
```entity User: user-alice-v2
former: [[user-alice-v1]]
name: "Alice (Updated)"
```
````

## 鲁棒性引用

发布不可变配置包时使用 Hash：

```yaml
base_policy: [[sha256:e3b0c442...]]
```

## 项目结构

```
project/
├── typedown.yaml          # 项目配置
├── config.td              # 根级 config
├── models/                # 模型定义
│   ├── user.td
│   └── config.td          # models 目录级 config
├── entities/              # 实体数据
│   ├── users/
│   │   ├── alice.td
│   │   └── bob.td
│   └── config.td
└── specs/                 # 验证规则
    └── validation.td
```

## UUID 映射

与现有数据库集成时，将 UUID 作为元数据字段：

```yaml
meta:
  db_uuid: '550e8400-e29b-41d4-a716-446655440000'
```

保持 `id` 字段的人类可读性。

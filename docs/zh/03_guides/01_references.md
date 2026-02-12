---
title: 引用系统
---

# 引用系统

Typedown 使用 `[[ ]]` 语法建立实体间的链接，支持 **ID 引用** 和 **内容哈希引用**。

## 引用语法

```typedown
[[entity-id]]           # ID 引用
[[sha256:abc123...]]    # 内容哈希引用
```

## 标识符类型

| 类型 | 格式示例 | 用途 |
|------|----------|------|
| **ID** | `[[user-alice-v1]]` | 全局唯一标识符，精确索引 |
| **Hash** | `[[sha256:a1b2...]]` | 内容寻址，绝对锚定 |

## ID 规范

- **字符限制**：字母、数字、下划线 `_`、连字符 `-`、点 `.`
- **命名风格**：推荐使用 `domain-type-name-version` 格式
  - 示例：`iam-user-alice-v1`、`infra-db-primary-v3`
- **全局唯一**：整个项目范围内必须唯一

## 内容寻址

基于内容的哈希引用，指向确定性数据快照：

```yaml
# 引用特定版本的配置快照
base_config: [[sha256:a1b2c3d4...]]
```

**哈希计算**：`SHA-256( Trim( YAML_Content ) )`

相同有效数据 → 相同哈希（忽略注释或格式差异）

## 在 YAML 中使用

### 单值引用

```yaml
# 编译器将 [[user-alice-v1]] 转换为 Ref 对象
manager: [[user-alice-v1]]
```

### 列表引用

```yaml
# Block Style
contributors:
  - [[user-vader-v1]]
  - [[user-tarkin-v1]]

# Flow Style
reviewers: [[[user-emperor-v1]], [[user-thrawn-v1]]]
```

**底层处理**：
1. YAML 解析为 `[['user-vader-v1'], ['user-tarkin-v1']]`
2. 发现字段类型为 `List[Ref[T]]`
3. 自动扁平化为 `[Ref('user-vader-v1'), Ref('user-tarkin-v1')]`

## 类型安全

使用 `Ref` 泛型强制类型约束：

```python
from typedown.types import Ref

class Task(BaseModel):
    # 必须引用 User 类型
    assignee: Ref["User"]
    
    # 允许多种类型
    subscribers: List[Ref["User", "Team"]]
    
    # 自引用
    parent: Optional[Ref["Task"]] = None
```

### 编译时检查

1. **存在性**：`[[user-alice-v1]]` 指向的实体是否存在？
2. **类型安全**：引用的实体是否为预期的 `User` 类型？
3. **数据正确性**：实体数据是否符合 Model Schema？

## 可引用对象

`[[ ]]` 是通用链接语法：

| 目标类型 | 示例 | 说明 |
|----------|------|------|
| Model | `type: [[User]]` | 类型定义 |
| Entity | `manager: [[user-alice-v1]]` | 数据实例 |
| Spec | `validates: [[check-age-v1]]` | 验证规则 |
| File | `assets: [[specs/design.pdf]]` | 文件资源 |

> 文件必须使用 `[[ ]]` 语法以纳入依赖管理。

## 演进引用

在 `former` 字段中使用：

```yaml
former: [[user-alice-v0]]  # ID 引用（最常用）
former: [[sha256:8f4b...]] # Hash 引用（最精确）
```

详见 [演进语义](../concepts/evolution)。

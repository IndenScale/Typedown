---
title: 引用
---

# 引用 (References)

Typedown 使用双中括号 `[[ ]]` 作为统一的引用语法。

## 1. 核心机制：引用即查询 (Reference as Query)

`[[query]]` 代表一个“查询意图”，而非绝对物理地址。

当使用 `[[alice]]` 时，编译器会在当前上下文中查找最匹配的目标。这种机制支持**渐进式开发**：

- 在早期草稿中，可以使用模糊的 Handle (`[[alice]]`)。
- 编译器通过 **三重解析 (Triple Resolution)** 机制将其解析为精确实体。

若需要绝对精确，你应该通过 **Content Hash** (内容指纹) 来锁定特定版本，而非依赖不透明的 UUID。

## 2. 引用形式 (Reference Forms)

Typedown 支持三种引用形式，编译器会根据上下文自动推断你的意图。

- **Slug (逻辑 ID)**: `[[user-alice-v1]]`

  - **语义**: 指向全局索引中的特定实体。
  - **推荐场景**: 跨文件引用、正式的文档链接。这是最常用的人类可读锚点。

- **Handle (局部句柄)**: `[[alice]]`

  - **语义**: 指向当前文件或当前代码块(Scope)内定义的临时变量名。
  - **推荐场景**: 快速原型开发、模块内部的依赖注入。

- **Hash (内容指纹)**: `[[sha256:8f4b...]]`
  - **语义**: 指向内容的绝对快照。
  - **推荐场景**: 系统级锁定、发布不可变配置包 (Immutable Packages)。它比人为命名的 ID 更安全，优于随机生成的 UUID。

> 详见 [标识符](./identifiers) 了解各类标识符的完整定义。

## 3. 内容寻址 (Content Addressing)

Typedown 支持基于内容的哈希引用。这使得引用可以指向一个**确定性**的数据快照，而非可变的实体。

### 计算逻辑

哈希值由 Entity 代码块的 **规范化 Body (Canonical Body)** 计算得出。

> 算法：`SHA-256( Trim( YAML_Content ) )`

这意味着：只要两个 Block 的有效数据内容一致（不包括 Handle、注释或格式差异），它们的 Hash 就一致。

### 语法示例

```markdown
# 引用特定版本的配置快照，无惧原 ID 被修改

base_config: [[sha256:a1b2c3d4...]]
```

## 4. 在 YAML 数据中使用

Typedown 采用 **"YAML with Sugar"** 策略。虽然标准 YAML 解析器会将 `[[ ]]` 视为嵌套列表，但 Typedown 编译器会在 AST 层面进行**智能解包 (Smart Unboxing)**。

### A. 单值引用 (Single Reference)

```yaml
# 这里的 [[leader]] 在标准 YAML 中是 ["leader"] (List<String>)
# 编译器智能转换为 Reference 对象
manager: [[leader]]
```

### B. 列表引用 (List of References)

这是最显著的语法优化。你不需要编写繁琐的嵌套列表结构。

````markdown
```entity Project: death_star
# 推荐写法 (Block Style)
contributors:
  - [[vader]]
  - [[tarkin]]

# 同时也支持 Flow Style
reviewers: [ [[emperor]], [[thrawn]] ]
```
````

**底层逻辑**:

1. YAML Parser 读取为 `[['vader'], ['tarkin']]`。
2. Typedown Validate 发现字段定义为 `List[Reference[T]]`。
3. 自动执行 Flatten 操作，转换为 `[Ref('vader'), Ref('tarkin')]`。

## 5. 类型安全 (`Reference[T]`)

在 Pydantic 模型中，使用 `Reference` 泛型来强制类型约束。

```python
from typedown.types import Reference

class Task(BaseModel):
    title: str
    # 约束: assignee 必须引用一个 User 类型的实体
    assignee: Reference["User"]
    # 约束: 也可以是多种类型之一
    subscribers: List[Reference["User", "Team"]]
```

### 编译时检查

当用户编写 Entity Block 时，编译器会执行四层检查：

1. **引用存在性 (Existence)**: `[[alice]]` 在当前作用域可见吗？
2. **引用类型 (Type Safety)**: `[[alice]]` 指向的是一个 `User` 吗？如果它是 `Device`，编译报错。
3. **引用数据正确性 (Data Correctness)**: 校验 Entity Block 内的数据是否符合 Model 的 Schema 并通过了所有 validator。

## 6. 引用其他对象

`[[ ]]` 是通用链接语法，支持指向系统中的任何一等公民：

- **Model**: `type: [[User]]` (引用模型/类型定义)
- **Entity**: `manager: [[users/alice]]` (引用具体的数据实例)
- **Spec**: `validates: [[check_age]]` (引用逻辑规格或函数)
- **File**: `assets: [[specs/design.pdf]]` (文件必须作为一等公民，**只能**使用 `[[ ]]` 语法以纳入依赖管理)

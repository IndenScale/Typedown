# 实体引用与链接

Typedown 通过 `[[]]` 语法支持强大的实体引用功能。引用在编译器流水线的 **校验阶段 (Stage 3)** 进行解析，通过拓扑排序确保所有依赖项都已完成物化。

## 1. 引用模式

根据查询结构的组合，引用会解析为不同类型的数据：

### 1.1 符号链接 (`[[ID]]`)

- **行为**：返回目标符号的 **ID 字符串**。
- **用途**：用于建立关联/指针，而不重复数据。
- **示例**：`owner: [[Alice]]` 解析为 `owner: "Alice"`。

### 1.2 数值查找 (`[[ID.path]]`)

- **行为**：导航到目标的内部数据并返回 **具体数值**。
- **索引**：支持通过 `[n]` 进行列表索引。
- **示例**：
  - `[[Project.version]]` -> `"1.0.0"`
  - `[[Farm.apples[0].weight]]` -> `0.5`

### 1.3 数据内联 (`[[ID.path.*]]`)

- **行为**：将目标对象（或子对象）序列化为 **完整字典/对象**。
- **示例**：`config: [[GlobalConfig.*]]` 会深度拷贝整个配置对象。

## 2. 引用解析机制

### 2.1 基于 ID 的精确匹配

引用必须匹配全局符号表中唯一的 `id`。ID 可以定义在：

- Entity 块的 Header (`entity:Type id=X`)。
- Model 块的 Header (`model id=X`)。
- Spec 块的 Header (`spec id=Y`)。

### 2.2 编译流水线

1. **扫描 (Stage 1)**：收集所有符号并构建初始符号表。
2. **链接 (Stage 2)**：解析类型并执行模型。
3. **校验 (Stage 3)**：
   - 构建所有 `[[ ]]` 引用的 **依赖图**。
   - 执行 **拓扑排序**。
   - 检测并报告 **循环依赖**。
   - 按顺序物化数据。

## 3. 引用约束 (Constraints)

编译器在 Stage 3 会强制执行以下约束，任何违反都将导致编译失败：

### 3.1 存在性 (Existence)

引用 `[[ID]]` 中的 ID 必须存在于全局符号表中。

- **错误形式**: `ReferenceError: Symbol 'Ghost' not found.`
- **范围**: 包括 Entity、Model 和 Spec 的 ID。

### 3.2 无环性 (Acyclicity)

实体间的依赖关系不能构成闭环（A -> B -> A）。

- **原因**: 强一致性要求实体必须按依赖顺序进行求值（Evaluation）。
- **错误形式**: `CycleError: Circular dependency detected: A -> B -> A`

### 3.3 类型安全 (Type Safety)

类型检查分为两个层面：

1. **结构类型 (Structural)**:

   - 由 **Pydantic** 原生处理。
   - 检查解析后的值是否符合字段的数据定义（如 `int`, `str`, `List`）。
   - **示例**: `age: [[Alice.name]]` (str) -> 违规 (`expected int`)。

2. **语义类型 (Semantic)**:
   - 由 **编译器** 在 Stage 3 处理。
   - 检查 ID 引用是否指向预期的 Entity Class。
   - **实现机制**: 使用 `Ref[T]` 泛型标记。
   - _注意_: 如果仅在 Model 中定义为 `field: str`，Pydantic 只能校验它是否为字符串，无法校验它是否指向特定类型的实体。严格的实体类型约束依赖于更高级的类型定义（如 `Ref[T]`）。

### 3.4 标准实现: `Ref[T]`

为了桥接 Pydantic 的结构校验与编译器的语义校验，Typedown 提供标准类型 `Ref[T]`。

```python
from typedown import Ref
from typing import Optional

class Project(BaseModel):
    # 运行时: Pydantic 获取 "user_01" 字符串，校验通过。
    # 编译期: Compiler 读取元数据，校验 "user_01" 是否存在且 type=="User"
    owner: Ref["User"]

    # 支持复杂嵌套
    members: list[Ref["User"]]
```

- **本质**: `Ref[T]` 是 `Annotated[str, ReferenceMeta(target=T)]` 的语法糖。
- **优势**: 不需要引入非标准的私有装饰器 (`@check_reference`)，保持了 Model 的纯洁性和标准 Python 类型提示兼容性。

## 4. 工具链支持

LSP (Language Server Protocol) 实现提供：

- **转到定义**：从 `[[ID]]` 跳转到源头代码块。
- **查找所有引用**：查看符号在何处被使用。
- **自动补全**：在键入 `[[` 时从符号表建议 ID。

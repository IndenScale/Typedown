# 特性: Desugar (脱糖与物化)

**状态**: 草稿
**负责人**: 编译器团队

## 1. 目标

Desugar 阶段的职责是将 AST 中零散的、包含隐式依赖的 `EntityBlock` 转换为完整的、扁平化的数据对象。这包括：

1. 解析 `import` 语句，加载 Python Pydantic 类。
2. 构建依赖图 (`former`, `derived_from`)。
3. 按依赖顺序实例化对象，执行**字段合并 (Field Merging)**。
4. 解析引用 (`[[query]]`)。

## 2. 核心算法

### 2.1 依赖图构建

编译器必须遍历全局符号表，构建一个有向图 (DAG)。

- **节点**: Entity IDs
- **边**: `A -> B` (A 依赖于 B)。
  - 如果 A `former` B，则边为 B -> A。
  - 如果 A `derived_from` B，则边为 B -> A。

**循环检测**:
在构建图时，必须检测循环依赖 (A -> B -> A)。如果发现循环，必须抛出 `CircularDependencyError`。

### 2.2 合并策略 (Merge Strategy)

当子对象 (Child) 继承父对象 (Parent) 时，字段值的合并规则如下：

| 字段类型                    | 规则                     | 说明                                                                                                                                                                                                                           |
| :-------------------------- | :----------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scalar** (Int, Str, Bool) | **覆盖 (Override)**      | 子对象的值完全替换父对象。                                                                                                                                                                                                     |
| **List**                    | **覆盖 (Override)**      | **MVP 决策**: 默认为全量替换。如果用户想追加，必须在子对象中重写完整列表。<br>理由：对于 `inventory: ["sword"]` -> `inventory: ["bow"]`，如果默认追加会变成 `["sword", "bow"]`，这可能违背意图（扔了剑换弓）。显式全写更安全。 |
| **Dict / Object**           | **递归合并 (Recursive)** | Key 级别的深度合并。子对象有的 Key 覆盖父对象，没有的 Key 保留父对象。                                                                                                                                                         |
| **None / Missing**          | **继承 (Inherit)**       | 如果子对象未定义该字段，直接沿用父对象的值。                                                                                                                                                                                   |

### 2.3 实例化流程

1.  **拓扑排序**: 对依赖图进行拓扑排序，得到实例化序列 $[E_1, E_2, ..., E_n]$。
2.  **迭代**:
    - 对于 $E_i$：
      1.  检查是否有 Parent (former/derived_from)。
      2.  如果有，获取 Parent 的**已解析数据 (Resolved Data)**。
      3.  获取 $E_i$ 的 **Raw Data**。
      4.  执行 `merge(parent_data, raw_data)`。
      5.  (可选) 此时可以进行初步的 Pydantic 校验（Type Coercion）。
      6.  将结果存入 `symbol_table[id].resolved_data`。

## 3. 导入解析 (Import Resolution)

### 3.1 动态加载机制

编译器需要能够动态加载 Python 模块。

- `Parser` 阶段只提取了字符串 `imports: [{"from": "models.user", "import": "User"}]`。
- `Desugar` 阶段需要：
  1.  将 `models/` 目录加入 `sys.path`。
  2.  使用 `importlib` 动态导入模块。
  3.  获取类对象，存入 `ClassRegistry`。

### 3.2 类匹配

EntityBlock 中的 `class_name` (e.g., "User") 需要在当前文件的 Scope 中查找。

- Scope 是由 `config.td` 和文件级 Front Matter 决定的。
- 编译器需要维护每个 Document 的 **Import Context**。

## 4. 引用解析 (Reference Resolution)

在所有 Entity 实例化完成后，进行引用解析。

- 遍历所有 `Reference` 节点。
- 解析 `query` (e.g., `[[User.name]]`).
- 如果 `query` 是 ID，检查符号表。
- 如果 `query` 包含属性访问，在 `resolved_data` 中查找。
- 更新 `Reference` 节点的 `resolved_entity_id` 和 `resolved_value`。

## 5. 验收标准 (Acceptance Criteria)

1. 能够正确处理 3 层以上的继承链 (A -> B -> C)。
2. 能够正确报错循环依赖。
3. List 字段正确执行“覆盖”操作。
4. 能够动态加载 `models/` 下的 Pydantic 类。

# Typedown 中间表示 (IR)

Typedown IR 是一组结构化数据模型，代表项目在解析和链接解析后的语义内容。它是 **前端 (Parser)** 与 **后端 (Spec Runner/Validator)** 之间的语言中立表示。

## 1. 节点层级

所有 IR 节点都继承自基础 `Node` 类。

### 1.1 基础节点 (Base Node)

| 字段       | 类型                       | 描述                                 |
| :--------- | :------------------------- | :----------------------------------- |
| `id`       | `Optional[str]`            | 该符号的唯一标识符。                 |
| `location` | `Optional[SourceLocation]` | 文件路径和行号范围，用于诊断和 LSP。 |

## 2. 语义节点 (Semantic Nodes)

### 2.1 EntityDef

代表一个数据实例。

- **Payload**: `data: Dict[str, Any]` (YAML 解析后的内容)。
- **Type**: `type_name: str` (关联的模型名称)。

### 2.2 ModelDef

代表一个 Pydantic/Python 模型块。

- **Payload**: `code: str`。

### 2.3 SpecDef

代表一个测试/验证块。

- **Payload**: `code: str` (Python) 或 `data: Dict` (YAML)。
- **Name**: `name: str`。

### 2.4 ImportStmt

代表虚拟或物理导入。

- **Source**: `source: str` (例如 `@lib.math`)。
- **Names**: `List[str]` (导入的符号列表)。

## 3. 文档 (Document)

`Document` 是单个物理文件的根容器。

- **Path**: `Path`。
- **Collections**: `imports`, `models`, `entities`, `specs`, `references`。

## 4. 符号表 (Symbol Table)

**编译器** 维护一个全局符号表 (`ID -> Node` 映射)。

- 所有带有 `id` 的 `EntityDef`, `ModelDef` 和 `SpecDef` 节点都会在此注册。
- `Evaluator` 使用此表来解析 `[[ID]]` 查询。

# 逻辑规范 (Spec)

`spec` 块用于定义复杂的逻辑校验规则。不同于 Model 内部的字段校验，Spec 运行在图谱构建完成之后，因此它可以访问全局上下文，验证跨实体的关系、执行聚合计算以及进行复杂的一致性检查。

## 语法签名 (Block Signature)

````typedown
```spec:<TestID>
@target(...)
def <TestID>(subject):
    ...
```
````

### 签名严格化要求

在 v0.2.13+ 版本中，Typedown 强化了块签名的校验逻辑：

- **命名一致性 (Signature Consistency)**: **Block ID** (`TestID`) 必须与块内 Python 代码定义的校验函数名**完全一致**。这确保了文档结构与代码逻辑的强绑定。
- **ID 字符限制**: 标识符仅允许包含字母、数字、下划线 `_` 和连字符 `-`（正则表达式：`[a-zA-Z0-9_\-]+`）。
- **空格不敏感**: 关键字 `spec` 与冒号 `:` 之间、冒号与 ID 之间的空格不再敏感。例如 `spec:my_test`、`spec : my_test` 均被视为等效合规。

- **关键字**: `spec`
- **标识符**: `<TestID>` 是该测试用例的唯一名称。
- **内容**: Python 代码，基于 Pytest 风格。

## 目标选择 (@target)

使用 `@target` 装饰器来声明该测试应用于哪些实体。

```python
@target(type="User", scope="local")
def check_user_consistency(subject: User):
    ...
```

### 参数详解

- **type**: 按模型类型过滤。支持字符串（如 `"User"`）。
- **tag** (可选): 按实体标签过滤。
- **scope** (可选): 控制执行频率与范围。
  - `"local"` (默认): **单体模式**。为每个匹配的实体运行一次测试，`subject` 即为当前实体。
  - `"global"`: **全局模式**。无论匹配到多少个实体，该测试仅运行一次。常用于聚合校验（如“总金额限制”）。`subject` 会传入第一个匹配到的实体（作为代表），或者在编写时忽略它。

## 编写断言

Spec 函数接收一个 `subject` 参数（实例化后的 Pydantic 对象）。你可以使用标准的 Python `assert` 语句：

```python
def check_admin_mfa(subject: User):
    if subject.role == "admin":
        # 如果断言失败，编译器会报告错误，并包含该消息
        assert subject.mfa_enabled, f"管理员 {subject.name} 未开启 MFA"
```

## 访问上下文 (Context Access)

Spec 环境通过注入强大的内置函数来打破“数据孤岛”：

### `query(selector)`

用于简单查询或基于 ID 的访问。支持 ID 引用、属性路径等。

- **参数**: `selector` (字符串)，支持：
  - **ID 引用**: `"user-alice"`, `"[[user-alice]]"`
  - **属性路径**: `"user-alice.profile.email"`
  - **文件路径**: `"assets/logo.png"`
- **返回**: 匹配的对象（Entity, Resource 或属性值）。如果未找到，抛出异常。

```python
@target(type="User")
def check_manager_relationship(subject):
    # 获取 Manager 的 ID (假设 subject.manager 存储的是 "users/bob" 这样的引用字符串)
    manager_id = subject.manager

    # 使用 query() 查找 Manager 实体
    # 注意：如果 Reference 已经由 Linker 解析，subject.manager 可能已经是实体对象了。
    # 但如果它是原始字符串，或者你需要反向查找，query() 非常有用。

    manager = query(manager_id)
    assert manager.department == subject.department
```

### `sql(query_string)`

集成 **DuckDB** 引擎，支持对全域实体进行高速 SQL 查询。这是处理 ERP 业务中“聚合校验”的首选方式。

```python
@target(type="Item", scope="global")
def check_total_inventory_cap(subject):
    # 查询所有 Item 的重量总和
    result = sql("SELECT sum(weight) as total FROM Item")
    total_weight = result[0]['total']

    limit = 10000
    assert total_weight <= limit, f"总库存重量 {total_weight} 超过上限 {limit}"
```

## 错误归因与诊断 (Diagnostics)

Typedown 提供了精准的报错机制，确保在复杂规则失败时能够快速定位。

### 1. 归因 (Blame)

在执行聚合规则时，如果发现错误，你可以使用 `blame()` 函数明确指出是哪些实体导致了失败，避免“全屏报红”。

```python
@target(type="Item", scope="global")
def check_weight_limit(subject):
    # 查找所有超重的实体
    overweight_items = sql("SELECT id, weight FROM Item WHERE weight > 500")

    for item in overweight_items:
        # 仅让超重的实体报错，而不是所有 Item
        blame(item['id'], f"单项重量 {item['weight']} 超过警戒线 500")

    assert not overweight_items
```

### 2. 双向诊断反馈

当 Spec 失败时，IDE 会同时在两个地方显示错误：

- **规则视角**: `spec` 块中的具体 `assert` 行（通过 Traceback 解析精确定位）。
- **数据视角**: 受影响的 `entity` 块定义处。

## 导入规范

为了保持 Spec 的灵活性，Spec 块允许使用 `import` 语句导入本地模块。这与 `model` 块的严格限制不同（Model 块禁止导入以确保 Schema 的纯粹性）。

## 最佳实践

- **优先使用 SQL**: 对于涉及多个实体的统计、过滤，`sql()` 比循环调用 `query()` 效率更高。
- **合理使用 Global Scope**: 聚合规则务必声明 `scope="global"`，避免重复执行 N 次导致的性能浪费。
- **善用 Blame**: 在聚合校验中，如果不调用 `blame`，错误可能会广播给所有匹配的实体；使用 `blame` 可以显著降低干扰，提升用户体验。
- **保持 Read-only**: 严禁在 Spec 中修改 `subject` 的属性或进行任何具有副作用的操作。

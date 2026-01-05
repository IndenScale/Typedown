---
title: 逻辑规范
---

## 逻辑规范 (Spec)

`spec` 块用于定义复杂的逻辑校验规则。不同于 Model 内部的字段校验，Spec 运行在图谱构建完成之后，因此它可以访问全局上下文，验证跨实体的关系。

## 语法签名

````typedown
```spec: <TestID>
@target(...)
def test_function(subject):
    ...
```
````

- **关键字**: `spec`
- **标识符**: `<TestID>` 是该测试用例的唯一名称。
- **内容**: Python 代码，基于 Pytest 风格。

## 目标选择 (@target)

使用 `@target` 装饰器来声明该测试应用于哪些实体。

```python
@target(type="User")
def check_user_consistency(subject: User):
    ...
```

- **type**: 按模型类型过滤。
- **tag** (可选): 按实体标签过滤。

## 编写断言

Spec 函数接收一个 `subject` 参数，它是被测试实体的实例化对象（Pydantic Model Instance）。

你可以使用标准的 Python `assert` 语句：

```python
def check_admin_mfa(subject: User):
    if subject.role == "admin":
        # 如果断言失败，编译器会报告错误，并包含该消息
        assert subject.mfa_enabled, f"管理员 {subject.name} 未开启 MFA"
```

## 访问上下文 (Context Access)

Spec 代码运行在一个受限的 Python 环境中，除了 `subject` 之外，还可以使用 `query()` 函数来查找图谱中的其他节点。

### `query(selector)`

用于在全局范围内查找实体或资源。

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

## 最佳实践

- **保持纯函数**: Spec 应当是无副作用的（Read-only）。不要在 Spec 中修改实体数据。
- **原子性**: 每个 Spec 应该只测试一个逻辑规则。
- **避免过度查询**: `query()` 虽然强大，但过度使用可能导致性能问题。对于紧密关联的对象，尽量利用 Linker 自动解析的引用。

---
title: 逻辑规范
---

# 逻辑规范 (Spec)

`spec` 块用于定义复杂的逻辑校验规则。不同于 Model 内部的字段校验，Spec 运行在图谱构建完成之后，因此它可以访问全局上下文，验证跨实体的关系。

## 语法签名

```markdown
```spec:<TestID>
@target(...)
def test_function(subject):
    ...
```
```

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

## 访问上下文

Spec 代码运行在一个受限的 Python 环境中，但可以访问：

- `subject`: 当前被测试的实体。
- 全局符号表：可以通过 `typelib` 或其他注入变量访问图谱中的其他节点。

## 最佳实践

- **保持纯函数**: Spec 应当是无副作用的（Read-only）。不要在 Spec 中修改实体数据。
- **原子性**: 每个 Spec 应该只测试一个逻辑规则。

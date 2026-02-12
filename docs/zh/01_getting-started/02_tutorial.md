---
title: 快速开始
---

# 快速开始

本教程将指导你掌握 Typedown 的核心工作流程：**编写 Markdown，即时获得反馈**。

## 1. 安装

### 安装 CLI

需要 Python 3.12+：

```bash
pip install typedown
```

### 安装 VS Code 扩展

在 VS Code 插件市场搜索 `Typedown` 并安装。

## 2. Hello World

创建一个新目录和 `hello.td` 文件（Typedown 使用 `.td` 扩展名，完全兼容 Markdown）：

### 步骤 1：定义模型

在 Typedown 中，一切从 **Model** 开始。告诉系统 `User` 应该长什么样：

````typedown
```model:User
class User(BaseModel):
    name: str
    role: str
```
````

这里使用 `model` 代码块，以 Pydantic 风格定义 `User` 类。

### 步骤 2：创建实体

模型定义后，可以实例化数据：

````typedown
```entity User: alice
name: "Alice"
role: "admin"
```
````

使用 `entity` 代码块创建类型为 `User`、ID 为 `alice` 的实体。

## 3. 获取反馈

在终端运行检查：

```bash
typedown check .
```

看到 **No errors found** 🎉 表示验证通过！

这就是 Typedown 的核心理念：**强类型 Markdown**。

如果你尝试修改 `alice` 的 `age`（未定义字段）或将 `name` 改为数字，`typedown check` 会立即报错。

## 4. 添加验证规则

定义 `spec` 来检查复杂规则：

````typedown
```spec:check_admin_mfa
@target(type="User")
def check_admin_mfa(user: User):
    if user.role == "admin":
        assert user.mfa_enabled, f"管理员 {user.name} 必须启用 MFA"
```
````

现在如果 `alice` 的角色是 `admin` 但没有 `mfa_enabled` 字段，将会报错。

## 5. 下一步

你已掌握 Typedown 的核心循环：**定义模型 → 创建实体 → 验证反馈**。

- 👉 [模型与实体](../concepts/model-and-entity) - 深入了解数据结构
- 👉 [验证规则](../concepts/validation) - 学习编写复杂的验证逻辑

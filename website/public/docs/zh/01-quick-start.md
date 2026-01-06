---
title: 快速开始
---

# 快速开始 (Quick Start)

欢迎来到 Typedown。本教程将带你体验 Typedown 的核心工作流：**编写 Markdown，即时获得反馈**。

## 1. 安装

Typedown 提供了命令行工具 (CLI) 和 VS Code 插件。

### 安装 CLI

需要 Python 3.12+。

```bash
pip install typedown
```

### 安装 VS Code 插件

在 VS Code 插件市场搜索 `Typedown` 并安装。

## 2. Hello World

创建一个新目录，并新建文件 `hello.td` (Typedown 使用 `.td` 扩展名，完全兼容 Markdown)。

### 第一步：定义模型 (Model)

在 Typedown 中，一切始于**模型**。我们需要先告诉系统 `User` 长什么样。

在 `hello.td` 中输入以下内容：

````markdown
```model:User
class User(BaseModel):
    name: str
    role: str
```
````

这里我们使用了 `model` 块，采用 Pydantic 风格定义了一个简单的 `User` 类。

### 第二步：创建实体 (Entity)

有了模型，我们就可以实例化数据了。在同一个文件中添加：

````markdown
```entity User: alice
name: "Alice"
role: "admin"
```
````

这里我们使用了 `entity` 块，创建了一个类型为 `User` 的实体，ID 为 `alice`。

## 3. 获得反馈

在终端中运行检查：

```bash
td check .
```

你会看到 Typedown 扫描了当前目录，并报告：**No errors found**。🎉

这就是 Typedown 的核心体验：**强类型的 Markdown**。

如果你尝试修改 `alice` 的 `age` (一个未定义的字段)，或者将 `name` 改为数字，`td check` 会立即报错。

## 4. 下一步

你已经掌握了 Typedown 的核心循环：**定义模型 -> 创建实体 -> 校验反馈**。

👉 前往 [语法基础](/zh/docs/syntax/code-blocks) 深入了解更多细节。

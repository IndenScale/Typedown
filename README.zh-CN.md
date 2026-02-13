# <picture><source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-dark.svg"><img alt="Typedown Logo" src="assets/brand/logo-light.svg" height="30"></picture> Typedown

> **Markdown 渐进式形式化**

[**🚀 安装 VS Code 扩展**](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode) · [**文档**](https://typedown.io/docs) · [**问题反馈**](https://github.com/IndenScale/Typedown/issues)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) [![PyPI](https://img.shields.io/pypi/v/typedown.svg)](https://pypi.org/project/typedown/)

> [English](./README.md) | **简体中文**

**Typedown** 为 Markdown 添加语义层，将松散的文本转化为可验证的知识库。

> 💡 **Typedown 文件 (`.td`) 专为 IDE 体验设计。** 安装 [VS Code 扩展](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode) 以获得实时验证、智能跳转和语义高亮。

## 问题：Markdown 难以规模化

Markdown 是技术文档的通用标准。但当仓库从 10 个文件增长到 10,000 个时，它变成了"只写"的坟场：

| 问题 | 描述 | Typedown 解决方案 |
| --- | --- | --- |
| **Schema 错误** | 数据不一致：`Status: Active` vs `status: active`，缺少必填字段 | **Model** - 使用 Pydantic 定义结构，编译时验证 |
| **引用失效** | 移动文件后链接断裂：`[[./old-path]]` 指向不存在的位置 | **Reference** - 基于内容哈希的寻址，自动追踪实体变更 |
| **约束违反** | 规则被打破：管理员未启用 MFA，库存总量超标 | **Spec** - 可执行的业务规则，验证复杂约束 |

## 核心概念

### 1. Model（模型）

使用 Pydantic 定义数据结构：

````typedown
```model:User
class User(BaseModel):
    name: str
    role: Literal["admin", "member"]
    mfa_enabled: bool = False
```
````

### 2. Entity（实体）

使用严格 YAML 实例化数据：

````typedown
```entity User: user-alice-v1
name: "Alice"
role: "admin"
mfa_enabled: true
```
````

### 3. Reference（引用）

使用 `[[...]]` 语法建立实体链接：

```typedown
此任务分配给 [[user-alice-v1]]。
```

支持 **ID 引用**（`[[entity-id]]`）和 **内容哈希**（`[[sha256:...]]`）。

### 4. Spec（验证规则）

三层验证机制：

````typedown
# 1. 字段级 - @field_validator
class User(BaseModel):
    @field_validator('email')
    def check_email(cls, v):
        assert '@' in v, "邮箱格式无效"
        return v

# 2. 模型级 - @model_validator
class Order(BaseModel):
    @model_validator(mode='after')
    def check_dates(self):
        assert self.end > self.start, "结束时间必须晚于开始"
        return self

# 3. 全局级 - spec
```spec:check_admin_mfa
@target(type="User", scope="local")
def check_admin_mfa(user: User):
    if user.role == "admin":
        assert user.mfa_enabled, f"管理员 {user.name} 必须启用 MFA"
```
````

## 快速开始

### 方式一：VS Code 扩展（推荐）

体验 Typedown 的最佳方式是通过 IDE 扩展，它提供实时验证、跳转到定义和语义高亮。

1. **安装 [VS Code 扩展](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)**
2. **克隆本仓库** 并在 VS Code 中打开 `cookbook/01_getting_started/` 文件夹
3. 打开任意 `.td` 文件即可体验 Typedown

> ⚠️ **注意：** Typedown 文件 (`.td`) 在 GitHub 上显示为普通 Markdown。完整体验需要 VS Code 扩展。

### 方式二：CLI 工具（用于 CI/CD）

用于在 CI 流水线或自动化中验证 Typedown 文件：

```bash
# 使用 uv（推荐）
uv tool install typedown

# 使用 pip
pip install typedown

# 验证项目
typedown check .
```

## CLI 命令

```bash
# 验证项目
typedown check .

# JSON 格式输出
typedown check --json

# 仅验证指定类型
typedown check --target User
```

## 文档

- [**快速开始**](https://typedown.io/docs/getting-started/) - 构建你的第一个模型
- [**核心概念**](https://typedown.io/docs/concepts/) - Model、Entity、Reference、Spec
- [**使用指南**](https://typedown.io/docs/guides/) - 最佳实践和高级主题

## 教程与案例

[`cookbook/`](./cookbook/) 目录包含配合 VS Code 扩展使用的学习资源：

- **`cookbook/01_getting_started/`** - 渐进式入门教程（中英文）
- **`cookbook/02_use_cases/`** - 实战用例（评标系统、PMO SaaS、ERP 等）

> 💡 **提示：** 克隆仓库并在安装 Typedown 扩展的 VS Code 中打开，以获得最佳学习体验。

## 许可证

MIT © [IndenScale](https://github.com/IndenScale)

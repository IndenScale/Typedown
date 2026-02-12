# <picture><source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-dark.svg"><img alt="Typedown Logo" src="assets/brand/logo-light.svg" height="30"></picture> Typedown

> **Markdown 渐进式形式化**

[**官网**](https://typedown.io) · [**文档**](https://typedown.io/docs) · [**问题反馈**](https://github.com/IndenScale/Typedown/issues)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/typedown.svg)](https://pypi.org/project/typedown/)

> [English](./README.md) | **简体中文**

**Typedown** 为 Markdown 添加语义层，将松散的文本转化为可验证的知识库。

## 问题：Markdown 难以规模化

Markdown 是技术文档的通用标准。但当仓库从 10 个文件增长到 10,000 个时，它变成了"只写"的坟场：

| 问题 | 描述 | Typedown 解决方案 |
|------|------|-------------------|
| **Schema 错误** | 数据不一致：`Status: Active` vs `status: active`，缺少必填字段 | **Model** - 使用 Pydantic 定义结构，编译时验证 |
| **引用失效** | 移动文件后链接断裂：`[[./old-path]]` 指向不存在的位置 | **Reference** - 基于内容哈希的寻址，自动追踪实体变更 |
| **约束违反** | 规则被打破：管理员未启用 MFA，库存总量超标 | **Spec** - 可执行的业务规则，验证复杂约束 |

## 核心概念

### 1. Model（模型）

使用 Pydantic 定义数据结构：

````markdown
```model:User
class User(BaseModel):
    name: str
    role: Literal["admin", "member"]
    mfa_enabled: bool = False
```
````

### 2. Entity（实体）

使用严格 YAML 实例化数据：

````markdown
```entity User: user-alice-v1
name: "Alice"
role: "admin"
mfa_enabled: true
```
````

### 3. Reference（引用）

使用 `[[...]]` 语法建立实体链接：

```markdown
此任务分配给 [[user-alice-v1]]。
```

支持 **ID 引用**（`[[entity-id]]`）和 **内容哈希**（`[[sha256:...]]`）。

### 4. Spec（验证规则）

三层验证机制：

````markdown
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

## 安装

### CLI 工具（用于 CI/CD）

```bash
# 使用 uv（推荐）
uv tool install typedown

# 使用 pip
pip install typedown
```

### VS Code 扩展

- [**VS Code Marketplace**](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)
- [**Open VSX**](https://open-vsx.org/extension/Typedown/typedown-vscode)

## 快速开始

创建 `hello.td` 文件（Typedown 使用 `.td` 扩展名，完全兼容 Markdown）：

````markdown
```model:User
class User(BaseModel):
    name: str
    email: str
```

```entity User: alice
name: "Alice"
email: "alice@example.com"
```
````

运行验证：

```bash
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

## 许可证

MIT © [IndenScale](https://github.com/IndenScale)

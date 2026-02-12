---
title: 介绍
---

# Typedown

> **Markdown 类型化系统**

**Typedown** 是一个基于 Markdown 的结构化文档工具，旨在通过语义层将松散的文本转化为结构化的数据。

## 为什么需要 Typedown？

Markdown 是技术文档的通用标准，但在大规模使用时，三类错误难以避免：

| 错误类型 | 问题描述 | Typedown 解决方案 |
|----------|----------|-------------------|
| **Schema 错误** | 数据格式不一致：`Status: Active` vs `status: active`，缺少必填字段 | **Model** - 使用 Pydantic 定义数据结构，编译时验证 |
| **引用失效** | 链接断裂：移动文件后 `[[./old-path]]` 指向不存在的位置 | **Reference** - 基于内容哈希的寻址，自动追踪实体变更 |
| **业务逻辑约束违反** | 规则被打破：管理员未启用 MFA，库存总量超标 | **Spec** - 可执行的业务规则，实时验证复杂约束 |

Typedown 通过这三层语义，将 Markdown 从「松散文本」转变为「可验证的知识库」。

## 核心概念

### 1. 结构 (Schema)

使用 Python (Pydantic) 定义数据结构：

````typedown
```model:User
class User(BaseModel):
    name: str
    role: Literal["admin", "member"]
```
````

### 2. 空间 (Graph)

使用 **ID** 或 **内容哈希** 建立实体间的链接：

```typedown
这份报告由 [[user-alice-v1]] 撰写。
```

### 3. 逻辑 (Validation)

三层验证，从单字段到全局聚合：

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
```spec:check_inventory
@target(type="Item", scope="global")
def check_total_weight(subject):
    total = sql("SELECT sum(weight) FROM Item")[0]['total']
    assert total <= 10000, "总重量超过限制"
```
````

## 安装

### VS Code 扩展（推荐）

- [**VS Code Marketplace**](https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode)
- [**Open VSX**](https://open-vsx.org/extension/Typedown/typedown-vscode)

### CLI 工具

```bash
# 即时运行（无需安装）
uvx typedown check

# 全局安装
uv tool install typedown
```

### 开发者

```bash
git clone https://github.com/IndenScale/typedown.git
```

## 下一步

👉 [快速开始教程](./tutorial) - 构建你的第一个模型

---
title: 验证规则
---

# 验证规则

Typedown 提供三层验证，从单字段到全局聚合：

| 层级 | 机制 | 范围 | 典型场景 |
|------|------|------|----------|
| **字段级** | `@field_validator` | 单个字段 | 邮箱格式、数值范围 |
| **模型级** | `@model_validator` | 单个实体 | 多字段联合约束 |
| **全局级** | `spec` | 整个图谱 | 聚合统计、跨实体规则 |

---

## 1. 字段级验证（Field Validator）

使用 Pydantic 的 `@field_validator` 验证单个字段的值：

```python
from pydantic import field_validator

class User(BaseModel):
    email: str
    age: int
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('邮箱格式无效')
        return v
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError('年龄范围无效')
        return v
```

---

## 2. 模型级验证（Model Validator）

使用 `@model_validator` 验证单个实体内部的多字段联合约束：

```python
from pydantic import model_validator

class TimeRange(BaseModel):
    start: datetime
    end: datetime
    
    @model_validator(mode='after')
    def check_time_order(self):
        if self.end <= self.start:
            raise ValueError('结束时间必须晚于开始时间')
        return self
```

模型级验证按引用遍历实体图谱，确保每个实体实例的内部一致性。

---

## 3. 全局级验证（Spec）

`spec` 代码块用于定义需要**全局聚合统计**的复杂约束，基于 Pytest 风格编写。

### 语法

````typedown
```spec:<TestID>
@target(type="ModelName", scope="local|global")
def <TestID>(subject):
    assert condition, "错误信息"
```
````

### Local Scope（局部模式）

为每个匹配实体执行一次，验证实体级别的业务规则：

```python
@target(type="User", scope="local")
def check_admin_mfa(subject: User):
    """每个管理员都必须启用 MFA"""
    if subject.role == "admin":
        assert subject.mfa_enabled, f"管理员 {subject.name} 必须启用 MFA"
```

### Global Scope（全局模式）

整个图谱只执行一次，适合**聚合统计**类约束：

```python
@target(type="Item", scope="global")
def check_total_weight_limit(subject):
    """所有 Item 的总重量不能超过限制"""
    result = sql("SELECT sum(weight) as total FROM Item")
    total = result[0]['total']
    assert total <= 10000, f"总重量 ({total}) 超过限制 10000"
```

### 全局验证的工具

#### `query(selector)`

用于简单的 ID 查询或属性访问：

```python
user = query("user-alice-v1")
managers = query("users/*.manager")
```

#### `sql(query_string)`

集成 **DuckDB** 引擎，处理 SQL 聚合查询：

```python
@target(type="Order", scope="global")
def check_daily_order_limit(subject):
    # 统计今日订单总数
    result = sql("""
        SELECT count(*) as cnt FROM Order 
        WHERE created_at >= date('now')
    """)
    assert result[0]['cnt'] <= 1000, "今日订单数超过限制"
```

#### `blame(entity_id, message)`

全局验证失败时，指定具体责任实体：

```python
@target(type="Item", scope="global")
def check_weight_limit(subject):
    overweight = sql("SELECT id, weight FROM Item WHERE weight > 500")
    
    for item in overweight:
        blame(item['id'], f"重量 {item['weight']} 超过阈值 500")
    
    assert not overweight
```

### 诊断显示

Spec 失败时，IDE 会在两处标记：
- **规则视图**：`spec` 块中的具体 `assert` 行
- **数据视图**：被 `blame` 的实体定义

---

## 验证策略选择

| 场景 | 推荐方式 | 示例 |
|------|----------|------|
| 单字段格式检查 | `@field_validator` | 邮箱格式、手机号 |
| 多字段联合检查 | `@model_validator` | 结束时间 > 开始时间 |
| 跨实体关系检查 | `spec` + `scope="local"` | 引用的实体是否存在 |
| 聚合统计约束 | `spec` + `scope="global"` + `sql()` | 总重量、平均值 |
| 全局唯一性检查 | `spec` + `scope="global"` | 用户名全局唯一 |

---

## CI/CD 集成

```bash
# 检查并输出 JSON
typedown check --json

# 过滤特定错误码
typedown check --json | jq '.diagnostics[] | select(.code == "E0103")'

# 仅显示错误（排除警告）
typedown check --json | jq '.diagnostics[] | select(.level == "error")'
```

### 预提交钩子

```yaml
- repo: local
  hooks:
    - id: typedown-check
      name: Typedown Check
      entry: typedown check
      language: system
      files: \.td$
```

---
title: 验证规则
---

# 验证规则

Typedown 提供两层验证：**字段验证**（Model 内）和 **规则验证**（Spec 全局）。

## 1. 字段验证（Model Validator）

在 Model 定义内部，确保单体数据完整性。

### 字段级验证

```python
from pydantic import field_validator

class User(BaseModel):
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('邮箱格式无效')
        return v
```

### 模型级验证

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

---

## 2. 规则验证（Spec）

`spec` 代码块用于定义复杂逻辑验证，在图谱构建完成后运行，可访问全局上下文。

### 语法

````typedown
```spec:<TestID>
@target(...)
def <TestID>(subject):
    ...
```
````

### 目标选择（@target）

```python
@target(type="User", scope="local")
def check_user_consistency(subject: User):
    ...
```

**参数**：
- `type`: 按模型类型过滤（如 `"User"`）
- `tag`（可选）: 按实体标签过滤
- `scope`（可选）:
  - `"local"`（默认）：实例模式，为每个匹配实体运行一次
  - `"global"`：全局模式，仅运行一次（适合聚合检查）

### 断言编写

使用标准 Python `assert`：

```python
def check_admin_mfa(subject: User):
    if subject.role == "admin":
        assert subject.mfa_enabled, f"管理员 {subject.name} 必须启用 MFA"
```

### 上下文访问

#### `query(selector)`

简单查询或 ID 访问：

```python
user = query("users/alice")
```

#### `sql(query_string)`

集成 **DuckDB** 引擎，处理聚合查询：

```python
@target(type="Item", scope="global")
def check_total_inventory(subject):
    result = sql("SELECT sum(weight) as total FROM Item")
    total = result[0]['total']
    assert total <= 10000, f"总重量 ({total}) 超过限制"
```

### 错误归因（Blame）

聚合规则失败时，使用 `blame()` 指定责任实体：

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

### 最佳实践

| 场景 | 推荐方式 |
|------|----------|
| 单字段约束 | `@field_validator` |
| 多字段联合约束 | `@model_validator` |
| 跨实体关系检查 | `spec` + `query()` |
| 聚合统计检查 | `spec` + `sql()` |
| 外部数据验证 | `spec` + Oracle（待实现） |

---

## 3. 质量控制策略

### CI/CD 集成

```bash
# 检查并输出 JSON
typedown check --json

# 过滤特定错误码
typedown check --json | jq '.diagnostics[] | select(.code == "E0103")'

# 仅显示错误（排除警告）
typedown check --json | jq '.diagnostics[] | select(.level == "error")'
```

### 错误级别

- **Error**: 严重错误，阻止执行
- **Warning**: 潜在问题，执行继续
- **Info**: 信息性消息
- **Hint**: 改进建议

### 预提交钩子

在 `.pre-commit-config.yaml` 中添加：

```yaml
- repo: local
  hooks:
    - id: typedown-check
      name: Typedown Check
      entry: typedown check
      language: system
      files: \.td$
```

# Typedown 错误码对照表

本文档描述了 Typedown 编译器使用的结构化错误码系统。

## 错误码格式

错误码格式为：`E{stage}{category}{number}`

- **Stage** (第2-3位): 编译阶段
  - `01` = L1 Scanner (扫描阶段)
  - `02` = L2 Linker (链接阶段)
  - `03` = L3 Validator (验证阶段)
  - `04` = L4 Spec (规范阶段)
  - `09` = System (系统错误)

- **Category** (第4位): 错误类别
  - `0-1` = Syntax/Parse (语法/解析错误)
  - `2-3` = Execution (执行错误)
  - `4-5` = Reference/Link (引用/链接错误)
  - `6-7` = Schema/Type (模式/类型错误)
  - `8-9` = System (系统错误)

- **Number** (第5位): 序号 (1-9)

## 错误级别

每个错误都有一个级别：

- **Error** (error) - 严重错误，阻止执行
- **Warning** (warning) - 潜在问题，执行继续
- **Info** (info) - 信息性消息
- **Hint** (hint) - 改进建议

## 错误码列表

### L1: Scanner 错误 (E01xx)

| 错误码 | 级别 | 描述 |
|--------|------|------|
| E0101 | Error | 语法解析失败 |
| E0102 | Error | 配置块位置错误 (config blocks 只能在 config.td 中) |
| E0103 | Error | 嵌套列表反模式 |
| E0104 | Error | 文件读取错误 |
| E0105 | Error | 文档结构错误 |

### L2: Linker 错误 (E02xx)

| 错误码 | 级别 | 描述 |
|--------|------|------|
| E0221 | Error | 模型执行失败 |
| E0222 | Error | 配置执行失败 |
| E0223 | Warning | Prelude 符号加载失败 |
| E0224 | Warning | 模型重建失败 |
| E0231 | Error | 模型块 ID 与定义的类名不匹配 |
| E0232 | Error | 模型使用了保留字段 'id' |
| E0233 | Error | 无效的模型类型 (不是 BaseModel 或 Enum) |
| E0241 | Error | 重复的 ID 定义 |

### L3: Validator 错误 (E03xx)

| 错误码 | 级别 | 描述 |
|--------|------|------|
| E0341 | Error | 引用解析失败 |
| E0342 | Error | 检测到循环依赖 |
| E0343 | Error | 演进 (Evolution) 目标未找到 |
| E0361 | Error | Schema 验证失败 |
| E0362 | Error | Ref[T] 类型不匹配 |
| E0363 | Error | ID 冲突 (系统 ID 必须在签名中定义，不能在 body 中) |
| E0364 | Error | 模型类未找到 |
| E0365 | Error | 查询语法错误 |

### L4: Spec 错误 (E04xx)

| 错误码 | 级别 | 描述 |
|--------|------|------|
| E0421 | Error | Spec 执行失败 |
| E0422 | Error | Oracle 执行失败 |
| E0423 | Warning | Spec 目标未找到 |
| E0424 | Error | Spec 断言失败 |

### System 错误 (E09xx)

| 错误码 | 级别 | 描述 |
|--------|------|------|
| E0981 | Error | 内部编译器错误 |
| E0982 | Error | 文件系统错误 |
| E0983 | Error | 配置错误 |

## 在代码中使用错误码

### 创建错误

```python
from typedown.core.base.errors import (
    TypedownError, ErrorCode, ErrorLevel,
    scanner_error, linker_error, validator_error, spec_error
)

# 方法1: 使用工厂函数 (推荐)
error = scanner_error(
    ErrorCode.E0103,
    entity_id="my_entity",
    location=entity.location
)

# 方法2: 使用模板
error = TypedownError.from_template(
    ErrorCode.E0362,
    field="manager",
    expected="UserAccount",
    value="org-123",
    actual="Organization",
    location=entity.location
)

# 方法3: 直接创建
error = TypedownError(
    message="自定义错误消息",
    code=ErrorCode.E0981,
    level=ErrorLevel.ERROR,
    location=source_location,
    details={"custom": "data"}
)
```

### 向后兼容

为了向后兼容，旧的 `severity` 参数仍然可用：

```python
# 旧代码 (仍然工作)
error = TypedownError(
    message="Error message",
    severity="warning"  # 自动转换为 ErrorLevel.WARNING
)
```

### 序列化到 JSON

错误对象可以通过 `to_dict()` 方法序列化为字典：

```python
error_dict = error.to_dict()
# {
#     "code": "E0101",
#     "level": "error",
#     "severity": "error",
#     "message": "Parse error: ...",
#     "stage": "L1-Scanner",
#     "category": "Syntax/Parse",
#     "location": {...},
#     "details": {...}
# }
```

### 诊断报告

使用 `DiagnosticReport` 来收集和管理诊断：

```python
from typedown.core.base.errors import DiagnosticReport

report = DiagnosticReport()
report.add(error)
report.extend(list_of_errors)

# 检查是否有错误
if report.has_errors():
    # 处理错误
    pass

# 按级别过滤
errors = report.by_level(ErrorLevel.ERROR)
warnings = report.by_level(ErrorLevel.WARNING)

# 按阶段过滤
scanner_errors = report.by_stage("L1-Scanner")

# 转换为字典列表
json_list = report.to_dict_list()
```

## CI/CD 集成

错误码系统设计用于 CI/CD 集成：

```bash
# 编译并检查特定错误码
$ typedown check --json | jq '.diagnostics[] | select(.code == "E0103")'

# 统计各阶段错误数量
$ typedown check --json | jq '.summary.by_stage'

# 只显示错误 (排除警告)
$ typedown check --json | jq '.diagnostics[] | select(.level == "error")'
```

## LSP 集成

错误码会显示在 LSP 诊断消息中：

```
[E0103] Nested list anti-pattern detected: Nested list detected in entity 'X'. Consider extracting to a separate Model.
```

这样用户可以快速识别错误类型并查阅文档。

---
title: 配置系统
---

# 配置系统

Typedown 提供两层配置：**config 代码块**（目录级）和 **Front Matter**（文件级）。

## 1. Config 代码块

`config` 代码块用于配置编译器的运行时环境，通常出现在 `config.td` 文件中。

### 语法

````typedown
```config python
<Setup Script>
```
````

- **关键字**: `config`
- **语言**: 目前仅支持 `python`
- **位置限制**: 通常仅允许出现在 `config.td` 文件中

### 作用域

`config` 块在**目录级**生效。在 `config.td` 中定义的配置会应用于该目录及其子目录下的所有文件（除非被子目录的 `config.td` 覆盖）。

### 常见用途

#### 导入公共模块

```python
import sys
import datetime
from typing import List, Optional

# 将项目源码目录加入路径
sys.path.append("${ROOT}/scripts")
```

#### 定义全局变量

```python
# config.td
DEFAULT_TIMEOUT = 30
```

```python
# model.td
class Service(BaseModel):
    timeout: int = Field(default=DEFAULT_TIMEOUT)
```

### 执行时机

Config 块在**解析阶段**之前执行，为 Model 定义和 Entity 实例化准备环境。

---

## 2. Front Matter

Typedown 文件支持标准 YAML Front Matter，位于文件开头，用于定义文件级元数据和快捷脚本。

### 语法

```yaml
---
title: 文档标题
tags: [api, v2]
scripts:
  validate: 'typedown check --full ${FILE}'
---
```

### 标准字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | `str` | 文档标题 |
| `tags` | `List[str]` | 文档标签，可用于查询过滤 |
| `author` | `str` | 文档作者 |
| `order` | `int` | 目录排序优先级 |

### 脚本定义

```yaml
scripts:
  # 覆盖默认的验证命令
  validate: 'typedown check --full ${FILE}'
  
  # 自定义测试命令
  test-api: 'pytest tests/api_test.py --target ${entity.id}'
  
  # 组合命令
  ci-pass: 'typedown check --full ${FILE} && typedown run test-api'
```

### 环境变量

脚本中可用的变量：

| 变量 | 说明 |
|------|------|
| `${FILE}` | 当前文件绝对路径 |
| `${DIR}` | 当前目录绝对路径 |
| `${ROOT}` | 项目根目录 |
| `${FILE_NAME}` | 不含扩展名的文件名 |
| `${TD_ENV}` | 当前环境（local, ci, prod） |

### 作用域继承

脚本解析遵循**就近优先**原则：

1. **文件级**：当前文件 Front Matter（最高优先级）
2. **目录级**：当前目录 `config.td` 的 Front Matter
3. **项目级**：根目录 `typedown.yaml` 的全局配置

---

## 配置优先级

| 层级 | 范围 | 优先级 |
|------|------|--------|
| Front Matter | 文件级 | 最高 |
| config.td | 目录级 | 中等 |
| typedown.yaml | 项目级 | 最低 |

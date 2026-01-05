---
title: 环境配置
---

# 环境配置 (Config)

`config` 块用于配置编译器的运行时环境。它通常用于导入公共库、设置全局变量或修改系统路径。

## 语法签名

```markdown
```config:python
<Setup Script>
```
```

- **关键字**: `config`
- **语言**: 目前仅支持 `python`。
- **位置限制**: 通常仅允许出现在 `config.td` 文件中。

## 作用域

`config` 块在**目录级**生效。
在 `config.td` 中定义的配置，会应用于该目录及其子目录下的所有文件（除非被子目录的 `config.td` 覆盖）。

## 常见用途

### 1. 导入公共模块

```python
import sys
import datetime
from typing import List, Optional

# 将项目源码目录加入路径，以便导入自定义 Python 工具库
sys.path.append("${ROOT}/scripts")
```

### 2. 定义全局变量

在 `config` 块中定义的变量，可以在同级目录的 `model` 或 `spec` 块中直接使用。

```python
# config.td
DEFAULT_TIMEOUT = 30
```

```python
# model.td
class Service(BaseModel):
    timeout: int = Field(default=DEFAULT_TIMEOUT)
```

## 执行时机

Config 块在**解析阶段**之前执行。这意味着它们为后续的 Model 定义和 Entity 实例化准备了环境。

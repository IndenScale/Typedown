---
title: 文件元数据
---

# 文件元数据 (Front Matter)

Typedown 文件支持标准的 YAML Front Matter，位于文件及其开头。用于定义文件级别的元数据和快捷脚本。

## 语法

```yaml
---
key: value
scripts:
  ...
---
```

## 标准字段

| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| **title** | `str` | 文档标题，用于生成侧边栏或索引。 |
| **tags** | `List[str]` | 文档标签，可用于查询过滤。 |
| **author** | `str` | 文档作者。 |
| **order** | `int` | 在目录中的排序优先级。 |

## 脚本 (Scripts)

`scripts` 字段用于定义该文件的专属操作命令。

```yaml
scripts:
  # 覆盖默认的验证命令
  validate: "td validate --strict ${FILE}"
  
  # 自定义测试命令
  test-api: "pytest tests/api_test.py --target ${entity.id}"
```

### 环境变量

在脚本命令中，可以使用以下变量：

- `${FILE}`: 当前文件绝对路径。
- `${DIR}`: 当前目录绝对路径。
- `${ROOT}`: 项目根目录。

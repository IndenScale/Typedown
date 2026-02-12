---
title: 脚本系统
---

# 脚本系统

Typedown 的脚本系统允许在 `.td` 文件的 Front Matter 中定义操作逻辑，将静态文档转化为可执行单元。

## 定义脚本

在文件 Front Matter 中定义：

```yaml
---
scripts:
  # 覆盖标准动作：验证当前文件
  validate: 'typedown check --full ${FILE}'
  
  # 自定义动作
  verify-api: 'pytest tests/api.py --id ${entity.id}'
  
  # 组合动作
  ci-pass: 'typedown check --full ${FILE} && typedown run verify-api'
---
```

## 作用域与继承

脚本解析遵循**就近原则**：

1. **文件级**：当前文件 Front Matter（最高优先级）
2. **目录级**：当前目录 `config.td` 的 Front Matter
3. **项目级**：根目录 `typedown.yaml`

## 环境变量

| 变量 | 说明 |
|------|------|
| `${FILE}` | 当前文件绝对路径 |
| `${DIR}` | 当前目录绝对路径 |
| `${ROOT}` | 项目根目录 |
| `${FILE_NAME}` | 不含扩展名的文件名 |
| `${TD_ENV}` | 当前环境（local, ci, prod） |

## 命令行调用

```bash
# 执行文件的 validate 脚本
typedown run validate user_profile.td

# 批量执行目录下所有文件的 test 脚本
typedown run test specs/
```

## 常用脚本模式

### CI/CD 检查

```yaml
scripts:
  ci: 'typedown check --json | tee typedown-report.json'
```

### 数据导出

```yaml
scripts:
  export: 'typedown export ${FILE} --format json > output.json'
```

### 外部验证

```yaml
scripts:
  verify-oracle: 'python scripts/check_external.py --ref ${entity.id}'
```

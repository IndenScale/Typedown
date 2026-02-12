---
title: 错误码
---

# 错误码对照表

## 格式说明

错误码格式：`E{stage}{category}{number}`

- **Stage** (第2-3位): 编译阶段
  - `01` = L1 Scanner
  - `02` = L2 Linker
  - `03` = L3 Validator
  - `04` = L4 Spec
  - `09` = System

- **Category** (第4位): 错误类别
  - `0-1` = Syntax/Parse
  - `2-3` = Execution
  - `4-5` = Reference/Link
  - `6-7` = Schema/Type
  - `8-9` = System

- **Number** (第5位): 序号 (1-9)

## 错误级别

- **Error**: 严重错误，阻止执行
- **Warning**: 潜在问题，执行继续
- **Info**: 信息性消息
- **Hint**: 改进建议

## 错误码列表

### L1: Scanner (E01xx)

| 错误码 | 级别 | 描述 |
|--------|------|------|
| E0101 | Error | 语法解析失败 |
| E0102 | Error | 配置块位置错误（config 只能在 config.td 中） |
| E0103 | Error | 嵌套列表反模式 |
| E0104 | Error | 文件读取错误 |
| E0105 | Error | 文档结构错误 |

### L2: Linker (E02xx)

| 错误码 | 级别 | 描述 |
|--------|------|------|
| E0221 | Error | 模型执行失败 |
| E0222 | Error | 配置执行失败 |
| E0223 | Warning | Prelude 符号加载失败 |
| E0224 | Warning | 模型重建失败 |
| E0231 | Error | 模型块 ID 与类名不匹配 |
| E0232 | Error | 模型使用了保留字段 'id' |
| E0233 | Error | 无效的模型类型 |
| E0241 | Error | 重复的 ID 定义 |

### L3: Validator (E03xx)

| 错误码 | 级别 | 描述 |
|--------|------|------|
| E0341 | Error | 引用解析失败 |
| E0342 | Error | 检测到循环依赖 |
| E0343 | Error | 演进目标未找到 |
| E0361 | Error | Schema 验证失败 |
| E0362 | Error | Ref[T] 类型不匹配 |
| E0363 | Error | ID 冲突 |
| E0364 | Error | 模型类未找到 |
| E0365 | Error | 查询语法错误 |

### L4: Spec (E04xx)

| 错误码 | 级别 | 描述 |
|--------|------|------|
| E0421 | Error | Spec 执行失败 |
| E0422 | Error | Oracle 执行失败 |
| E0423 | Warning | Spec 目标未找到 |
| E0424 | Error | Spec 断言失败 |

### System (E09xx)

| 错误码 | 级别 | 描述 |
|--------|------|------|
| E0981 | Error | 内部编译器错误 |
| E0982 | Error | 文件系统错误 |
| E0983 | Error | 配置错误 |

## CI/CD 集成

```bash
# 检查并输出 JSON
typedown check --json

# 过滤特定错误码
typedown check --json | jq '.diagnostics[] | select(.code == "E0103")'

# 统计各阶段错误数量
typedown check --json | jq '.summary.by_stage'
```

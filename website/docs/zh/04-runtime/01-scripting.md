---
title: 脚本系统
---

# 脚本系统 (Script System)

Typedown 的脚本系统允许在 `.td` 文件的 Front Matter 中定义操作逻辑，将静态文档转化为可执行的单元。

## 1. 核心机制

脚本定义在文件的 Front Matter 中。

### 定义方式

```yaml
---
# 定义该文件的专属动作
scripts:
  # 覆盖标准动作：验证当前文件逻辑
  validate: "td validate --strict ${FILE}"

  # 自定义动作：连接工商局接口核验数据
  verify-business: "python scripts/oracle_check.py --id ${entity.id}"

  # 组合动作
  ci-pass: "td validate ${FILE} && td run verify-business"
---
```

## 2. 作用域与继承 (Scoping)

脚本解析遵循**就近原则 (Nearest Winner)**，实现了配置的层级继承：

1. **File Scope**: 当前文件的 Front Matter。优先级最高，覆盖同名脚本。
2. **Directory Scope**: 当前目录（或最近父目录）的 `config.td`。
   - **注意**: 必须在 `config.td` 的 **Front Matter** 中定义 `scripts` 字段，而非代码块中。
   - 作用于该目录下所有文件。
3. **Project Scope**: 根目录的 `typedown.yaml`。定义全局默认行为。

## 3. 环境变量注入

运行时环境会自动注入上下文变量，赋予脚本感知环境的能力：

- `${FILE}`: 当前文件的绝对路径。
- `${DIR}`: 当前文件所在目录的绝对路径。
- `${ROOT}`: 项目根目录。
- `${FILE_NAME}`: 不带后缀的文件名。
- `${TD_ENV}`: 当前运行环境 (local, ci, prod)。

## 4. 命令行交互

用户通过统一的接口调用这些脚本，无需记忆复杂的底层命令。

```bash
# 执行当前文件的 validate 脚本
$ td run validate user_profile.td

# 批量执行 specs/ 目录下所有文件的 test 脚本
$ td run test specs/
```

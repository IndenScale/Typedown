# 示例 06: 模块化项目 (系统架构)

现实世界的项目通常分散在多个文件中。Typedown 通过基于目录的作用域机制，天然支持这种方式。

## 核心概念

1.  **文件分离 (File Separation)**: 将 Model, Spec 和 Entity 放在不同的文件中，以提高可维护性。
2.  **共享作用域 (Shared Scope)**: 同一目录（及其子目录）下的文件共享同一个 `symbol_table`。
3.  **`config.td`**: 一个特殊文件，用于向整个目录树导出公共库/符号。

## 结构

- `config.td`: 导出 `datetime` 模块。
- `models.td`: 定义 `Task` 模型。
- `data.td`: 定义实际的任务数据。

## 如何运行

使用 `--path` 参数将 **目录** 传递给 CLI。

```bash
td check --path examples/zh/06_modular_project
```

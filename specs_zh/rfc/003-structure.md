# 项目结构概览

Typedown 推荐采用清晰的分层目录结构来组织文档、模型和约束。

## 标准目录结构

一个典型的 Typedown 项目包含以下四个核心目录：

```text
.
├── docs/       # [内容层] Markdown 文档 (.md, .td)
│   ├── arch/
│   │   ├── config.td  # 目录级配置
│   │   └── design.md
│   └── ...
├── models/     # [模式层] Pydantic 数据模型定义 (.py)
│   └── user.py
├── specs/      # [逻辑层] Pytest 约束与测试脚本 (.py)
│   └── test_consistency.py
└── assets/     # [资源层] 图片、图表、静态文件
```

## 配置与元数据 (`config.td`)

Typedown 采用**基于文件系统的配置继承机制**。
每个目录都可以包含一个 `config.td` 文件，用于定义该目录及其子目录下所有文档的共享配置（如公共 Imports、元数据默认值）。

- **导入机制**: 关于如何导入类（本地路径、URI、别名等）及配置继承的详细规则，请参阅 [04_import.md](./04_import.md)。
- **引用机制**: 关于如何在文档间通过 `[[]]` 语法引用实体及处理版本，请参阅 [05_reference.md](./05_reference.md)。

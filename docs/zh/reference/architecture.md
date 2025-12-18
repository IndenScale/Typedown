# 架构

Typedown 的运作方式就像是文档的编译器。

## 编译流水线

1.  **解析 (Parse / Lexical Analysis):**
    *   读取 Markdown 文件。
    *   提取代码块 (`model`, `entity`, `spec`)。
    *   识别引用 (`[[...]]`)。

2.  **解析 (Resolve / Semantic Analysis):**
    *   **导入解析：** 加载配置和 Python 模块。
    *   **符号表构建：** 将所有实体 ID 映射到其定义。
    *   **引用链接：** 将 `former`、`derived_from` 和 `[[...]]` 引用连接到其目标。

3.  **验证 (Validate / Execution):**
    *   **结构验证：** Pydantic 模型验证每个实体的原始数据。
    *   **逻辑验证：** Pytest 针对完全解析的 Workspace 执行 `spec` 代码块。

## 工作区 (Workspace)

**工作区 (Workspace)** 是整个项目的内存表示。它是所有测试和工具交互的“唯一事实来源”。

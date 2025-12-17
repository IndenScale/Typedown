# 编译器架构

`tdc` (Typedown Compiler) 的工作流程分为三个主要阶段：

## 1. Analyze (分析)

*   **File Discovery**: 扫描 `docs/` 目录。
*   **Config Loading**: 解析各级 `config.td` 并构建继承树。
*   **Symbol Table**: 解析所有 Markdown 文件，提取 `entity` 块，建立初步的符号表（Symbol Table）。

## 2. Desugar (脱糖)

这是编译器的核心逻辑。

*   **Dependency Graph**: 根据 `former` 和 `derived_from` 关系构建依赖图。
*   **Topological Sort**: 对依赖图进行拓扑排序，确定解析顺序。
*   **Merge & Resolve**: 按顺序实例化对象，将父对象的属性合并到子对象中，生成扁平化的数据结构。

## 3. Validate (验证)

*   **Pydantic Check**: 对每个“脱糖”后的完整对象运行 Pydantic 验证器。
*   **Pytest Runner**: 收集所有数据对象，将其注入 Pytest 上下文，运行 `specs/` 中的测试用例。

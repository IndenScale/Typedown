## 交互语言

你可以自由选择推理语言，但是必须使用中文汇报。

## 多语言支持

该项目需要实现多语言支持。

根目录文档，如 README.md，需要有对应的 README_ZH.md。

其他文档，需要有多语言目录。所有语言文档目录中的序号保持一致，但是命名和内容使用各自的语言。

## Markdown 嵌套

Markdown 代码块中可以嵌套 Markdown 代码块。

需要使用正确的嵌套模式，尤其是正确数量的 `。

````markdown
# 嵌套的 Markdown

```python
# 嵌套的 Python
print("hello world")
```
````

## 文档系统

该系统使用 `docs` 与 `dev-docs` 两个目录来记录面向用户与开发者的文档。

前者专注记录公式，而后者记录讨论、设计决策和实现记录。

## AI 辅助文档

- **[.gemini/skills.md](.gemini/skills.md)**: Typedown 核心技能手册（语法、CLI、调试）。

- **[.gemini/agents.md](.gemini/agents.md)**: 角色定义与分工。

## 运行

使用 `uv run td` 来运行程序。

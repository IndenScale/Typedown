# 内部数据模型

编译器在内存中维护着文档的结构化表示。

## Document Node

表示一个 Markdown 文件。

- `path`: 文件路径
- `frontmatter`: 合并后的元数据
- `entities`: 文件内定义的 Entity 列表

## Entity Node

表示一个数据对象。

- `id`: 唯一标识符
- `class_ref`: Pydantic 类引用
- `raw_data`: 源代码块中的原始数据
- `resolved_data`: 脱糖后的完整数据
- `source_location`: 文件名及行号（用于报错定位）

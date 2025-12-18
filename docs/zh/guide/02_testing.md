# 测试与验证

Typedown 允许你直接在文档中编写测试。这确保了你的规范不仅仅是文本，而是可执行的契约。

## 1. `spec` 代码块

使用 `spec` 代码块编写基于 **Python** 和 **Pytest** 的测试逻辑。

````markdown
```spec
def test_character_level_limit(workspace):
    # 获取所有 RPGCharacter 的实例
    chars = workspace.get_entities_by_type("RPGCharacter")
    
    for char in chars:
        assert char.level <= 100, f"Character {char.id} 超过了等级限制"
```
````

## 2. `workspace` 夹具 (Fixture)

Typedown 会自动向你的测试中注入一个 `workspace` 夹具。通过这个对象，你可以访问项目的所有解析状态。

**常用方法：**
*   `workspace.get_entity(id: str) -> EntityBlock`: 根据 ID 获取单个实体。
*   `workspace.get_entities_by_type(class_name: str) -> List[Any]`: 获取指定类型的所有实体（已解析的对象）。

## 3. 运行测试

使用 CLI 命令执行项目中的所有 spec 代码块。

```bash
td test .
```

该命令会：
1.  解析所有 Markdown 文件。
2.  解析所有实体和依赖关系。
3.  将 `spec` 代码块提取到临时测试套件中。
4.  运行 `pytest` 并报告结果。

# 测试机制 (Testing Mechanism)

Typedown 的核心支柱之一是逻辑验证。为了处理复杂的业务规则和跨实体约束，Typedown 集成了 **Pytest** 作为其测试引擎。

## 1. 验证层级 (Validation Levels)

Typedown 将验证分为两个层级：

1. **内部验证 (Validator)**:

   - **关注点**: 单个 Entity 内部的数据正确性（如：字段类型、数值范围、格式）。
   - **实现**: 直接在 `model` 定义中使用 Pydantic 的 `field_validator` 或 `model_validator`。
   - **执行时机**: 在编译期（解析 Entity 时）自动执行。

2. **规格验证 (Specification)**:
   - **关注点**: 跨实体的一致性、复杂的业务规则、系统级约束（如：外键存在性、数值平衡）。
   - **实现**: 使用 `spec` 代码块编写标准的 Pytest 测试用例。
   - **执行时机**: 使用 `td test` 命令时执行。

## 2. Spec 代码块

使用 `spec` 标记代码块来编写测试逻辑。这些代码块本质上是 Python 脚本，会被提取并作为 Pytest 测试文件运行。

````markdown
```spec
# 自动注入: pytest, session
# 无需手动 import pytest

# 编写标准的 Pytest 测试函数
# 'session' 是系统自动注入的 Fixture，包含整个项目的数据
def test_all_monsters_have_valid_drops(session):
    items = session.table("Item")
    monsters = session.table("Monster")

    for monster in monsters:
        for drop_id in monster.drops:
            assert drop_id in items, f"Monster {monster.name} drops unknown item {drop_id}"
```
````

### 自动注入与上下文

- **Fixture**: 测试函数可以请求系统预置的 Fixture，最核心的是 `session` (或 `workspace`)，它提供了对所有已解析 Entity 的访问接口。
- **Imports**: 执行环境默认包含 `pytest`。因此你可以直接使用 `@pytest.mark...` 而无需编写 import 语句。

## 3. 测试组织与标签 (Markers)

利用 Pytest 的 Marker 机制，可以灵活地组织和筛选测试用例。

````markdown
```spec
# 同样，pytest 模块已自动注入，直接使用即可

@pytest.mark.smoke
def test_basic_integrity(session):
    assert len(session.entities) > 0

@pytest.mark.rpg
@pytest.mark.balance
def test_boss_difficulty(session):
    # ...
```
````

通过 CLI 命令 `td test -m smoke` 即可只运行带有 `smoke` 标签的测试。

## 4. 内联检查 (Inline Check) (可选)

对于针对特定 Entity 的快速断言，可以使用 `check` 块。它会自动转化为针对紧邻的上一个 Entity 的测试用例。

````markdown
```entity:User
id: "admin"
age: 30
```

```check
# 'entity' 变量自动绑定到上面的 User 实例
assert entity.age >= 18
```
````

import pytest

# 这是一个模拟的 Spec 文件，展示如何对全局 Entity 进行验证

def test_characters_alive(characters):
    """所有角色的 HP 必须大于 0"""
    for char in characters:
        assert char.hp > 0, f"Character {char.name} ({char.id}) is dead!"

def test_inventory_integrity(characters, items):
    """角色背包中的物品 ID 必须在物品数据库中存在"""
    item_ids = {item.id for item in items}
    for char in characters:
        for item_id in char.inventory:
            assert item_id in item_ids, f"Character {char.name} has unknown item: {item_id}"

def test_evolution_consistency(characters):
    """如果角色有前身，名字不应该改变 (除非改名卡)"""
    # 这一步通常需要编译器提供的 helper 来访问 former 对象
    # 这里仅做伪代码演示
    pass

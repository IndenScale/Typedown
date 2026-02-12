# RPG 背包系统

```model: Item
class Item(BaseModel):
    name: str
    weight: float
    value: int
```

```spec: check_single_item_weight
@target(type="Item")
def check_single_item_weight(subject):
    """确保单个物品不会太重以至于无法携带。"""
    LIMIT = 50.0
    if subject.weight > LIMIT:
         # 使用 blame 定位导致问题的具体实体
         blame(subject, f"物品太重了！({subject.weight} > {LIMIT})")
         raise ValueError(f"物品 '{subject.name}' 太重了！")
```

```spec: check_total_inventory_cap
@target(type="Item", scope="global")
def check_total_inventory_cap(subject):
    """确保背包总重量不超过负重上限。"""
    CAPACITY = 100.0
    
    # 使用 SQL 查询所有物品进行聚合
    all_items = sql("SELECT * FROM Item")
    total_weight = sum(item.weight for item in all_items)
    
    if total_weight > CAPACITY:
        # 智能聚合：找出最重的物品并归咎于它
        heaviest = max(all_items, key=lambda x: x.weight)
        blame(heaviest, f"已超过容量 {CAPACITY}。由于该物品最重 ({heaviest.weight})，被标记为 culprit。")
        
        raise ValueError(f"背包总负重超限！当前: {total_weight}, 最大: {CAPACITY}")
```

```entity Item: sword
name: "Iron Sword"
weight: 15.0
value: 50
```

```entity Item: shield
name: "Wooden Shield"
weight: 10.0
value: 30
```

```entity Item: heavy_armor
name: "Plate Armor"
weight: 80.0  # (15 + 10 + 80 = 105) > 100
value: 200
```
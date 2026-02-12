# RPG Inventory System

```model:Item
class Item(BaseModel):
    name: str
    weight: float
    value: int
```

```spec:check_single_item_weight
@target(type="Item")
def check_single_item_weight(subject):
    """Ensure a single item is not too heavy to carry."""
    LIMIT = 50.0
    if subject.weight > LIMIT:
         # Use blame to pinpoint the specific entity causing the problem
         blame(subject, f"Item is too heavy! ({subject.weight} > {LIMIT})")
         raise ValueError(f"Item '{subject.name}' is too heavy!")
```

```spec:check_total_inventory_cap
@target(type="Item", scope="global")
def check_total_inventory_cap(subject):
    """Ensure the total weight of the inventory does not exceed the capacity limit."""
    CAPACITY = 100.0
    
    # Use SQL to query all items for aggregation
    all_items = sql("SELECT * FROM Item")
    total_weight = sum(item.weight for item in all_items)
    
    if total_weight > CAPACITY:
        # Smart aggregation: find the heaviest item and blame it
        heaviest = max(all_items, key=lambda x: x.weight)
        blame(heaviest, f"Capacity {CAPACITY} exceeded. Since this is the heaviest item ({heaviest.weight}), it is marked as the culprit.")
        
        raise ValueError(f"Total inventory weight limit exceeded! Current: {total_weight}, Max: {CAPACITY}")
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

# RPG Inventory System

```model: Item
class Item(BaseModel):
    name: str
    weight: float
    value: int
```

```spec: check_single_item_weight
@target(type="Item")
def check_single_item_weight(subject):
    """Ensure no single item is too heavy to carry."""
    LIMIT = 50.0
    if subject.weight > LIMIT:
         raise ValueError(f"Item '{subject.name}' is too heavy! ({subject.weight} > {LIMIT})")
```

```spec: check_total_inventory_cap
@target(type="Item")
def check_total_inventory_cap(subject):
    """Ensure total inventory weight does not exceed capacity."""
    CAPACITY = 140.0
    
    # query() returns wrappers around strict dicts or objects
    # We query all entities of type Item to calculate sum
    all_items = query("@Item")
    
    total_weight = sum(item.weight for item in all_items)
    
    if total_weight > CAPACITY:
        raise ValueError(f"Global inventory capacity exceeded! Current: {total_weight}, Max: {CAPACITY}")
```

```entity Item: sword
name: "Iron Sword"
weight: 55.0
value: 50
```

```entity Item: shield
name: "Wooden Shield"
weight: 10.0
value: 30
```

```entity Item: heavy_armor
name: "Plate Armor"
weight: 80.0  # This will trigger the error (15+10+80 = 105 > 100)
value: 200
```
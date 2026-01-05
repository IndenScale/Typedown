# RPG Inventory System

```model:Item
class Item(BaseModel):
    name: str
    weight: float
    value: int
```

```spec:weight_limit
@target(type="Item")
def test_total_weight_limit(subject):
    # This spec runs for every Item.
    # To check TOTAL weight, we need aggregation capabilities (Global Context).
    if subject.weight > 50.0:
         raise ValueError(f"Item '{subject.name}' is too heavy! ({subject.weight})")
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
weight: 80.0  # This will trigger the error (15+10+80 = 105 > 100)
value: 200
```
# Deep Reference & Indexing Test

```entity:Config id=Farm
apples:
  - id: "apple_a"
    weight: 0.5
    logs:
      - msg: "Picked"
        date: "2024-01-01"
      - msg: "Sorted"
  - id: "apple_b"
    weight: 0.6
```

```entity:Report id=R1
# 1. Basic indexing
first_apple_weight: "[[Farm.apples[0].weight]]"

# 2. Deep indexing and final serialization
# Should get {"msg": "Picked", "date": "2024-01-01"}
first_log_full: "[[Farm.apples[0].logs[0].*]]"

# 3. ID reference (should stay "Farm")
farm_id: "[[Farm]]"
```

```spec
def test_deep_indexing(workspace):
    r1 = workspace.get_entity("R1")
    
    # 1. Weight lookup
    assert r1.first_apple_weight == 0.5
    
    # 2. Deep log serialization
    log = r1.first_log_full
    assert log.msg == "Picked"
    assert log.date == "2024-01-01"
    
    # 3. ID
    assert r1.farm_id == "Farm"
```

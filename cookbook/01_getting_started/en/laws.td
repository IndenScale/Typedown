# The Laws of the Kingdom

## 1. Royal Hierarchy (Schema)

First, we define the hierarchical data structure of the domain.

```model:Character
class Character(BaseModel):
    name: str
```

```model:King
class King(Character):
    # King class inherits from Character
    pass
```

## 2. Uniqueness Validation (Spec)

Then, we define the rules. This Spec uses Global Context to ensure there can be only one King.

```spec:uniqueness_check
@target(type="King", scope="global")
def uniqueness_check(subject):
    # Use SQL to count the number of Kings
    count = sql("SELECT count(*) as total FROM King")[0]['total']
    
    if count > 1:
        # Identify the pretender
        pretenders = sql("SELECT id, name FROM King WHERE name != 'Arthur Pendragon'")
        for p in pretenders:
            blame(p['id'], f"Only Arthur is the true King. {p['name']} is a pretender!")
            
    assert count <= 1, f"There cannot be two Kings in this land! (Current: {count})"
```

## 3. Conflict (Data)

Finally, we attempt to create two Kings to trigger an error.

```entity King: arthur
name: "Arthur Pendragon"
```

```entity King: mordred
name: "Mordred the Pretender"
```

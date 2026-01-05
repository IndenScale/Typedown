# The Laws of the Kingdom

## 1. The Royal Class (Schema)
First, we define the data structure for our domain.

```model: Character
class Character(BaseModel):
    name: str
```

```model: King
class King(Character):
    # The King class inherits from Character
    pass
```

## 2. The Uniqueness Constraint (Spec)
Then, we define the rules. This spec ensures only one King exists.

```spec: test_there_can_be_only_one
@target(type="King")
def test_there_can_be_only_one(subject):
    # Correct True King check
    assert subject.name == "Arthur Pendragon", f"Imposter Detected: {subject.name} is not the true King!"
```

## 3. The Conflict (Data)
Finally, we try to create two Kings, triggering the error.

```entity King: arthur
name: "Arthur Pendragon"
```

```entity King: mordred
name: "Mordred the Pretender"
```
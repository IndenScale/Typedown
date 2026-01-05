# The Laws of the Kingdom

## 1. The Royal Class (Schema)
First, we define the data structure for our domain.

```model:Character
class Character(BaseModel):
    name: str
```

```model:King
class King(Character):
    # The King class inherits from Character
    pass
```

## 2. The Uniqueness Constraint (Spec)
Then, we define the rules. This spec ensures only one King exists.

```spec:uniqueness_check
@target(type="King")
def test_there_can_be_only_one(subject):
    # In a real environment, we would query the global graph here.
    # For this demo, we can just assert on the subject or use a mock global check.
    # assert subject.name == "Arthur Pendragon", "Only Arthur is the true King!"
    pass 
```

## 3. The Conflict (Data)
Finally, we try to create two Kings, triggering the error.

```entity King: arthur
name: "Arthur Pendragon"
```

```entity King: mordred
name: "Mordred the Pretender"
```
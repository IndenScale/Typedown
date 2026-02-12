# Test Spec Executor

## Model Definition

```model:User
class User(BaseModel):
    name: str
    age: int
```

## Test Entities

```entity User:alice
name: "Alice"
age: 25
```

```entity User:bob
name: "Bob"
age: 17
```

```entity User:charlie
name: "Charlie"
age: 30
```

## Spec: Age Validation

```spec id=check_adult
# This spec validates that all users are adults (age >= 18)
@target(type="User")
def validate_age(subject):
    assert subject.age >= 18, f"User {subject.name} is underage (age: {subject.age})"
```

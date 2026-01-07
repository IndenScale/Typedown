# 04 Context Interaction

Here we define a `User` model with a computed property `full_name`.

```model: User
class User(BaseModel):
    first_name: str
    last_name: str
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

## Spec using the Property

The spec doesn't need to know how `full_name` is constructed. It just uses it.

```spec: check_name_length
@target(type="User")
def check_name_length(user):
    # We use the computed property defined in the model
    if len(user.full_name) > 20:
        raise ValueError(f"Name is too long: {user.full_name}")
```

```entity User: alice
first_name: "Alice"
last_name: "Smith"
```

```entity User: long_name
first_name: "Christopher"
last_name: "Cumberbatch-Hiddleston"
```

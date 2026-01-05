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
Then, we define the rules. This spec ensures only one King exists using the new Global Context.

```spec:uniqueness_check
@target(type="King", scope="global")
def uniqueness_check(subject):
    # 使用 SQL 统计国王数量
    count = sql("SELECT count(*) as total FROM King")[0]['total']
    
    if count > 1:
        # 指出哪个是伪王
        pretenders = sql("SELECT id, name FROM King WHERE name != 'Arthur Pendragon'")
        for p in pretenders:
            blame(p['id'], f"只有 Arthur 是真正的国王，{p['name']} 是篡位者！")
            
    assert count <= 1, f"这片土地上不能有两个国王！(当前: {count})"
```

## 3. The Conflict (Data)
Finally, we try to create two Kings, triggering the error.

```entity King: arthur
name: "Arthur Pendragon"
```

```entity King: mordred
name: "Mordred the Pretender"
```
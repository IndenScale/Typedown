# 王国律法 (The Laws of the Kingdom)

## 1. 皇室阶级 (Schema)

首先，我们定义领域的层级数据结构。

```model:Character
class Character(BaseModel):
    name: str
```

```model:King
class King(Character):
    # King 类继承自 Character
    pass
```

## 2. 唯一性校验 (Spec)

然后，我们定义规则。这个 Spec 使用全局上下文（Global Context）确保只能有一个国王。

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

## 3. 冲突 (Data)

最后，我们尝试创建两个国王，以触发错误。

```entity King: arthur
name: "Arthur Pendragon"
```

```entity King: mordred
name: "Mordred the Pretender"
```
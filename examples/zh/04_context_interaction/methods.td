# 04 上下文交互

这里我们定义了一个带有 `full_name` 计算属性的 `User` 模型。

```model: User
class User(BaseModel):
    first_name: str
    last_name: str
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

## 使用属性的 Spec

Spec 不需要知道 `full_name` 是如何构建的，直接使用即可。

```spec: check_name_length
@target(type="User")
def check_name_length(user):
    # 我们使用模型中定义的计算属性
    if len(user.full_name) > 20:
        raise ValueError(f"名字太长了: {user.full_name}")
```

```entity User: alice
first_name: "Alice"
last_name: "Smith"
```

```entity User: long_name
first_name: "Christopher"
last_name: "Cumberbatch-Hiddleston"
```

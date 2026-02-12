---
tags: [demo, script-test]
scripts:
  # 自定义脚本：打印文件信息
  info: "echo 'File: ${FILE}' && echo 'Dir: ${DIR}' && echo 'Root: ${ROOT}' && echo 'Name: ${FILE_NAME}'"
  
  # 覆盖标准动作：验证当前文件
  validate: "td validate --path ${FILE}"
  
  # 组合动作
  full-check: "td lint --path ${FILE} && td check --path ${FILE} && td validate --path ${FILE}"
---

# Script System Test

这是一个测试脚本系统的示例文件。

```model User
class User(BaseModel):
    name: str
    age: int
```

```entity User: alice
name: Alice
age: 25
```

```entity User: bob
name: Bob
age: 30
```

```spec
@target(type="User")
def test_user_age(subject):
    """验证用户年龄大于 0"""
    assert subject.age > 0, f"{subject.name} 的年龄必须大于 0"
```

# Organization Models

```model:Employee
class Employee(BaseModel):
    name: str
    role: str
    email: str
```

```model:Department
class Department(BaseModel):
    name: str
    lead: Ref["Employee"]
```

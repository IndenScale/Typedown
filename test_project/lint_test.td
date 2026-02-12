# Test Nested List Lint

```model: Company
class Company(BaseModel):
    name: str
    departments: List[str]
```

## Valid Entity (No Nested Lists)

```entity Company:acme
name: "ACME Corp"
departments:
  - "Engineering"
  - "Sales"
  - "Marketing"
```

## Invalid Entity (Nested Lists - Should Fail Lint)

```entity Company:bad_company
name: "Bad Corp"
# This should trigger a lint error
teams:
  - ["Alice", "Bob"]
  - ["Charlie", "David"]
```

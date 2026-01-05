# Core Domain Primitives

```model:Currency
class Currency(str, Enum):
    CNY = "CNY"
    USD = "USD"
    EUR = "EUR"
```

```model:Money
class Money(BaseModel):
    amount: float = Field(..., ge=0)
    currency: Currency = Field(default=Currency.CNY)
    
    def __str__(self):
        return f"{self.currency} {self.amount}"
```

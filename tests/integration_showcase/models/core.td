# Core Domain Primitives

```model:Currency
from enum import Enum

class Currency(str, Enum):
    CNY = "CNY"
    USD = "USD"
    EUR = "EUR"
```

```model:Money
from pydantic import BaseModel, Field

class Money(BaseModel):
    amount: float = Field(..., ge=0)
    currency: Currency = Field(default=Currency.CNY)
    
    def __str__(self):
        return f"{self.currency} {self.amount}"
```

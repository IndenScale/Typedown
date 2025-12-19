from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional, Any
from datetime import datetime

class Currency(str, Enum):
    CNY = "CNY"
    USD = "USD"
    EUR = "EUR"

class Money(BaseModel):
    amount: float = Field(..., description="金额", ge=0)
    currency: Currency = Field(default=Currency.CNY, description="币种")

    def __str__(self):
        return f"{self.currency} {self.amount:.2f}"
    
    # Python 原生方法，支持复杂逻辑
    def __add__(self, other):
        if not isinstance(other, Money) or other.currency != self.currency:
            raise ValueError("Cannot add different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)

class BaseEntity(BaseModel):
    """所有ERP实体的基类"""
    id: str = Field(..., description="全局唯一标识符")
    created_at: datetime = Field(default_factory=datetime.now)

# 01 Schema 约束

在这里，我们增强了 `Book` 模型，以自动确保数据质量。

```model: Book
class Book(BaseModel):
    title: str
    # L1 约束: 价格必须为正数
    price: float = Field(gt=0, description="Price must be positive")
    
    # L1 约束: ISBN 必须正好是 13 位数字
    isbn: str = Field(pattern=r"^\d{13}$", description="13-digit ISBN")
    
    # 可选字段
    discount_price: float | None = None

    # L2 约束: 自动修正标题格式
    @field_validator('title')
    @classmethod
    def title_must_be_title_case(cls, v: str) -> str:
        if not v.istitle():
            return v.title()
        return v

    # L2 约束: 确保逻辑一致性
    @model_validator(mode='after')
    def check_discount(self):
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError('discount_price must be less than price')
        return self
```

## 合法实体 (Valid Entity)

这个实体将通过校验。注意小写的标题会被自动修复。

```entity Book: nice_book
title: "the hitchhiker's guide to the galaxy"
price: 42.0
isbn: "9780345391803"
discount_price: 10.0
```

## 非法实体 (Invalid Entity)

这个实体会导致 `td check` 报错，因为折扣价高于原价。

```entity Book: bad_pricing
title: "Expensive Fail"
price: 100.0
isbn: "9781234567890"
discount_price: 150.0
```

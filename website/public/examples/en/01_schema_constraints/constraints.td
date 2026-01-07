# 01 Schema Constraints

We enhance our `Book` model to ensure data quality automatically.

```model: Book
class Book(BaseModel):
    title: str
    # L1 Constraint: Price must be positive
    price: float = Field(gt=0, description="Price must be positive")
    
    # L1 Constraint: ISBN must be exactly 13 digits
    isbn: str = Field(pattern=r"^\d{13}$", description="13-digit ISBN")
    
    # Optional field
    discount_price: float | None = None

    # L2 Constraint: Auto-correct title formatting
    @field_validator('title')
    @classmethod
    def title_must_be_title_case(cls, v: str) -> str:
        if not v.istitle():
            return v.title()
        return v

    # L2 Constraint: Ensure logic consistency
    @model_validator(mode='after')
    def check_discount(self):
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError('discount_price must be less than price')
        return self
```

## Valid Entity

This entity will pass validation. Note the lowercase title will be fixed.

```entity Book: nice_book
title: "the hitchhiker's guide to the galaxy"
price: 42.0
isbn: "9780345391803"
discount_price: 10.0
```

## Invalid Entity

This entity will fail `td check` because the discount is higher than the price.

```entity Book: bad_pricing
title: "Expensive Fail"
price: 100.0
isbn: "9781234567890"
discount_price: 150.0
```

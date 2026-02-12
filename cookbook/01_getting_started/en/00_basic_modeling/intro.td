# 00 Basic Modeling

Welcome to Typedown. Let's define a simple Book structure.

## 1. The Blueprint (Model)

We define a `Book` model. Note that we can use standard Python types (`str`, `int`, `bool`).

```model: Book
class Book(BaseModel):
    title: str
    author: str
    published_year: int
    # Default values work just like in Python
    is_available: bool = True
```

## 2. The Data (Entity)

Now we create an instance of a Book.
The syntax is `entity <ModelName>: <EntityID>`.

```entity Book: dune
title: "Dune"
author: "Frank Herbert"
published_year: 1965
```

```entity Book: neuromancer
title: "Neuromancer"
author: "William Gibson"
published_year: 1984
is_available: false
```

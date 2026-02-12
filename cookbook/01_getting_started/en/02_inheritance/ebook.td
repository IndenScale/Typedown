# 02 Inheritance

We can extend the `Book` model to create an `EBook` model.

## 1. The Base Model

```model: Book
class Book(BaseModel):
    title: str
    author: str
```

## 2. The Child Model

`EBook` inherits all fields from `Book` and adds new ones.

```model: EBook
class EBook(Book):
    file_size_mb: float
    format: str = "pdf"
```

## 3. The Polymorphic Entity

This entity is an `EBook`, but it fundamentally is also a `Book`.

```entity EBook: digital_dune
title: "Dune"
author: "Frank Herbert"
file_size_mb: 2.5
format: "epub"
```

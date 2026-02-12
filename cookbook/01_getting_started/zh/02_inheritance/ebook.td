# 02 继承

我们可以扩展 `Book` 模型来创建一个 `EBook` 模型。

## 1. 基础模型 (Base Model)

```model: Book
class Book(BaseModel):
    title: str
    author: str
```

## 2. 子模型 (Child Model)

`EBook` 继承了 `Book` 的所有字段，并添加了新字段。

```model: EBook
class EBook(Book):
    file_size_mb: float
    format: str = "pdf"
```

## 3. 多态实体 (Polymorphic Entity)

这个实体是一个 `EBook`，但从根本上说它也是一本 `Book`。

```entity EBook: digital_dune
title: "Dune"
author: "Frank Herbert"
file_size_mb: 2.5
format: "epub"
```

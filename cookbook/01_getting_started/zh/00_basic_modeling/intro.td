# 00 基础建模

欢迎来到 Typedown。让我们定义一个简单的书籍结构。

## 1. 蓝图 (Model)

我们要定义一个 `Book` 模型。注意我们可以使用标准的 Python 类型 (`str`, `int`, `bool`)。

```model: Book
class Book(BaseModel):
    title: str
    author: str
    published_year: int
    # 默认值机制与 Python 完全一致
    is_available: bool = True
```

## 2. 数据 (Entity)

现在我们要创建一个 Book 的实例。
语法是 `entity <ModelName>: <EntityID>`。

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

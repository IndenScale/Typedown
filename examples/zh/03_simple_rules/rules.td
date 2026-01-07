# 03 简单规则 (Simple Rules)

我们使用 `spec` 来强制执行需要运行时计算的逻辑（例如“今天”）。

```model: Book
class Book(BaseModel):
    title: str
    published_date: date
```

## 逻辑 (The Spec)

这个函数会对 **每一个** `Book` 类型的实体运行。

```spec: check_publication_date
@target(type="Book")
def check_publication_date(subject):
    """确保书籍并非来自未来。"""
    from datetime import date
    if subject.published_date > date.today():
         raise ValueError(f"书籍 '{subject.title}' 来自未来！")
```

## 数据 (The Data)

```entity Book: old_book
title: "Generic History Book"
published_date: 1990-01-01
```

```entity Book: future_book
title: "Time Traveler's Guide"
published_date: 2099-01-01
```

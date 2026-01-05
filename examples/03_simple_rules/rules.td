# 03 Simple Rules

We use a `spec` to enforce logic that requires runtime calculation (e.g., "today").

```model: Book
class Book(BaseModel):
    title: str
    published_date: date
```

## The Logic (Spec)

This function runs for **every** entity of type `Book`.

```spec: check_publication_date
@target(type="Book")
def check_publication_date(subject):
    """Ensure book is not from the future."""
    from datetime import date
    if subject.published_date > date.today():
         raise ValueError(f"Book '{subject.title}' is from the future!")
```

## The Data

```entity Book: old_book
title: "Generic History Book"
published_date: 1990-01-01
```

```entity Book: future_book
title: "Time Traveler's Guide"
published_date: 2099-01-01
```

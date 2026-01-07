# 05 Global Governance

We want to limit the total file size of our digital library.

```model: Book
class Book(BaseModel):
    title: str
    file_size_mb: float
```

## Global Spec

This spec runs once. `subject` is None (or irrelevant) in global scope.

```spec: check_total_storage
@target(type="Book", scope="global")
def check_total_storage(subject):
    """Ensure total library size does not exceed limit."""
    LIMIT_MB = 100.0
    
    # Query all entities of type Book using SQL-like syntax
    all_books = sql("SELECT * FROM Book")
    
    # Calculate total size
    total_size = sum(b.file_size_mb for b in all_books)
    
    if total_size > LIMIT_MB:
        # Smart Diagnostic: Find the responsible entity
        biggest = max(all_books, key=lambda x: x.file_size_mb)
        
        # 'blame' attaches the error to a specific entity
        blame(biggest, f"This book is contributing most to the overflow ({biggest.file_size_mb} MB)")
        
        raise ValueError(f"Library storage full! Used: {total_size} MB, Limit: {LIMIT_MB} MB")
```

## The Data

```entity Book: small_book
title: "Article"
file_size_mb: 5.0
```

```entity Book: huge_atlas
title: "World Atlas High Res"
file_size_mb: 120.0
```

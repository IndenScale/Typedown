# 05 全局治理

我们要限制数字图书馆的总文件大小。

```model: Book
class Book(BaseModel):
    title: str
    file_size_mb: float
```

## 全局 Spec

这个 Spec 只运行一次。在 global 作用域中，`subject` 为 None（或不相关）。

```spec: check_total_storage
@target(type="Book", scope="global")
def check_total_storage(subject):
    """确保图书馆总大小不超过限制。"""
    LIMIT_MB = 100.0
    
    # 使用类 SQL 语法查询所有 Book 类型的实体
    all_books = sql("SELECT * FROM Book")
    
    # 计算总大小
    total_size = sum(b.file_size_mb for b in all_books)
    
    if total_size > LIMIT_MB:
        # 智能诊断：找出责任实体
        biggest = max(all_books, key=lambda x: x.file_size_mb)
        
        # 'blame' 将错误归咎于特定实体
        blame(biggest, f"这本书是导致溢出的罪魁祸首 ({biggest.file_size_mb} MB)")
        
        raise ValueError(f"图书馆存储已满！已用: {total_size} MB, 限制: {LIMIT_MB} MB")
```

## 数据

```entity Book: small_book
title: "Article"
file_size_mb: 5.0
```

```entity Book: huge_atlas
title: "World Atlas High Res"
file_size_mb: 120.0
```

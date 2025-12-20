# Circular Reference Test

```entity:Config id=X
val: "[[Y.val]]"
```

```entity:Config id=Y
val: "[[X.val]]"
```

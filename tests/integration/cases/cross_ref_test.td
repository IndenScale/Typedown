# Cross Entity Reference Test

```entity:Config id=A
val: "I am A"
from_b: "[[B.val]]"
```

```entity:Config id=B
val: "I am B"
from_c: "[[C.val]]"
```

```entity:Config id=C
val: "I am C"
```

```spec
def test_chain(workspace):
    a = workspace.get_entity("A")
    b = workspace.get_entity("B")
    assert a.from_b == "I am B"
    assert b.from_c == "I am C"

def test_query_interface(compiler):
    # Testing the new query interface
    val = compiler.query("A.from_b")
    assert val == "I am B"
```

# Linkage Logic Test

```entity:Config id=Main
title: "Typedown"
version: "1.0.0"
```

```entity:Project id=P1
# 1. Symbolic Link (should be string "Main")
ref_id: "[[Main]]"

# 2. Value Lookup (should be "1.0.0")
ver: "[[Main.version]]"

# 3. Data Inlining (should be the full dict)
full_conf: "[[Main.*]]"
```

```spec
def test_linkage_modes(workspace):
    p1 = workspace.get_entity("P1")
    
    # 1. Symbolic Link
    assert p1.ref_id == "Main"
    
    # 2. Value Lookup
    assert p1.ver == "1.0.0"
    
    # 3. Data Inlining
    # Note: AttributeWrapper wraps the dict during test execution
    assert p1.full_conf.title == "Typedown"
    assert p1.full_conf.version == "1.0.0"
```

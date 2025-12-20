# Smoke Test

Check if the engine is green.

```model
class Color(BaseModel):
    name: str
    hex: str
```

```entity:Color
id: color_green
name: "Green"
hex: "#00FF00"
```

```check
# Inline check for the entity above
assert entity.name == "Green"
assert entity.hex.startswith("#")
```

```spec
def test_green_is_valid(workspace):
    colors = workspace.get_entities_by_type("Color")
    assert len(colors) == 1
    assert colors[0].name == "Green"
    assert colors[0].hex == "#00FF00"
```

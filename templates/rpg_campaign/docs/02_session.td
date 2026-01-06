### Valen 的状态更新 (V2)

Valen 失去了 30 点 HP，但经过治疗恢复了 10 点。最终 HP 为 80。
同时，他从哥布林身上搜刮到了一把备用铁剑。

```entity Character: valen_v2
former: [[slug_char_valen_v1]]
hp: 80
inventory:
  - [[item_sword_iron]]
  - [[item_sword_iron]]
```

### Lyra 的状态更新 (V2)

Lyra 消耗了一瓶药水。

```entity Character: lyra_v2
former: [[slug_char_lyra_v1]]
inventory:
  - [[item_potion_hp]] # 只剩一瓶
```

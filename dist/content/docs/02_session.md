# 第一章：暗林遭遇

队伍进入了幽暗的森林。突然，草丛中跳出了两只哥布林！

## 遭遇战

这里我们将基于图鉴中的 [[mon_goblin_base]] 生成两个具体的敌人。

```entity:Monster
derived_from: "mon_goblin_base"
id: "encounter_01_goblin_a"
name: "疯狂的哥布林"
hp: 20 # 比原型弱一点
```

```entity:Monster
derived_from: "mon_goblin_base"
id: "encounter_01_goblin_b"
name: "强壮的哥布林"
hp: 40 # 强壮变体
attack: 8
```

战斗非常激烈。战士 [[Valen]] 冲向了 [[encounter_01_goblin_b]]。
法师 [[Lyra]] 在后方支援。

## 战后结算

经过一番苦战，哥布林被击败了。但是 Valen 受了伤。

Lyra 使用了一瓶药水治疗 Valen。

### Valen 的状态更新 (V2)

Valen 失去了 30 点 HP，但经过治疗恢复了 10 点。最终 HP 为 80。
同时，他从哥布林身上搜刮到了一把备用铁剑。

```entity:Character
former: "char_valen_v1"
id: "char_valen_v2"
hp: 80
inventory: ["item_sword_iron", "item_sword_iron"]
```

### Lyra 的状态更新 (V2)

Lyra 消耗了一瓶药水。

```entity:Character
former: "char_lyra_v1"
id: "char_lyra_v2"
inventory: ["item_potion_hp"] # 只剩一瓶
```

## 当前队伍状态

现在，[[Valen]].hp 是 [[char_valen_v2.hp]] (80)，而 [[Lyra]].inventory 中只剩下了 [[char_lyra_v2.inventory]]。
队伍继续前进...

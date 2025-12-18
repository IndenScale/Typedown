# 怪物与物品图鉴

## 基础物品

```entity:Item
id: "item_potion_hp"
name: "治疗药水 (小)"
weight: 0.5
value: 10
```

```entity:Item
id: "item_sword_iron"
name: "铁剑"
weight: 2.0
value: 50
```

## 怪物原型

这里定义了基础的哥布林模板。

```entity:Monster
id: "mon_goblin_base"
name: "哥布林"
type: "Humanoid"
hp: 30
attack: 5
loot: ["item_sword_iron"]
```

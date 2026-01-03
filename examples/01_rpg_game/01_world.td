# RPG Lite: The World

Here we define the actual game content: Items and Characters.
References are handled using the `[[...]]` syntax.

## Items

```entity Item: rusty-sword
name: "Rusty Sword"
weight: 3.5
value: 10
```

```entity Item: healing-potion
name: "Healing Potion"
weight: 0.5
value: 50
```

## Characters

Notice how `inventory` references the items defined above.

```entity Character: hero-kael
name: "Kael"
class_name: "Mage"
level: 2
hp: 45
max_hp: 60
inventory:
  - [[healing-potion]]
  - [[rusty-sword]]
```

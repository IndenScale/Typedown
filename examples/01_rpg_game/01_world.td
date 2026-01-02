# RPG Lite: The World

Here we define the actual game content: Items and Characters.
References are handled using the `[[...]]` syntax.

## Items

```entity Item: rusty-sword
id: "items/rusty-sword-v1"
name: "Rusty Sword"
weight: 3.5
value: 10
```

```entity Item: healing-potion
id: "items/potion-v1"
name: "Healing Potion"
weight: 0.5
value: 50
```

## Characters

Notice how `inventory` references the items defined above.

```entity Character: hero-kael
id: "chars/kael-v1"
name: "Kael"
class_name: "Mage"
level: 2
hp: 45
max_hp: 60
inventory:
  - [[items/potion-v1]]
  - [[items/rusty-sword-v1]]
```

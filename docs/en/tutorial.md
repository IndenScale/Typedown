# Tutorial: RPG Campaign

Welcome to the Typedown tutorial. In this guide, we will model a simple RPG campaign to demonstrate how Typedown handles:

1. **Definitions**: Defining concepts and entities.
2. **References**: Linking entities together.
3. **Evolution**: Tracking changes in state over time.

## 1. Setup

In this example, we have predefined python models for `Character`, `Item`, and `Monster`. We import them in our `config.td`:

```python
# config.td
from use_cases.rpg_campaign.models.schema import Character, Item, Monster
```

## 2. Defining The World (The Manual)

First, we define our base items and monsters in `00_manual.td`. This acts as our "Source of Truth" for game assets.

### Basic Items

We define a potion and a sword using the `Item` schemata. Note the `id` field which we will use to reference these items later.

```entity Item: potion
id: "item_potion_hp"
name: "Healing Potion (Small)"
weight: 0.5
value: 10
```

```entity Item: sword
id: "item_sword_iron"
name: "Iron Sword"
weight: 1.5
value: 50
```

### Monster Prototypes

We define a base Goblin template.

```entity Monster: goblin
id: "mon_goblin_base"
name: "Goblin"
type: "Humanoid"
hp: 30
attack: 5
loot:
  - [[sword]] # Reference to the sword variable if defined locally, or we can use ID
```

_Note: In Typedown, `[[...]]` is used for references. It resolves handles or IDs._

## 3. The Adventure Party

In `01_party.td`, we introduce our main characters.

### Warrior Valen

```entity Character: valen
id: "slug_char_valen_v1"
name: "Valen"
class_name: "Warrior"
hp: 100
max_hp: 100
inventory:
  - [[item_sword_iron]] # Starts with an Iron Sword
```

### Mage Lyra

```entity Character: lyra
id: "slug_char_lyra_v1"
name: "Lyra"
class_name: "Mage"
hp: 60
max_hp: 60
inventory:
  - [[item_potion_hp]]
  - [[item_potion_hp]]
```

## 4. The Session (Evolution)

In `02_session.td`, the story unfolds. This demonstrates Typedown's powerful **Evolution Semantics**.

### The Encounter

Two goblins appear! We instantiate them based on `mon_goblin_base`.

```entity Monster: goblin_a
id: "encounter_01_goblin_a"
derived_from: "mon_goblin_base"
name: "Crazy Goblin"
hp: 20 # Weaker than base
```

```entity Monster: goblin_b
id: "encounter_01_goblin_b"
derived_from: "mon_goblin_base"
name: "Tough Goblin"
hp: 40
attack: 8
```

### State Updates

After the battle, Valen is hurt and Lyra uses a potion. We define **Version 2 (V2)** of our characters.

**Valen V2**: took damage, healed a bit, picked up a spare sword.

```entity Character: valen_v2
id: "char_valen_v2"
former: [[slug_char_valen_v1]] # Evolves from V1
hp: 80
inventory:
  - [[item_sword_iron]]
  - [[item_sword_iron]]
```

**Lyra V2**: used a potion.

```entity Character: lyra_v2
id: "char_lyra_v2"
former: [[slug_char_lyra_v1]]
inventory:
  - [[item_potion_hp]] # One potion left
```

## Conclusion

By using `former`, we create a linked chain of states. We can query the current state of the party or look back at their history. This is "Consensus Modeling" in action.

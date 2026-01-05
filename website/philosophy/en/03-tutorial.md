---
title: Tutorial
---

# Tutorial: The RPG Campaign

Welcome to the Typedown tutorial. Typedown is a **Consensus Modeling Language (CML)** designed to turn fluid thought into verifiable data. In this guide, we will model a simple RPG campaign to explore Typedown's core pillars:

1. **Definitions**: Modeling concepts and declaring entities.
2. **References**: Linking the world together via "Intent."
3. **Evolution**: Tracking the state of the world through time.

## 1. Setup: The Context Field

Typedown reflects the physical structure of your workspace. We start by configuring our environment in `config.td`. Here, we import our Pydantic models (Schemas) that define what a Character, Item, and Monster look like.

```python
# config.td
from models.schema import Character, Item, Monster
```

## 2. Defining The World (The Manual)

In `00_manual.td`, we define our base game assets. This is our static "Source of Truth."

### Basic Items

We define a potion and a sword. Note the `id` field—this is the **Slug**, a stable, global identifier.

```entity Item: potion
name: "Healing Potion (Small)"
weight: 0.5
value: 10
```

```entity Item: sword
name: "Iron Sword"
weight: 1.5
value: 50
```

### Monster Templates

Next, we define a Goblin. In Typedown, we prefer **Explicitness**. Instead of deep inheritance trees, we use AI or simple templates to populate data.

```entity Monster: goblin
name: "Goblin"
type: "Humanoid"
hp: 30
attack: 5
loot:
  - [[item_sword_iron]]
```

> **A Note on References**: `[[item_sword_iron]]` is a **Query Intent**. It means "Find the entity with this ID or Handle in the current context."

## 3. The Adventure Party

In `01_party.td`, we introduce our protagonists.

```entity Character: valen
name: "Valen"
class_name: "Warrior"
hp: 100
max_hp: 100
inventory:
  - [[item_sword_iron]]
```

```entity Character: lyra
name: "Lyra"
class_name: "Mage"
hp: 60
max_hp: 60
inventory:
  - [[item_potion_hp]]
```

## 4. The Session (Evolution)

As the game unfolds in `02_session.td`, we encounter Typedown's most powerful feature: **Evolution Semantics**.

### The Encounter

Two goblins appear! Instead of complex "derivation," we simply declare them as distinct entities in this specific session context.

```entity Monster: goblin_a
name: "Crazy Goblin"
hp: 20
attack: 5
```

### State Updates: The Timeline

After a fierce battle, Valen is wounded and Lyra consumes a potion. We don't overwrite the old data; we evolve it. By using the `former` keyword, we link the new state to the previous one, creating an immutable history.

**Valen V2**: Wounded, but has scavenged an extra sword.

```entity Character: valen_v2
former: "char_valen_v1"
name: "Valen"
class_name: "Warrior"
hp: 80
max_hp: 100
inventory:
  - [[item_sword_iron]]
  - [[item_sword_iron]]
```

**Lyra V2**: Spent her potion.

```entity Character: lyra_v2
former: "char_lyra_v1"
name: "Lyra"
class_name: "Mage"
hp: 60
max_hp: 60
inventory: []
```

## Conclusion: The Power of the Field

By using `former`, you've created a **verifiable timeline**. The compiler can now:

- Track how Valen's HP changed over sessions.
- Ensure that `valen_v2` is still a valid `Character`.
- Navigate between the past and present of your world.

This is the promise of Typedown: **Cognitive freedom through the discipline of modeling.**

# The Hero's Journey: Evolution

Typedown is not just for static data; it's a **Consensus Modeling Language** that tracks how thoughts and entities evolve over time.

## The Story Continues

After braving the _Whispering Woods_, Kael has not only gained experience but has also undergone a fundamental transformation. In Typedown, we use the `former` keyword to link these states.

### Kael Level Up

Kael is no longer a mere "Mage". He has touched the ancient scrolls and become an "Archmage".

```entity Character: hero-kael-v2
# 1. Identity Consistency
# We use 'id' to give this entity a stable, global identifier.


# 2. Evolution Link
# 'former' points to the previous stable state of this character.
# Note: Evolution must use Global IDs (L0/L2/L3), not local handles.
former: "hero-kael"

# 3. Explicit Data
# Typedown uses "Pure Pointers"—data isn't merged automatically.
# This ensures that each block is a complete, immutable snapshot.
name: "Kael the Archmage"
class_name: "Archmage"
level: 10
hp: 120
max_hp: 120
inventory:
  - [[healing-potion]]
  # Kael dropped the rusty sword and gained something new in the narrative (imaginary)
```

## Why Evolution Matters?

By using `former`, we create a **verifiable timeline**.

- **LSP Support**: You can "Go to Definition" on `former` to see where Kael came from.
- **Auditability**: In business scenarios (like the `use_cases/bid_agent`), this allows us to track how a bid proposal changed from Draft A to Final B.
- **Narrative Integration**: The Markdown text above the blocks provides the _human rationale_ (The "Why"), while the blocks provide the _machine truth_ (The "What").

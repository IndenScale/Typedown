# Example 05: Global Governance (System Logic)

So far, we've validated single entities. But what if a rule depends on the **collection** of all entities? This is where `scope="global"` comes in.

## Concepts

1.  **`scope="global"`**: The spec runs once for the entire dataset, not per entity.
2.  **`sql()`**: A powerful way to query your entities as if they were a database.
3.  **Aggregation**: Use Python's `sum`, `max`, `min` on the query results.
4.  **`blame()`**: When a global rule fails, you can point the finger at a specific entity to highlight it in the IDE.

## How to Run

```bash
td check --path examples/05_global_governance
```

The check will fail because `huge_atlas` alone exceeds the library limit. Notice how the error is attributed to `huge_atlas` thanks to `blame()`.

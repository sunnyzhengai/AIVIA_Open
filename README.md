# 🧠 AIVIA-Core  
**Transform your SQL data into a living Neo4j graph you can chat with.**

---

> 🕒 **Personal Open-Source Project**  
> AIVIA-Core is an independent open-source project developed outside of my employment, on personal time and equipment.  
> It uses only publicly available or synthetic data, and is shared for educational and research purposes.

---

## 🚧 Work in Progress

AIVIA-Core is actively evolving.  
This early open-source release focuses on transparency and collaboration while we gradually publish the core modules.

Current status:
- ✅ Documentation and demo structure ready  
- 🔧 Refactoring existing components into the new modular design  
- 🧪 Preparing the first end-to-end demo notebook

Follow updates in [Discussions](https://github.com/SUNNYZHENG/aivia-core/discussions).

---

## ✨ Overview

AIVIA-Core turns your existing SQL tables and relationships into a **knowledge graph** and lets you query it in **natural language**.  
Instead of writing nested joins, you can ask questions like:

> “Which **open deals > $10k**, created in the **last 60 days**, have **no upcoming meeting** in the next **14 days**?”

AIVIA returns a **traceable Cypher query** (and results), e.g.:

```cypher
MATCH (a:Account)-[:HAS_DEAL]->(d:Deal)
OPTIONAL MATCH (d)-[:HAS_ACTIVITY]->(act:Activity)
WHERE d.stage <> "Closed Won"
  AND d.stage <> "Closed Lost"
  AND d.amount > 10000
  AND date(d.created_date) >= date() - duration('P60D')
  AND (
    // No future next step within 14 days
    NOT EXISTS {
      MATCH (d)-[:HAS_ACTIVITY]->(act2:Activity)
      WHERE act2.next_step_date IS NOT NULL
        AND date(act2.next_step_date) <= date() + duration('P14D')
    }
  )
RETURN a.name AS account, d.name AS deal, d.amount AS amount, d.stage AS stage
ORDER BY amount DESC

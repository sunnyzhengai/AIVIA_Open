# Sales CRM — Synthetic Demo Dataset

This folder contains a tiny, **synthetic** CRM dataset (CSVs) for the AIVIA-Core demo:

> **SQL/CSVs → Graph (Neo4j) → Natural language → Traceable Cypher → Results**

It models common CRM concepts: **Accounts, Contacts, Deals, Activities, Users** and optional **Campaigns/Touches**.

---

## How to use these CSVs

1. Start a local Neo4j database (Desktop or Aura Free).
2. Open the notebook: `notebooks/demo_sales_crm.ipynb`  
   - The notebook loads these CSVs, builds the graph (MERGE nodes/edges), and runs example questions.
3. Explore/modify the CSVs and re-run the notebook to see how answers change.

> Diagram used in docs/README: `docs/diagrams/sales_crm_graph.png`

---

## Files & Columns (Data Dictionary)

All dates use **ISO 8601** (`YYYY-MM-DD`). Booleans are `true/false`. IDs are strings.

### `accounts.csv` — one row per company
| column       | type   | description                            |
|--------------|--------|----------------------------------------|
| `account_id` | string | Unique account key (e.g., `AC-1001`)  |
| `name`       | string | Company name                           |
| `industry`   | string | e.g., SaaS, FinTech, Healthcare       |
| `region`     | string | e.g., NAMER, EMEA, APAC               |

### `contacts.csv` — people at companies (buying committee)
| column       | type   | description                                                                 |
|--------------|--------|-----------------------------------------------------------------------------|
| `contact_id` | string | Unique person key (e.g., `CT-2001`)                                         |
| `account_id` | string | FK → `accounts.account_id`                                                  |
| `name`       | string | Person’s name (synthetic)                                                   |
| `title`      | string | Job title (VP Eng, Head of Finance, etc.)                                  |
| `email`      | string | Fake email (e.g., `alex@example.com`)                                      |
| `role`       | string | Buying-committee role: **Economic Buyer**, **Finance**, **Security**, **Procurement**, **Champion**, **User** |

> Tip: Deliberately leave some deals **missing** Finance/Security/Economic Buyer to make “gap” questions interesting.

### `deals.csv` — opportunities/pipeline
| column          | type    | description                                                           |
|-----------------|---------|-----------------------------------------------------------------------|
| `deal_id`       | string  | Unique deal key (e.g., `DL-3001`)                                     |
| `account_id`    | string  | FK → `accounts.account_id`                                            |
| `name`          | string  | Deal name                                                             |
| `amount`        | number  | Expected ARR/TCV (e.g., `25000`)                                      |
| `stage`         | string  | e.g., Prospecting, Evaluate, Proposal, Legal, Closed Won/Lost        |
| `created_date`  | date    | When the deal was created                                             |
| `close_date`    | date    | Expected/actual close date (empty if none)                            |
| `owner_user_id` | string  | FK → `users.user_id`                                                  |
| `source`        | string  | e.g., Inbound, Partner, Referral, or a Campaign ID like `CMP-4001`    |
| `is_commit`     | boolean | `true/false` (included in forecast commit)                            |

### `activities.csv` — interactions on deals
| column           | type   | description                                                                                  |
|------------------|--------|----------------------------------------------------------------------------------------------|
| `activity_id`    | string | Unique activity key (e.g., `AT-5001`)                                                       |
| `deal_id`        | string | FK → `deals.deal_id`                                                                         |
| `type`           | string | Email, Call, Meeting                                                                         |
| `date`           | date   | When it happened                                                                             |
| `next_step_date` | date   | **Future** scheduled step (e.g., next meeting). Leave empty when none.                       |

> Include a mix of deals **with** and **without** a future `next_step_date`.

### `users.csv` — owners/teams
| column    | type   | description                           |
|-----------|--------|---------------------------------------|
| `user_id` | string | Unique user key (e.g., `U-01`)        |
| `name`    | string | Owner name                            |
| `team`    | string | e.g., Enterprise, Mid-Market, SMB    |
| `region`  | string | NAMER, EMEA, APAC                    |

### `campaigns.csv` (optional) — marketing sources
| column        | type   | description                         |
|---------------|--------|-------------------------------------|
| `campaign_id` | string | Unique campaign key (`CMP-4001`)    |
| `name`        | string | Campaign name (Webinar X, Event Y)  |
| `channel`     | string | Ads, Webinar, Event, Content, Referral |

### `touches.csv` (optional) — campaign touches to contacts
| column      | type   | description                                  |
|-------------|--------|----------------------------------------------|
| `touch_id`  | string | Unique touch key (`TC-9001`)                 |
| `campaign_id` | string | FK → `campaigns.campaign_id`              |
| `contact_id`  | string | FK → `contacts.contact_id`                |
| `date`      | date   | When the touch occurred                      |

---

## Intended Graph (Conceptual)

- `(:Account)<-[:BELONGS_TO]-(:Contact)`
- `(:Account)-[:HAS_DEAL]->(:Deal)`
- `(:Deal)-[:HAS_ACTIVITY]->(:Activity)`
- `(:Deal)-[:OWNED_BY]->(:User)`
- *(Optional)* `(:Deal)-[:SOURCED_BY]->(:Campaign)`  
- *(Optional)* `(:Campaign)-[:TOUCHED]->(:Contact)` *(via touches)*

Refer to the diagram in the main docs:  
`docs/diagrams/sales_crm_graph.png`

---

## Canonical Questions (try these in the demo)

1) **Open, high-value, no next step**  
   “Which **open deals > $10k** created in the **last 60 days** have **no upcoming meeting** in the next **14 days**?”

2) **Buying-committee gaps**  
   “Which **commit deals** this quarter are **missing Finance or Security** in the buying committee?”

3) **Stale in stage**  
   “Which deals have been in **Evaluate** for **> 21 days** with **no activity in 14 days**?”

4) **Attribution that matters** *(optional)*  
   “Which **campaigns** are associated with deals that **closed < 30 days** from creation?”

5) **Forecast sanity check**  
   “Show **commit** deals this quarter with **no economic buyer** or **no activity in 14 days**.”

---

## Data Quality & Safety

- 100% **synthetic names/emails** (e.g., `alex@example.com`).
- **Recent dates** (last 90–120 days) so time-window questions work.
- Include **both positive and negative** examples (e.g., some deals do have future `next_step_date`, some don’t).
- Booleans are `true/false`; amounts are numeric (no currency symbols).

---

## License

This synthetic dataset follows the repository’s license (Apache 2.0).  
Use freely for demos, testing, and examples.

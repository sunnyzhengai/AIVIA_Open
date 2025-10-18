# SPDX-License-Identifier: Apache-2.0
"""
Public entrypoint for AIVIA NL→Cypher→Results.
Swap the TODOs with your existing matcher / path / builder modules.
"""
from typing import Dict, Any, Tuple, List
import pandas as pd
from neo4j import GraphDatabase
from .adapters.matcher_adapter import match_concepts_adapter

class AiviaEngine:
    def __init__(self, driver, schema_index=None, value_index=None):
        self.driver = driver
        self.schema_index = schema_index
        self.value_index = value_index

    def run(self, question: str, top_k: int = 8) -> Tuple[str, pd.DataFrame, Dict[str, Any]]:
        # 1) Match (labels/properties/values)
        match = self._match_concepts(question, top_k=top_k)        # TODO: wire your matcher

        # 2) Resolve path (connect matched nodes)
        path  = self._resolve_path(match)                          # TODO: wire your path resolver

        # 3) Build Cypher from path + filters
        cypher = self._build_cypher(question, match, path)         # TODO: wire your cypher builder

        # 4) Execute
        df = self._exec_cypher(cypher)

        debug = {"question": question, "match": match, "path": path, "cypher": cypher}
        return cypher, df, debug

    # ----------------- internals (temporary stubs) -----------------
    def _match_concepts(self, question: str, top_k: int) -> Dict[str, Any]:
        # Use the adapter to call the real matcher (or fallback to stub)
        return match_concepts_adapter(question, top_k=top_k)

    def _resolve_path(self, match: Dict[str, Any]) -> List[str]:
        # TEMP: we know the Sales CRM graph; prefer short paths.
        return ["Account-[:HAS_DEAL]->Deal", "Deal-[:HAS_ACTIVITY]->Activity", "Deal-[:OWNED_BY]->User"]

    def _build_cypher(self, question: str, m: Dict[str, Any], path: List[str]) -> str:
        # TEMP: recognize our 3 canonical prompts and emit portable Cypher.
        q = question.lower()

        if "no next meeting" in q or "no next step" in q:
            amount = m["needs_amount_gt"] or 10000
            window = m["window_days"] or 60
            next_days = m["next_meeting_days"] or 14
            return f"""
WITH date(localdatetime()) AS today
MATCH (a:Account)-[:HAS_DEAL]->(d:Deal)
WHERE d.stage <> "Closed Won" AND d.stage <> "Closed Lost"
  AND d.amount > {amount}
  AND date(d.created_date) >= today - duration({{days: {window}}})
  AND NOT EXISTS {{
    MATCH (d)-[:HAS_ACTIVITY]->(act2:Activity)
    WHERE act2.next_step_date IS NOT NULL
      AND date(act2.next_step_date) <= today + duration({{days: {next_days}}})
  }}
OPTIONAL MATCH (d)-[:OWNED_BY]->(u:User)
RETURN a.name AS account, d.id AS deal_id, d.name AS deal, d.amount AS amount,
       d.stage AS stage, d.created_date AS created, u.name AS owner
ORDER BY amount DESC
""".strip()

        if "commit" in q and ("finance" in q or "security" in q):
            return """
WITH date(localdatetime()) AS today
WITH today, date({year: today.year, month: ((toInteger((today.month-1)/3)*3)+1), day:1}) AS q_start
MATCH (a:Account)-[:HAS_DEAL]->(d:Deal)
WHERE d.is_commit = true
  AND date(d.created_date) >= q_start
  AND d.stage <> "Closed Won" AND d.stage <> "Closed Lost"
OPTIONAL MATCH (a)<-[:BELONGS_TO]-(c_fin:Contact {role:"Finance"})
OPTIONAL MATCH (a)<-[:BELONGS_TO]-(c_sec:Contact  {role:"Security"})
WITH a, d, c_fin, c_sec
WHERE c_fin IS NULL OR c_sec IS NULL
RETURN a.name AS account, d.id AS deal_id, d.name AS deal,
       CASE WHEN c_fin IS NULL THEN "Missing Finance" ELSE "" END +
       CASE WHEN c_fin IS NULL AND c_sec IS NULL THEN " & " ELSE "" END +
       CASE WHEN c_sec IS NULL THEN "Missing Security" ELSE "" END AS gap
ORDER BY account
""".strip()

        if "evaluate" in q and ("no activity" in q or "stale" in q):
            stale = m["stale_days"] or 21
            recent = 14
            return f"""
WITH date(localdatetime()) AS today
MATCH (a:Account)-[:HAS_DEAL]->(d:Deal)
WHERE d.stage = "Evaluate"
  AND date(d.created_date) <= today - duration({{days: {stale}}})
  AND NOT EXISTS {{
    MATCH (d)-[:HAS_ACTIVITY]->(act:Activity)
    WHERE date(act.date) >= today - duration({{days: {recent}}})
  }}
RETURN a.name AS account, d.id AS deal_id, d.name AS deal, d.created_date AS created
ORDER BY created ASC
""".strip()

        # Fallback: conservative open-deals listing
        return """
WITH date(localdatetime()) AS today
MATCH (a:Account)-[:HAS_DEAL]->(d:Deal)
WHERE d.stage <> "Closed Won" AND d.stage <> "Closed Lost"
RETURN a.name AS account, d.id AS deal_id, d.name AS deal, d.amount AS amount, d.stage AS stage
ORDER BY amount DESC
""".strip()

    def _exec_cypher(self, cypher: str) -> pd.DataFrame:
        with self.driver.session() as s:
            rows = s.run(cypher).data()
        return pd.DataFrame(rows)

# Convenience function
def run_query(driver, question: str, schema_index=None, value_index=None, top_k: int = 8):
    eng = AiviaEngine(driver, schema_index=schema_index, value_index=value_index)
    return eng.run(question, top_k=top_k)

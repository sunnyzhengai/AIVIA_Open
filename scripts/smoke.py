# scripts/smoke.py
# SPDX-License-Identifier: Apache-2.0
import os, sys
import pandas as pd
from neo4j import GraphDatabase
from aivia.run_query import run_query

PROMPTS = [
    "open deals > 10k last 60 days no next meeting 14 days",
    "commit deals this quarter missing finance or security",
    "evaluate stage > 21 days with no activity in 14 days",
]

def main():
    uri  = os.getenv("AIVIA_NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("AIVIA_NEO4J_USER", "neo4j")
    pwd  = os.getenv("AIVIA_NEO4J_PASS", "password")
    driver = GraphDatabase.driver(uri, auth=(user, pwd))

    ok = True
    for q in PROMPTS:
        cypher, df, dbg = run_query(driver, q)
        rows = 0 if df is None else len(df)
        print(f"[SMOKE] {q} -> rows={rows}")
        if cypher.strip() == "" or df is None:
            ok = False

    driver.close()
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()

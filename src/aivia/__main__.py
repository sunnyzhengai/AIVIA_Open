# Minimal CLI to test locally
from neo4j import GraphDatabase
from .run_query import run_query
import os, sys

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "open deals >10k last 60 days no next meeting 14 days"
    driver = GraphDatabase.driver(
        os.getenv("AIVIA_NEO4J_URI","bolt://localhost:7687"),
        auth=(os.getenv("AIVIA_NEO4J_USER","neo4j"), os.getenv("AIVIA_NEO4J_PASS","password"))
    )
    cypher, df, dbg = run_query(driver, q)
    print("== Generated Cypher ==")
    print(cypher)
    print("\n== Results (top 10) ==")
    print(df.head(10).to_string(index=False))

# AIVIA Developer Notes (NL→Cypher integration)

This package exposes `aivia.run_query(driver, question, ...) -> (cypher, df, debug)`.

Swap the stubbed internals in `src/aivia/run_query.py` with your existing modules:

- Matcher → `label_and_filter_matcher.py`
- Path → `path_resolver.py`
- Cypher Builder → `cypher_prompt_builder.py` (or equivalent)

Keep dates **as strings** in the graph; cast inside Cypher with `date(...)`. Prefer `WITH date(localdatetime()) AS today` + `duration({days:N})` for portability.

# SPDX-License-Identifier: Apache-2.0
# Thin wrapper so AiviaEngine can call your existing matcher unchanged elsewhere.
from typing import Dict, Any

# TODO: import your real matcher here
# from your_pkg.label_and_filter_matcher import match_labels_and_filters

def match_concepts_adapter(question: str, top_k: int = 8) -> Dict[str, Any]:
    # TODO: return your real structure. For now, map to the keys AiviaEngine expects.
    # Replace this with: res = match_labels_and_filters(question, top_k=top_k)
    # Then translate `res` -> dict below.
    q = question.lower()
    return {
        "needs_amount_gt": 10000 if ("10k" in q or "10000" in q) else None,
        "window_days": 60 if "60" in q else 30 if "30" in q else None,
        "next_meeting_days": 14 if "14" in q else None,
        "wants_commit": "commit" in q,
        "wants_roles": [r for r in ["finance","security","economic buyer"] if r in q],
        "stage_eq": "evaluate" if "evaluate" in q else None,
        "stale_days": 21 if "21" in q else 14 if "14" in q else None,
    }

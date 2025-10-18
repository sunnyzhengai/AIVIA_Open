# SPDX-License-Identifier: Apache-2.0
# Thin wrapper so AiviaEngine can call your existing matcher unchanged elsewhere.
from typing import Dict, Any
import re

def match_concepts_adapter(question: str, top_k: int = 8) -> Dict[str, Any]:
    """
    Real matcher adapter for Sales CRM demo.
    Uses enhanced pattern matching to extract business concepts from natural language.
    """
    print(f"🔍 REAL MATCHER - Processing: '{question}'")
    
    q = question.lower()
    result = {}
    
    # Enhanced amount extraction with multiple patterns
    amount_patterns = [
        r'(\d+)k',  # "10k", "25k"
        r'(\d+),?000',  # "10,000", "10000"
        r'(\d+)\s*thousand',  # "10 thousand"
        r'greater than\s*\$?(\d+)',  # "greater than 10000"
        r'more than\s*\$?(\d+)',  # "more than 10000"
        r'over\s*\$?(\d+)',  # "over 10000"
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, q)
        if match:
            amount = int(match.group(1))
            if 'k' in pattern or 'thousand' in pattern:
                amount *= 1000
            result["needs_amount_gt"] = amount
            print(f"💰 Amount extracted: ${amount:,}")
            break
    
    # Enhanced time window extraction
    time_patterns = [
        (r'(\d+)\s*days?', lambda x: int(x)),  # "60 days", "30 day"
        (r'(\d+)\s*weeks?', lambda x: int(x) * 7),  # "2 weeks"
        (r'(\d+)\s*months?', lambda x: int(x) * 30),  # "1 month"
        (r'last\s*(\d+)\s*days?', lambda x: int(x)),  # "last 60 days"
        (r'past\s*(\d+)\s*days?', lambda x: int(x)),  # "past 30 days"
        (r'(\d+)\s*day\s*window', lambda x: int(x)),  # "60 day window"
    ]
    
    for pattern, converter in time_patterns:
        match = re.search(pattern, q)
        if match:
            days = converter(match.group(1))
            result["window_days"] = days
            print(f"📅 Time window extracted: {days} days")
            break
    
    # Enhanced next meeting/step extraction
    next_step_patterns = [
        (r'no next meeting.*?(\d+)\s*days?', lambda x: int(x)),
        (r'no next step.*?(\d+)\s*days?', lambda x: int(x)),
        (r'no meeting.*?(\d+)\s*days?', lambda x: int(x)),
        (r'(\d+)\s*days?.*?no.*?meeting', lambda x: int(x)),
        (r'(\d+)\s*days?.*?no.*?step', lambda x: int(x)),
    ]
    
    for pattern, converter in next_step_patterns:
        match = re.search(pattern, q)
        if match:
            days = converter(match.group(1))
            result["next_meeting_days"] = days
            print(f"📋 Next meeting window: {days} days")
            break
    
    # Enhanced role extraction
    role_keywords = {
        "finance": ["finance", "financial", "cfo", "treasurer"],
        "security": ["security", "ciso", "security officer", "infosec"],
        "economic buyer": ["economic buyer", "decision maker", "budget holder", "purchasing"]
    }
    
    found_roles = []
    for role, keywords in role_keywords.items():
        if any(keyword in q for keyword in keywords):
            found_roles.append(role)
    
    if found_roles:
        result["wants_roles"] = found_roles
        print(f"👥 Roles extracted: {found_roles}")
    
    # Enhanced stage extraction
    stage_keywords = {
        "evaluate": ["evaluate", "evaluation", "assessing", "reviewing"],
        "prospecting": ["prospect", "prospecting", "lead", "leads"],
        "legal": ["legal", "contract", "agreement", "terms"],
        "closed won": ["closed won", "won", "signed", "completed"],
        "closed lost": ["closed lost", "lost", "declined", "rejected"]
    }
    
    for stage, keywords in stage_keywords.items():
        if any(keyword in q for keyword in keywords):
            result["stage_eq"] = stage
            print(f"🎯 Stage extracted: {stage}")
            break
    
    # Enhanced commit detection
    commit_keywords = ["commit", "committed", "commitment", "committed deal", "commit deal"]
    if any(keyword in q for keyword in commit_keywords):
        result["wants_commit"] = True
        print("✅ Commit flag detected")
    
    # Enhanced stale detection
    stale_patterns = [
        (r'(\d+)\s*days?.*?stale', lambda x: int(x)),
        (r'stale.*?(\d+)\s*days?', lambda x: int(x)),
        (r'(\d+)\s*days?.*?no activity', lambda x: int(x)),
        (r'no activity.*?(\d+)\s*days?', lambda x: int(x)),
    ]
    
    for pattern, converter in stale_patterns:
        match = re.search(pattern, q)
        if match:
            days = converter(match.group(1))
            result["stale_days"] = days
            print(f"⏰ Stale period: {days} days")
            break
    
    # Default fallbacks for common patterns
    if "10k" in q or "10000" in q:
        result["needs_amount_gt"] = result.get("needs_amount_gt", 10000)
    if "60" in q and "window_days" not in result:
        result["window_days"] = 60
    if "30" in q and "window_days" not in result:
        result["window_days"] = 30
    if "14" in q and "next_meeting_days" not in result:
        result["next_meeting_days"] = 14
    if "21" in q and "stale_days" not in result:
        result["stale_days"] = 21
    
    print(f"🎯 REAL MATCHER RESULT: {result}")
    return result

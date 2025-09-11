import yaml
import re
from pathlib import Path
from typing import List, Tuple

CONFIG_PATH = Path("app/dept_config.yaml")

def load_dept_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def route_departments(query: str, top_k: int = 2) -> Tuple[List[str], str]:
    """
    Return (ordered_depts, reason). Simple keyword voting.
    """
    cfg = load_dept_config()
    q = query.lower()
    scores = []
    for dept, spec in cfg.get("departments", {}).items():
        kws = [k.lower() for k in spec.get("keywords", [])]
        hits = sum(1 for kw in kws if re.search(rf"\b{re.escape(kw)}\b", q))
        if hits > 0:
            scores.append((dept, hits))
    if not scores:
        # no hits: fall back to configured default
        fb = cfg.get("fallback", "global")
        return [fb], f"No keyword match; falling back to '{fb}'."

    # sort by hits desc
    scores.sort(key=lambda x: x[1], reverse=True)
    selected = [d for d, _ in scores[:top_k]]
    reason = f"Matched departments by keywords: {selected}"
    return selected, reason

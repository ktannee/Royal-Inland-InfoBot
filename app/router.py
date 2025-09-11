import yaml, re
from pathlib import Path
from typing import List, Tuple
from slug import slug

CONFIG_PATH = Path("app/dept_config.yaml")

def load_dept_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def route_departments(query: str, top_k: int = 2) -> Tuple[List[str], str]:
    cfg = load_dept_config()
    q = query.lower()
    scores = []
    for dept_raw, spec in cfg.get("departments", {}).items():
        dept_slug = slug(dept_raw)
        kws = [k.lower() for k in spec.get("keywords", [])]
        hits = sum(1 for kw in kws if re.search(rf"\b{re.escape(kw)}\b", q))
        if hits > 0:
            scores.append((dept_slug, hits, dept_raw))
    if not scores:
        fb = slug(cfg.get("fallback", "global"))
        return [fb], f"No keyword match; falling back to '{fb}'."
    scores.sort(key=lambda x: x[1], reverse=True)
    selected_slugs = [d for d, _, _ in scores[:top_k]]
    human = [r for _, _, r in scores[:top_k]]
    reason = f"Matched departments: {human} → {selected_slugs}"
    return selected_slugs, reason

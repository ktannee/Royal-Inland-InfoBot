import re

def slug(s: str) -> str:
    """Normalize dept names to a file/ID-safe slug."""
    s = s.strip().lower()
    s = re.sub(r"[\s\-]+", "_", s)     # spaces & hyphens -> underscore
    s = re.sub(r"[^a-z0-9_]", "", s)   # drop anything weird
    return s

from app.router import route_departments
from app.slug import slug

def test_router_mental_health_keywords():
    q = "I need mental health services. Who do I call?"
    depts, reason = route_departments(q, top_k=2)
    assert "mental_health" in [slug(d) for d in depts], reason

def test_router_fallback_global():
    q = "completely unrelated text"
    depts, reason = route_departments(q, top_k=2)
    assert depts and depts[0] in {"global", slug("global")}, reason

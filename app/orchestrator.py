from typing import Optional
from app.agents.registry import get_registered_agents
from app.guardrails import pre_answer_guardrails, post_answer_guardrails
from app.rag_pipeline import retrieve_with_routing, generate_answer

def handle_query(query: str):
    """
    Returns a dict:
      {
        "answer": str | None,
        "blocked_msg": str | None,
        "route_reason": str,
        "contexts": list[str],
        "scores": list[float],
        "agent": str | None
      }
    """
    # 1) Retrieve (includes department routing)
    contexts, scores, route_reason = retrieve_with_routing(query, k_per_dept=3, max_depts=2)

    # 2) Global guardrails (emergency, PII, medical advice, low-confidence)
    allow, blocked_msg = pre_answer_guardrails(query, scores)
    if not allow:
        return {
            "answer": None,
            "blocked_msg": blocked_msg,
            "route_reason": route_reason,
            "contexts": contexts,
            "scores": scores,
            "agent": None,
        }

    # 3) Agent selection & execution
    for agent in get_registered_agents():
        if agent.can_handle(query):
            result = agent.run(query, contexts)
            if result.get("allowed"):
                return {
                    "answer": result.get("answer"),
                    "blocked_msg": None,
                    "route_reason": route_reason,
                    "contexts": contexts,
                    "scores": scores,
                    "agent": agent.name,
                }
            else:
                # Agent abstained (e.g., no numbers found) -> show its safe fallback
                return {
                    "answer": None,
                    "blocked_msg": result.get("fallback"),
                    "route_reason": route_reason,
                    "contexts": contexts,
                    "scores": scores,
                    "agent": agent.name,
                }

    # 4) Fallback to generic RAG generation (with post-answer safety)
    answer = generate_answer(query, contexts)
    ok, post_msg = post_answer_guardrails(answer)
    if not ok:
        return {
            "answer": None,
            "blocked_msg": post_msg,
            "route_reason": route_reason,
            "contexts": contexts,
            "scores": scores,
            "agent": None,
        }

    return {
        "answer": answer,
        "blocked_msg": None,
        "route_reason": route_reason,
        "contexts": contexts,
        "scores": scores,
        "agent": None,
    }

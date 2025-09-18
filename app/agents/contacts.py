from typing import List, Dict, Any
from app.guardrails import extract_contacts
from app.config import LOW_CONF_FALLBACK, HOSPITAL_SWITCHBOARD, HEALTHLINK_BC

CONTACT_TRIGGERS = [
    "contact", "phone", "call", "number", "who do i call",
    "hotline", "helpline", "reach", "switchboard"
]

class ContactsAgent:
    """
    Service Directory & Contacts Agent
    - Deterministically extracts phone numbers / special helplines from retrieved contexts.
    - Never invents numbers; if none found, falls back to switchboard.
    """

    name = "contacts"

    def can_handle(self, query: str) -> bool:
        t = query.lower()
        return any(k in t for k in CONTACT_TRIGGERS)

    def run(self, query: str, contexts: List[str]) -> Dict[str, Any]:
        phones, flags = extract_contacts(contexts)  # flags may include "310-MHSU (6478)"
        if not phones and not flags:
            # Minimal safe fallback: don't guess; offer switchboard
            return {
                "allowed": False,
                "answer": None,
                "citations": [],
                "fallback": (
                    f"I couldn’t find a specific number in the documents. "
                    f"Please call the hospital switchboard at **{HOSPITAL_SWITCHBOARD}**."
                )
            }

        lines = []
        if flags:
            lines.append(f"• Call **{', '.join(flags)}**")
        if phones:
            # De-duplicate while preserving order
            seen = set()
            uniq = [p for p in phones if not (p in seen or seen.add(p))]
            lines.append(f"• Other numbers found: **{', '.join(uniq)}**")
        lines.append(f"• For general health advice in BC: **HealthLink BC at {HEALTHLINK_BC}**")

        return {
            "allowed": True,
            "answer": "\n".join(lines),
            "citations": [],   # optional: add URLs or doc ids if you track them
            "fallback": None
        }
import re
from typing import List, Tuple
from app.config import (
    EMERGENCY_MESSAGE, NON_URGENT_ADVICE_MESSAGE, LOW_CONF_FALLBACK,
    RETRIEVAL_SIM_THRESHOLD, MIN_STRONG_MATCHES
)

PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b")
MHSU_SHORT = re.compile(r"\b310[-\s]?MHSU\b", re.IGNORECASE)
# --- Keyword sets ---

EMERGENCY_KEYWORDS = {
    "chest pain", "severe chest pain", "shortness of breath", "can’t breathe",
    "cannot breathe", "trouble breathing", "stroke", "face droop", "arm weak",
    "slurred speech", "heart attack", "uncontrolled bleeding", "bleeding a lot",
    "suicidal", "suicide", "overdose", "poison", "passed out", "fainted",
    "seizure", "seizing", "head injury", "gunshot", "stab wound"
}

# Phrases that try to elicit diagnosis/treatment/interpretation
MEDICAL_ADVICE_PATTERNS = [
    r"\bdiagnos(e|is|ing)\b",
    r"\bwhat (is|could be) my condition\b",
    r"\bshould i take\b",
    r"\bprescribe\b",
    r"\btreatment plan\b",
    r"\binterpret (my )?(lab|test|report|mri|x-?ray|ct)\b",
    r"\bmy (mri|ct|scan|lab|test) (says|shows)\b",
    r"\bdo i have\b",
    r"\bis this cancer\b",
]

CONTACT_INTENT = {"contact", "phone", "call", "number", "hours", "location",
                  "where", "address", "how do i reach", "who do i call"}

# Very light profanity/abuse filter (expand as needed)
PROFANITY = {"fuck you", "fuck", "f***", "f**k", "bitch", "asshole", "stupid", "idiot"}

# Basic PII regex (heuristics; not perfect)
EMAIL_RE   = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE   = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b")
DOB_RE     = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b", re.IGNORECASE)
MRN_HINTS  = re.compile(r"\b(MRN|medical record|health number|PHN)\b", re.IGNORECASE)
NAME_HINTS = re.compile(r"\bmy name is\b", re.IGNORECASE)

def contains_emergency(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in EMERGENCY_KEYWORDS)

def requests_medical_advice(text: str) -> bool:
    t = text.lower()
      # ✅ If clearly a contact/wayfinding request, do NOT treat as medical advice
    if any(kw in t for kw in CONTACT_INTENT):
        return False
    if any(w in t for w in PROFANITY):
        # profanity is handled separately, but still treat as out-of-scope
        return False
    return any(re.search(pat, t) for pat in MEDICAL_ADVICE_PATTERNS)

def contains_pii(text: str) -> bool:
    return bool(
        EMAIL_RE.search(text) or PHONE_RE.search(text) or DOB_RE.search(text)
        or MRN_HINTS.search(text) or NAME_HINTS.search(text)
    )

def retrieval_strength(scores: List[float]) -> Tuple[int, float]:
    """Return (# of strong matches, best score)."""
    strong = [s for s in scores if s >= RETRIEVAL_SIM_THRESHOLD]
    return len(strong), (max(scores) if scores else 0.0)

def pre_answer_guardrails(user_text: str, retrieved_scores: List[float]):
    """Return (allow_generation: bool, message_if_blocked: str or None)."""
    t = user_text.lower()
    is_contact = any(k in t for k in CONTACT_INTENT)

    # 1) Emergencies
    if contains_emergency(user_text):
        return False, EMERGENCY_MESSAGE

    # 2) PII
    if contains_pii(user_text):
        return False, (
            "For your privacy, please **don’t share personal details** (name, email, phone, MRN, "
            "DOB, or medical history) here. Ask your question without personal identifiers."
        )

    # 3) Medical advice
    if requests_medical_advice(user_text):
        return False, NON_URGENT_ADVICE_MESSAGE

    # 4) Retrieval strength (hallucination guard)
    # count, best = retrieval_strength(retrieved_scores)
    # if count < MIN_STRONG_MATCHES:
    #     return False, LOW_CONF_FALLBACK
    
    # 5) Loosen the "abstain" rule for directory/helpline queries
    strong = [s for s in retrieved_scores if s >= RETRIEVAL_SIM_THRESHOLD]
    # if not is_contact:
    #     if len(strong) < MIN_STRONG_MATCHES:
    # Contact/wayfinding: allow if at least one strong match
    if is_contact:
            if len(strong)<1:
                return False, LOW_CONF_FALLBACK
    else:
        # for non-contact intent, require the usual minimum strong matches
        if len(strong) < MIN_STRONG_MATCHES:
            return False, LOW_CONF_FALLBACK

    return True, None

def post_answer_guardrails(generated_text: str):
    """Light post-check to ensure we didn't accidentally provide medical advice."""
    # If the model slipped and gave advice words—very conservative check
    t = generated_text.lower()
    if re.search(r"\b(you should|take|start|use|dose|dosage|prescribe|avoid)\b", t):
        return (
            False,
            NON_URGENT_ADVICE_MESSAGE + " I can help with hospital locations, hours, and services if you’d like."
        )
    return True, None

def extract_contacts(texts):
    phones = set()
    flags = set()
    for t in texts:
        for m in PHONE_RE.findall(t):
            phones.add(m.strip())
        if MHSU_SHORT.search(t):
            flags.add("310-MHSU (6478)")
    return sorted(phones), sorted(flags)
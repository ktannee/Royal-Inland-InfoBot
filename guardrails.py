import re
from typing import List, Tuple
from config import (
    EMERGENCY_MESSAGE, NON_URGENT_ADVICE_MESSAGE, LOW_CONF_FALLBACK,
    RETRIEVAL_SIM_THRESHOLD, MIN_STRONG_MATCHES
)

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
    r"\bshould I take\b",
    r"\bprescribe\b",
    r"\btreatment plan\b",
    r"\binterpret (my )?(lab|test|report|mri|x-?ray|ct)\b",
    r"\bmy (mri|ct|scan|lab|test) (says|shows)\b",
    r"\bdo I have\b",
    r"\bis this cancer\b",
]

# Very light profanity/abuse filter (expand as needed)
PROFANITY = {"fuck", "f***", "f**k", "bitch", "asshole", "stupid", "idiot"}

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
    count, best = retrieval_strength(retrieved_scores)
    if count < MIN_STRONG_MATCHES:
        return False, LOW_CONF_FALLBACK

    return True, None

def post_answer_guardrails(generated_text: str):
    """Light post-check to ensure we didn't accidentally provide medical advice."""
    # If the model slipped and gave advice words—very conservative check
    if re.search(r"\b(you should|take|start|use|dose|dosage|prescribe|avoid)\b", generated_text.lower()):
        return (
            False,
            NON_URGENT_ADVICE_MESSAGE + " I can help with hospital locations, hours, and services if you’d like."
        )
    return True, None

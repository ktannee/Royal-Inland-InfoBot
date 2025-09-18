HOSPITAL_NAME = "Royal Inland Hospital (RIH), Kamloops, BC"

# What to say for emergencies
EMERGENCY_MESSAGE = (
    "This sounds urgent. Please call **911** or go to the nearest **Emergency Department** immediately."
)

# Where to redirect non-urgent medical questions
NON_URGENT_ADVICE_MESSAGE = (
    "I can’t provide medical advice. For non-emergencies, consider calling **HealthLink BC at 811**, "
    "or contact your healthcare provider."
)

# Generic fallback when info isn’t in the KB
LOW_CONF_FALLBACK = (
    "I don’t have enough verified information to answer that. "
    "Please contact the hospital information desk or check official Interior Health pages."
)

# A short disclaimer you can display in the UI
DISCLAIMER = (
    "I provide general hospital information sourced from uploaded documents. "
    "I **do not** give medical advice or interpret personal health information."
)

# Retrieval similarity threshold (cosine; 0..1)
RETRIEVAL_SIM_THRESHOLD = 0.35

# Minimum number of strong matches required to answer
MIN_STRONG_MATCHES = 2

# Canonical switchboard or general contact for fallbacks
HOSPITAL_SWITCHBOARD = "250-374-5111"   # update if you have a different master number

# Static, well-known provincial line you want to show with contact answers
HEALTHLINK_BC = "811"

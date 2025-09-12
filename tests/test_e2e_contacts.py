from app.guardrails import extract_contacts

def test_e2e_contact_response_from_context():
    contexts = ["""
    If you or someone you know is struggling, find support.
    Call 310-MHSU (6478) to reach your local Mental Health & Substance Use centre.
    For general health advice, call HealthLink BC at 811.
    """]
    phones, flags = extract_contacts(contexts)
    assert "310-MHSU (6478)" in flags

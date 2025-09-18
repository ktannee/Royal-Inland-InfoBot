from app.agents.contacts import ContactsAgent

def test_contacts_agent_happy_path():
    agent = ContactsAgent()
    q = "Who do I call for mental health services? I need a contact number."
    ctx = [
        "Find support. Call 310-MHSU (6478) to reach your local centre.",
        "General enquiries: 250-374-5111."
    ]
    assert agent.can_handle(q)
    res = agent.run(q, ctx)
    assert res["allowed"] is True
    assert "310-MHSU (6478)" in res["answer"]

def test_contacts_agent_fallback():
    agent = ContactsAgent()
    q = "What's the phone number?"
    ctx = ["This page has no numbers."]
    res = agent.run(q, ctx)
    assert res["allowed"] is False
    assert "switchboard" in res["fallback"].lower()
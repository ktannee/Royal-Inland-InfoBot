from typing import List
from agents.contacts import ContactsAgent

def get_registered_agents() -> List[object]:
    # Order matters: first agent that claims it can handle the query will run
    return [
        ContactsAgent(),
        # Add more agents here later (HoursAgent, NavigationAgent, AlertsAgent, ...)
    ]
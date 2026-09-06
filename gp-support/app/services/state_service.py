def get_empty_state() -> dict:
    """Returns the default empty state for a new consultation."""
    return {
        "reason_for_visit": None,
        "symptoms": [],
        "symptom_location": None,
        "onset": None,
        "duration": None,
        "severity": None,
        "medical_history": {"status": "unknown", "items": []},
        "current_medications": {"status": "unknown", "items": []},
        "allergies": {"status": "unknown", "items": []},
        "additional_concerns": None,
        "missing_information": [
            "reason_for_visit", "symptoms", "onset", "duration",
            "severity", "medical_history", "current_medications", "allergies"
        ],
        "conversation_complete": False,
        "summary": ""
    }

def format_state_for_prompt(state: dict) -> str:
    """Formats the JSON state into a readable string for the system prompt."""

    if not state:
        state = get_empty_state()

    formatted = "CURRENT EXTRACTED PATIENT INFORMATION:\n"

    for key, value in state.items():
        if key in ["missing_information", "conversation_complete", "consultation_id"]:
            continue # We don't need to feed these specific meta-fields back to the chat model

        # Format the complex objects (allergies, meds, history)
        if isinstance(value, dict) and "status" in value:
            status = value["status"]
            items = ", ".join(value["items"]) if value.get("items") else "None noted"
            formatted += f"- {key.replace('_', ' ').title()}: [{status.upper()}] {items}\n"
        # Format lists (symptoms)
        elif isinstance(value, list):
            items = ", ".join(value) if value else "None noted"
            formatted += f"- {key.replace('_', ' ').title()}: {items}\n"
        # Format basic strings
        else:
            formatted += f"- {key.replace('_', ' ').title()}: {value if value else 'Unknown'}\n"

    return formatted
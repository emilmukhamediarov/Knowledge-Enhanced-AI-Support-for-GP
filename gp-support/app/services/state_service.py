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

def get_next_phase(state: dict) -> str:
    """
    Decide the broad next stage of the consultation.

    The LLM can decide how to phrase a question,
    but Python decides what category of information
    should be collected next.
    """

    if not state:
        return "explore_problem"

    # Current problem is not sufficiently described yet.
    core_problem_fields = [
        state.get("reason_for_visit"),
        state.get("symptoms"),
        state.get("onset"),
        state.get("duration"),
        state.get("severity"),
    ]

    if any(
        value is None or value == []
        for value in core_problem_fields
    ):
        return "explore_problem"

    medical_history = state.get("medical_history", {})
    if medical_history.get("status") == "unknown":
        return "confirm_medical_history"

    medications = state.get("current_medications", {})
    if medications.get("status") == "unknown":
        return "confirm_medications"

    allergies = state.get("allergies", {})
    if allergies.get("status") == "unknown":
        return "confirm_allergies"

    if state.get("additional_concerns") is None:
        return "additional_concerns"

    return "complete"

def get_phase_instruction(
    phase: str,
    patient_profile: dict | None = None
) -> str:

    patient_profile = patient_profile or {}

    if phase == "explore_problem":
        return """
CURRENT CONSULTATION PHASE: EXPLORE CURRENT PROBLEM

- Continue gathering information about the patient's active complaint.
- Do NOT move to routine medical history, medications, allergies, or additional concerns yet.
- Ask exactly ONE useful question about the current problem.
- Use information already collected and do not repeat answered questions.
"""

    if phase == "confirm_medical_history":
        medical_history = patient_profile.get("medical_history")

        if medical_history:
            return f"""
CURRENT CONSULTATION PHASE: CONFIRM MEDICAL HISTORY

- Do NOT ask about medications, allergies, or additional concerns yet.
- The patient's recorded medical history is:
  {medical_history}
- Ask ONE question confirming whether this medical history is still correct.
- Do not ask the patient to provide their medical history from scratch.
"""

        return """
CURRENT CONSULTATION PHASE: COLLECT MEDICAL HISTORY

- Do NOT ask about medications, allergies, or additional concerns yet.
- No medical history is currently recorded.
- Ask ONE question about relevant medical history or health conditions.
"""

    if phase == "confirm_medications":
        medications = patient_profile.get("medications")

        if medications is not None:
            medication_text = (
                ", ".join(medications)
                if medications
                else "none"
            )

            return f"""
CURRENT CONSULTATION PHASE: CONFIRM MEDICATIONS

- Do NOT ask about allergies or additional concerns yet.
- The patient's recorded current medications are:
  {medication_text}
- Ask ONE question confirming whether this medication information is still correct.
- Do not ask for medications from scratch.
"""

        return """
CURRENT CONSULTATION PHASE: COLLECT MEDICATIONS

- Do NOT ask about allergies or additional concerns yet.
- No medication information is currently recorded.
- Ask ONE question about current medications.
"""

    if phase == "confirm_allergies":
        allergies = patient_profile.get("allergies")

        if allergies is not None:
            allergy_text = (
                ", ".join(allergies)
                if allergies
                else "none"
            )

            return f"""
CURRENT CONSULTATION PHASE: CONFIRM ALLERGIES

- Do NOT move to additional concerns yet.
- The patient's recorded allergies are:
  {allergy_text}
- Ask ONE question confirming whether this allergy information is still correct.
- Do not ask about allergies from scratch.
"""

        return """
CURRENT CONSULTATION PHASE: COLLECT ALLERGIES

- No allergy information is currently recorded.
- Ask ONE question about allergies.
"""

    if phase == "additional_concerns":
        return """
CURRENT CONSULTATION PHASE: ADDITIONAL CONCERNS

- Required consultation information has been collected.
- Ask ONE question asking whether the patient has any additional concerns for their doctor.
"""

    if phase == "complete":
        return """
CURRENT CONSULTATION PHASE: COMPLETE

- The required consultation information has been collected.
- Do not ask another question.
- Respond ONLY with the appropriate translated equivalent of:
  "Your pre-consultation information is complete."
"""

    return ""



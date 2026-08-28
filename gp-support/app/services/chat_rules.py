import re


def is_advice_request(text: str) -> bool:
    text = text.lower().strip()

    patterns = [
        r"\b(?:should|can|could|may)\s+i\s+(?:take|use|have)\b",
        r"\bdo you think i\s+(?:should|can|could|may)\s+(?:take|use|have)\b",
        r"\bis it (?:okay|ok|safe) (?:for me )?to (?:take|use)\b",
        r"\bwhat (?:should|can|could) i (?:take|do|use)\b",
        r"\bwhat do you recommend\b",
        r"\bany advice\b",
        r"\bhow (?:should|can) i treat\b",
    ]

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )

def has_high_severity_rating(text: str) -> bool:
    text = text.lower().strip()

    patterns = [
        r"^(9|10)\b",
        r"\b(9|10)\s*/\s*10\b",
        r"\b(9|10)\s+out of\s+10\b",
        r"\b(?:it is|it's|pain is|severity is)\s+(9|10)\b",
    ]

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


def keep_one_question(reply: str) -> str:
    first_question = reply.find("?")

    if first_question == -1:
        return reply

    return reply[:first_question + 1].strip()


def remove_medical_advice(reply: str) -> str:
    blocked_phrases = [
        "stay hydrated",
        "staying hydrated",
        "drink more water",
        "monitor your temperature",
        "monitor your symptoms",
        "follow their recommendations",
        "i recommend",
        "you should take",
        "you should use",
        "you need to take",
        "you should drink",
        "you need to drink",

        # Clinical interpretation
        "that's a fever",
        "that is a fever",
        "is considered high",
        "is considered low",
        "that's high",
        "that is high",
    ]

    sentences = reply.split(". ")

    safe_sentences = []

    for sentence in sentences:
        sentence_lower = sentence.lower()

        if any(
            phrase in sentence_lower
            for phrase in blocked_phrases
        ):
            continue

        safe_sentences.append(sentence)

    return ". ".join(safe_sentences).strip()



def get_missing_background_field(messages):
    answered = {
        "medical_history": False,
        "medications": False,
        "allergies": False,
    }

    previous_assistant = ""

    for message in messages:
        content = message.content.lower().strip()

        if message.role == "assistant":
            previous_assistant = content
            continue

        if message.role != "user":
            continue

        # Patient explicitly talked about allergies
        if "allerg" in content:
            answered["allergies"] = True

        # Patient explicitly talked about medications
        medication_words = [
            "medication",
            "medications",
            "medicine",
            "medicines",
            "meds",
        ]

        if any(word in content for word in medication_words):
            answered["medications"] = True

        # Work out what the previous assistant question was asking
        asked_history = (
            "medical history" in previous_assistant
            or "medical condition" in previous_assistant
            or "chronic condition" in previous_assistant
        )

        asked_medications = (
            "medication" in previous_assistant
            or "medications" in previous_assistant
            or "medicine" in previous_assistant
        )

        asked_allergies = "allerg" in previous_assistant

        # If the user answered the actual question,
        # mark that field as completed.

        if asked_history:
            # "no allergies" should NOT count as medical history
            if (
                "allerg" not in content
                and not any(
                    word in content
                    for word in medication_words
                )
            ):
                answered["medical_history"] = True

        if asked_medications:
            # "no allergies" should NOT count as medications
            if "allerg" not in content:
                answered["medications"] = True

        if asked_allergies:
            answered["allergies"] = True

    if not answered["medical_history"]:
        return "medical_history"

    if not answered["medications"]:
        return "medications"

    if not answered["allergies"]:
        return "allergies"

    return None


def background_question(field):
    questions = {
        "medical_history": (
            "Do you have any relevant medical conditions or medical history?"
        ),
        "medications": (
            "Are you currently taking any medications?"
        ),
        "allergies": (
            "Do you have any allergies?"
        ),
    }

    return questions[field]
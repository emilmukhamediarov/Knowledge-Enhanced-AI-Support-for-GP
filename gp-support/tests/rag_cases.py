"""Fixed evaluation cases for the GP Support RAG pipeline.

The cases test both retrieval quality and grounded clinical behaviour.
They intentionally include cases that expose known weaknesses in the
current implementation so improvements can be measured objectively.
"""

def _answer(status="confirmed_none", items=None):
    return {
        "status": status,
        "items": items or [],
    }


def _summary(
    *,
    reason_for_visit,
    symptoms,
    symptom_location=None,
    onset=None,
    duration=None,
    severity=None,
    medical_history=None,
    current_medications=None,
    allergies=None,
    additional_concerns=None,
):
    return {
        "reason_for_visit": reason_for_visit,
        "symptoms": symptoms,
        "symptom_location": symptom_location,
        "onset": onset,
        "duration": duration,
        "severity": severity,
        "medical_history": medical_history or _answer(),
        "current_medications": current_medications or _answer(),
        "allergies": allergies or _answer(),
        "additional_concerns": additional_concerns,
    }


RAG_CASES = [
    {
        "name": "persistent_cough_4_weeks",
        "purpose": (
            "Tests whether a duration threshold from the acute bronchitis "
            "guidance can be applied to the patient case."
        ),
        "summary": _summary(
            reason_for_visit="persistent cough",
            symptoms=["cough"],
            onset="4 weeks ago",
            duration="4 weeks",
            severity="moderate",
        ),
        "expected_source_files": [
            "Chest Cold (Acute Bronchitis).txt",
        ],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "cough_with_bloody_mucus_in_additional_concerns",
        "purpose": (
            "Tests whether additional_concerns reaches RAG reasoning. "
            "The current query builder does not include this field."
        ),
        "summary": _summary(
            reason_for_visit="persistent cough",
            symptoms=["cough"],
            duration="1 week",
            additional_concerns="I noticed bloody mucus when coughing.",
        ),
        "expected_source_files": [
            "Chest Cold (Acute Bronchitis).txt",
        ],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "cold_12_days_without_improvement",
        "purpose": (
            "Tests whether the common-cold duration criterion is applied "
            "using the patient's full case."
        ),
        "summary": _summary(
            reason_for_visit="cold symptoms",
            symptoms=["runny nose", "sore throat", "cough"],
            duration="12 days",
            additional_concerns="The symptoms have not improved.",
        ),
        "expected_source_files": [
            "Cold.txt",
        ],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "meningococcal_clinical_features",
        "purpose": (
            "Tests retrieval for an explicitly "
            "high-concern symptom combination in the knowledge base."
        ),
        "summary": _summary(
            reason_for_visit="sudden fever and rash",
            symptoms=[
                "sudden high fever",
                "neck stiffness",
                "confusion",
                "purpuric rash",
            ],
            onset="today",
            duration="1 day",
            severity="severe",
        ),
        "expected_source_files": [
            "Meningococcal Disease.txt",
        ],
        # RAG should surface grounded guidance, not propose another diagnosis
        # merely because a second semantically similar document was retrieved.
        "forbidden_answer_terms_any": [
            "could be indicative of Lyme",
            "indicative of Lyme Disease",
        ],
        "expect_no_match": False,
    },
    {
        "name": "asthma_pattern",
        "purpose": (
            "Tests straightforward asthma retrieval and rejects a false "
            "bronchitis duration criterion that the patient does not meet."
        ),
        "summary": _summary(
            reason_for_visit="breathing problems",
            symptoms=[
                "wheezing",
                "chest tightness",
                "cough at night",
            ],
            duration="2 weeks",
        ),
        "expected_source_files": [
            "Asthma.txt",
        ],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "strep_throat_pattern",
        "purpose": (
            "Tests straightforward strep-throat retrieval and verifies that "
            "ordinary listed symptoms are described accurately."
        ),
        "summary": _summary(
            reason_for_visit="sore throat",
            symptoms=[
                "fever",
                "pain when swallowing",
                "red swollen tonsils",
            ],
            onset="2 days ago",
            duration="2 days",
        ),
        "expected_source_files": [
            "Strep Throat.txt",
        ],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "pink_eye_pattern",
        "purpose": (
            "Tests conjunctivitis retrieval and verifies that conditional "
            "contact-lens guidance is not applied when contact-lens use "
            "was never stated by the patient."
        ),
        "summary": _summary(
            reason_for_visit="red eye",
            symptoms=[
                "purulent eye discharge",
                "eyelids matted together",
                "decreased vision",
            ],
            symptom_location="left eye",
            duration="2 days",
        ),
        "expected_source_files": [
            "Pink Eye.txt",
        ],
        "forbidden_answer_terms_any": [
            "contact lens wearers with these symptoms should",
        ],
        "expect_no_match": False,
    },
    {
        "name": "unsupported_urinary_presentation",
        "purpose": (
            "Negative-control case: the supplied knowledge base contains "
            "no urinary-condition document, so retrieval should reject "
            "the presentation rather than force an unrelated match."
        ),
        "summary": _summary(
            reason_for_visit="burning when urinating",
            symptoms=["burning urination", "urinary frequency"],
            duration="3 days",
        ),
        "expected_source_files": [],
        "forbidden_answer_terms_any": [],
        "expect_no_match": True,
    },
    {
        "name": "appendicitis_migrating_abdominal_pain",
        "purpose": "Tests retrieval and urgent-care guidance for abdominal pain that moves to the lower right side.",
        "summary": _summary(
            reason_for_visit="worsening abdominal pain",
            symptoms=["pain around belly button", "pain moved to lower right abdomen"],
            duration="several hours",
        ),
        "expected_source_files": ["Appendicitis.txt"],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "food_poisoning_dehydration",
        "purpose": "Tests retrieval for vomiting and diarrhea with signs of dehydration.",
        "summary": _summary(
            reason_for_visit="vomiting and diarrhea",
            symptoms=["vomiting", "diarrhea", "urinating less than usual"],
            duration="2 days",
        ),
        "expected_source_files": ["Food poisoning.txt"],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "norovirus_after_exposure",
        "purpose": "Tests retrieval for vomiting and diarrhea starting after contact with someone ill.",
        "summary": _summary(
            reason_for_visit="vomiting and diarrhea",
            symptoms=["vomiting", "diarrhea", "nausea"],
            onset="1 day ago",
            duration="1 day",
            additional_concerns="I was around someone with a stomach bug two days ago.",
        ),
        "expected_source_files": ["Norovirus Stomach Bug.txt"],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "ankle_sprain_recent_injury",
        "purpose": "Tests retrieval for a recent ankle sprain and the source's initial self-care guidance.",
        "summary": _summary(
            reason_for_visit="ankle injury",
            symptoms=["ankle pain", "swelling", "bruising"],
            onset="yesterday",
            duration="1 day",
        ),
        "expected_source_files": ["Sprains and strains.txt"],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "child_ear_infection_persistent_symptoms",
        "purpose": "Tests retrieval for a child's ear pain lasting longer than the source's 2–3 day threshold.",
        "summary": _summary(
            reason_for_visit="child's ear pain",
            symptoms=["ear pain", "fever"],
            duration="4 days",
        ),
        "expected_source_files": ["Ear Infection.txt"],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "tick_bite_expanding_rash",
        "purpose": "Tests retrieval for an expanding rash after a tick bite.",
        "summary": _summary(
            reason_for_visit="rash after tick bite",
            symptoms=["expanding rash", "fatigue"],
            onset="about a week ago",
            duration="several days",
            additional_concerns="I was bitten by a tick before the rash appeared.",
        ),
        "expected_source_files": ["Lyme Disease.txt"],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "pregnancy_chickenpox_exposure",
        "purpose": "Tests retrieval for chickenpox exposure in a person at higher risk of severe illness.",
        "summary": _summary(
            reason_for_visit="chickenpox exposure",
            symptoms=["no symptoms"],
            duration="exposed yesterday",
            medical_history=_answer(
                status="confirmed",
                items=["pregnant", "no evidence of immunity to chickenpox"],
            ),
        ),
        "expected_source_files": ["Chickenpox (Varicella).txt"],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
    {
        "name": "heartburn_after_meals",
        "purpose": "Tests retrieval for heartburn and reflux symptoms associated with meals and lying down.",
        "summary": _summary(
            reason_for_visit="burning feeling in chest",
            symptoms=["heartburn", "sour taste in mouth"],
            duration="intermittent",
            additional_concerns="It is worse after eating and when lying down.",
        ),
        "expected_source_files": ["Heartburn and acid reflux.txt"],
        "forbidden_answer_terms_any": [],
        "expect_no_match": False,
    },
]

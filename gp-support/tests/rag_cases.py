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
        "expected_red_flag_terms_any": [
            "more than 3 weeks",
            "3 weeks",
        ],
        "expect_red_flags_empty": False,
        "forbidden_red_flag_terms_any": [],
        "forbidden_answer_terms_any": [],
        # We deliberately do not equate "seek medical care" with urgent.
        "expected_urgent": None,
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
        "expected_red_flag_terms_any": [
            "bloody mucus",
            "blood",
        ],
        "expect_red_flags_empty": False,
        "forbidden_red_flag_terms_any": [],
        "forbidden_answer_terms_any": [],
        "expected_urgent": None,
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
        "expected_red_flag_terms_any": [
            "more than 10 days",
            "10 days",
            "without improvement",
        ],
        "expect_red_flags_empty": False,
        "forbidden_red_flag_terms_any": [],
        "forbidden_answer_terms_any": [],
        "expected_urgent": None,
        "expect_no_match": False,
    },
    {
        "name": "meningococcal_clinical_features",
        "purpose": (
            "Tests retrieval and red-flag matching for an explicitly "
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
        "expected_red_flag_terms_any": [
            "neck stiffness",
            "purpuric",
            "petechial",
            "confusion",
        ],
        "expect_red_flags_empty": False,
        "forbidden_red_flag_terms_any": [],
        # RAG should surface grounded guidance, not propose another diagnosis
        # merely because a second semantically similar document was retrieved.
        "forbidden_answer_terms_any": [
            "could be indicative of Lyme",
            "indicative of Lyme Disease",
        ],
        "expected_urgent": True,
        "expect_no_match": False,
    },
    {
        "name": "asthma_pattern",
        "purpose": (
            "Tests straightforward asthma retrieval and rejects a false "
            "bronchitis duration red flag that the patient does not meet."
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
        "expected_red_flag_terms_any": [],
        "expect_red_flags_empty": True,
        "forbidden_red_flag_terms_any": [
            "more than 3 weeks",
            "3 weeks",
        ],
        "forbidden_answer_terms_any": [],
        "expected_urgent": False,
        "expect_no_match": False,
    },
    {
        "name": "strep_throat_pattern",
        "purpose": (
            "Tests straightforward strep-throat retrieval and verifies that "
            "ordinary listed symptoms are not relabelled as red flags."
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
        "expected_red_flag_terms_any": [],
        "expect_red_flags_empty": True,
        "forbidden_red_flag_terms_any": [
            "fever",
            "pain when swallowing",
            "red swollen tonsils",
        ],
        "forbidden_answer_terms_any": [],
        "expected_urgent": False,
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
        "expected_red_flag_terms_any": [],
        "expect_red_flags_empty": True,
        "forbidden_red_flag_terms_any": [
            "contact lens",
            "keratitis",
        ],
        "forbidden_answer_terms_any": [
            "contact lens wearers with these symptoms should",
        ],
        "expected_urgent": False,
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
        "expected_red_flag_terms_any": [],
        "expect_red_flags_empty": True,
        "forbidden_red_flag_terms_any": [],
        "forbidden_answer_terms_any": [],
        "expected_urgent": False,
        "expect_no_match": True,
    },
]

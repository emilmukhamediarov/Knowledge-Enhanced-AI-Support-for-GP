"""Supervised-style end-to-end checks for the GP Support RAG pipeline.

Run all cases:
    python -m tests.rag_supervised_evaluation

Run one case:
    python -m tests.rag_supervised_evaluation --case heartburn_after_meals
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from llama_index.core.postprocessor import SimilarityPostprocessor

from app.services.knowledge_rag import (
    ask_structured,
    build_query_from_consultation_summary,
    load_index,
)


TOP_K = 2
SIMILARITY_CUTOFF = 0.67


def _summary(
    *,
    reason_for_visit: str,
    symptoms: list[str],
    symptom_location: str | None = None,
    medical_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "reason_for_visit": reason_for_visit,
        "symptoms": symptoms,
        "symptom_location": symptom_location,
        "medical_history": medical_history or {
            "status": "confirmed_none",
            "items": [],
        },
        "current_medications": {
            "status": "confirmed_none",
            "items": [],
        },
    }


CASES = [
    {
        "name": "appendicitis_migrating_pain",
        "summary": _summary(
            reason_for_visit="abdominal pain moving to the lower right side",
            symptoms=[
                "pain started around the belly button",
                "pain moved to the lower right abdomen",
                "pain is getting worse",
            ],
        ),
        "expected_source": "Appendicitis.txt",
        "required_answer_groups": [
            ["appendicitis"],
            [
                "belly button",
                "navel",
                "umbilical",
                "middle of the abdomen",
                "center of the abdomen",
                "centre of the abdomen",
                "central abdominal pain",
            ],
            [
                "lower right",
                "right lower",
            ],
        ],
        "forbidden_answer_terms": [
            "appendicitis is harmless",
            "appendicitis never requires treatment",
        ],
    },
    {
        "name": "food_poisoning_with_dehydration",
        "summary": _summary(
            reason_for_visit="vomiting and diarrhea after eating",
            symptoms=[
                "vomiting",
                "diarrhea",
                "urinating less than usual",
            ],
        ),
        "expected_source": "Food poisoning.txt",
        "required_answer_groups": [
            ["food poisoning", "foodborne illness", "food-borne illness"],
            ["dehydration", "dehydrated"],
            [
                "drink",
                "oral rehydration",
                "small sips",
                "fluid intake",
                "replace lost fluids",
                "replace fluids",
            ],
        ],
        "forbidden_answer_terms": [
            "food poisoning never causes dehydration",
            "fluids are unnecessary for food poisoning",
        ],
    },
    {
        "name": "norovirus_vomiting_and_diarrhea",
        "summary": _summary(
            reason_for_visit="vomiting and diarrhea after contact with a sick person",
            symptoms=[
                "vomiting",
                "diarrhea",
                "nausea",
                "stomach pain",
                "symptoms started 24 hours after exposure",
            ],
        ),
        "expected_source": "Norovirus Stomach Bug.txt",
        "required_answer_groups": [
            ["norovirus"],
            ["vomiting", "vomit"],
            ["diarrhea", "diarrhoea"],
            [
                "drink",
                "oral rehydration",
                "fluid intake",
                "replace lost fluids",
                "replace fluids",
            ],
        ],
        "forbidden_answer_terms": [
            "norovirus is caused by influenza",
            "antibiotics cure norovirus",
            "norovirus is a bacterial infection",
        ],
    },
    {
        "name": "ankle_sprain_price_care",
        "summary": _summary(
            reason_for_visit="ankle injury with swelling and bruising",
            symptoms=[
                "ankle pain",
                "swelling",
                "bruising",
                "injury happened yesterday",
            ],
            symptom_location="ankle",
        ),
        "expected_source": "Sprains and strains.txt",
        "required_answer_groups": [
            ["sprain", "strain"],
            [
                "protect",
                "support the ankle",
                "support the injury",
                "ankle support",
            ],
            ["rest", "avoid exercise", "avoid putting weight"],
            ["ice", "cold pack", "cold compress"],
            ["compression", "compress", "bandage"],
            [
                "elevate",
                "elevation",
                "elevating",
                "keep it raised",
                "keep the ankle raised",
                "raise the injured area",
            ],
        ],
        "forbidden_answer_terms": [
            "heat packs are recommended during the first two days",
            "massage is recommended immediately after the injury",
        ],
    },
    {
        "name": "child_ear_infection",
        "summary": _summary(
            reason_for_visit="child with ear pain and fever",
            symptoms=[
                "ear pain",
                "fever",
                "symptoms have lasted 4 days",
            ],
        ),
        "expected_source": "Ear Infection.txt",
        "required_answer_groups": [
            ["ear infection", "otitis media"],
            ["ear pain", "earache", "ear ache"],
            [
                "doctor",
                "gp",
                "healthcare provider",
                "health care provider",
                "clinician",
                "medical evaluation",
                "medical assessment",
            ],
        ],
        "forbidden_answer_terms": [
            "antibiotics are always required for ear infections",
            "ear infections never need antibiotics",
        ],
    },
    {
        "name": "lyme_disease_after_tick_bite",
        "summary": _summary(
            reason_for_visit="expanding rash after a tick bite",
            symptoms=[
                "tick bite about one week ago",
                "rash has gradually expanded",
                "fatigue",
            ],
        ),
        "expected_source": "Lyme Disease.txt",
        "required_answer_groups": [
            ["lyme"],
            ["tick"],
            [
                "expanding",
                "expanded",
                "expands",
                "enlarging",
                "enlarges",
                "increasing in size",
                "gets bigger",
                "getting bigger",
                "grows",
                "growing",
            ],
        ],
        "forbidden_answer_terms": [
            "the rash always has a bullseye appearance",
            "every lyme rash has a bullseye",
            "the rash proves you have lyme disease",
        ],
    },
    {
        "name": "pregnancy_chickenpox_risk",
        "summary": _summary(
            reason_for_visit="pregnant person exposed to chickenpox",
            symptoms=[
                "exposed to chickenpox yesterday",
                "no symptoms yet",
            ],
            medical_history={
                "status": "confirmed",
                "items": [
                    "pregnant",
                    "no evidence of immunity to chickenpox",
                ],
            },
        ),
        "expected_source": "Chickenpox (Varicella).txt",
        "required_answer_groups": [
            ["chickenpox", "varicella"],
            ["pregnant", "pregnancy"],
            [
                "high risk",
                "higher risk",
                "increased risk",
                "at risk",
                "risk of severe",
                "risk for severe",
                "more severe",
                "more serious",
            ],
        ],
        "forbidden_answer_terms": [
            "there is no risk during pregnancy",
            "pregnant women cannot develop severe chickenpox",
        ],
    },
    {
        "name": "heartburn_after_meals",
        "summary": _summary(
            reason_for_visit="burning feeling in the middle of the chest",
            symptoms=[
                "heartburn",
                "sour taste in the mouth",
                "symptoms get worse after eating",
                "symptoms get worse when lying down",
            ],
        ),
        "expected_source": "Heartburn and acid reflux.txt",
        "required_answer_groups": [
            ["heartburn", "acid reflux"],
            ["sour taste", "acid taste", "acidic taste"],
            ["after eating", "after meals", "following meals"],
            ["lying down", "lie down", "lying flat"],
        ],
        "forbidden_answer_terms": [
            "eating immediately before bed is recommended",
            "extra pillows are recommended",
            "antacids permanently cure acid reflux",
        ],
    },
]


def _normalise(text: str) -> str:
    return " ".join(text.lower().split())


def _node_file_name(node) -> str | None:
    metadata = getattr(node.node, "metadata", {}) or {}

    file_name = metadata.get("file_name")
    if file_name:
        return str(file_name)

    file_path = metadata.get("file_path")
    if file_path:
        return Path(str(file_path)).name

    return None


def _retrieve(index, query: str) -> list[dict[str, Any]]:
    retriever = index.as_retriever(similarity_top_k=TOP_K)
    raw_nodes = retriever.retrieve(query)

    processor = SimilarityPostprocessor(
        similarity_cutoff=SIMILARITY_CUTOFF
    )
    filtered_nodes = processor.postprocess_nodes(
        raw_nodes,
        query_str=query,
    )

    return [
        {
            "score": node.score,
            "file_name": _node_file_name(node),
            "text_preview": node.node.get_text()[:250],
        }
        for node in filtered_nodes
    ]


def _check_source(
    case: dict[str, Any],
    retrieved: list[dict[str, Any]],
) -> tuple[bool, str]:
    expected = _normalise(case["expected_source"])

    for item in retrieved:
        file_name = _normalise(item.get("file_name") or "")
        if expected == file_name or expected in file_name:
            return True, f"expected source retrieved: {case['expected_source']}"

    # Fallback for indexes where source filenames were not saved as metadata.
    expected_title = _normalise(Path(case["expected_source"]).stem)
    retrieved_text = _normalise(
        " ".join(item["text_preview"] for item in retrieved)
    )
    if expected_title in retrieved_text:
        return True, f"source title found in retrieved text: {expected_title}"

    names = [item.get("file_name") or "unknown" for item in retrieved]
    return False, f"expected {case['expected_source']}; retrieved {names}"


def _check_answer(
    case: dict[str, Any],
    answer: str,
) -> tuple[bool, str]:
    normalised_answer = _normalise(answer)

    missing_groups = []
    for group in case["required_answer_groups"]:
        alternatives = [_normalise(term) for term in group]
        if not any(term in normalised_answer for term in alternatives):
            missing_groups.append(" / ".join(group))

    forbidden_hits = [
        term
        for term in case["forbidden_answer_terms"]
        if _normalise(term) in normalised_answer
    ]

    problems = []
    if missing_groups:
        problems.append(f"missing required answer content: {missing_groups}")
    if forbidden_hits:
        problems.append(f"forbidden claims found: {forbidden_hits}")

    if problems:
        return False, "; ".join(problems)

    return True, "required answer content found; no forbidden claims found"


def _evaluate_case(index, case: dict[str, Any]) -> dict[str, Any]:
    query = build_query_from_consultation_summary(case["summary"])
    retrieved = _retrieve(index, query)
    source_pass, source_detail = _check_source(case, retrieved)

    rag_result = ask_structured(index, query)
    parse_pass = not rag_result.get("parse_error", False)

    answer = str(rag_result.get("answer") or "")
    answer_pass, answer_detail = _check_answer(case, answer)

    return {
        "name": case["name"],
        "query": query,
        "retrieved": retrieved,
        "answer": answer,
        "checks": {
            "source": {
                "pass": source_pass,
                "detail": source_detail,
            },
            "parse": {
                "pass": parse_pass,
                "detail": (
                    "valid structured result"
                    if parse_pass
                    else "RAG response could not be parsed"
                ),
            },
            "answer": {
                "pass": answer_pass,
                "detail": answer_detail,
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case",
        help="Run one case by name.",
    )
    args = parser.parse_args()

    cases = CASES
    if args.case:
        cases = [case for case in CASES if case["name"] == args.case]
        if not cases:
            available = ", ".join(case["name"] for case in CASES)
            raise SystemExit(
                f"Unknown case '{args.case}'. Available cases: {available}"
            )

    print("Loading existing RAG index...")
    index = load_index()

    failed_cases = 0

    for case in cases:
        result = _evaluate_case(index, case)
        checks = result["checks"]
        case_pass = all(item["pass"] for item in checks.values())

        print(f"\n{'PASS' if case_pass else 'FAIL'}: {result['name']}")
        print(f"Query: {result['query']}")

        print("Retrieved sources:")
        if not result["retrieved"]:
            print("  (none)")
        for item in result["retrieved"]:
            score = item["score"]
            score_text = f"{score:.4f}" if score is not None else "None"
            print(f"  {item['file_name'] or 'unknown'} (score={score_text})")

        print("Checks:")
        for check_name, check in checks.items():
            status = "PASS" if check["pass"] else "FAIL"
            print(f"  {status} {check_name}: {check['detail']}")

        print(f"Answer: {result['answer']}")

        if not case_pass:
            failed_cases += 1

    print(f"\nRESULT: {len(cases) - failed_cases}/{len(cases)} cases passed")

    if failed_cases:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
"""Standalone evaluation runner for the current GP Support RAG pipeline.

Examples:
    python -m tests.rag_evaluation --retrieval-only
    python -m tests.rag_evaluation
    python -m tests.rag_evaluation --case persistent_cough_4_weeks

The evaluator NEVER rebuilds the vector index and does not write application
data. It loads the existing index, runs fixed cases, prints diagnostics, and
writes a JSON report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from llama_index.core.postprocessor import SimilarityPostprocessor

from app.services.knowledge_rag import (
    ask_structured,
    build_query_from_consultation_summary,
    load_index,
)
from tests.rag_cases import RAG_CASES


# These mirror the current values in knowledge_rag.py.
# They are diagnostic settings only; end-to-end evaluation still calls
# ask_structured(), which uses the application's real implementation.
EVAL_TOP_K = 2
EVAL_SIMILARITY_CUTOFF = 0.67


def _normalise(value: str) -> str:
    return " ".join(value.lower().split())


def _node_file_name(node) -> str | None:
    metadata = getattr(node.node, "metadata", {}) or {}

    file_name = metadata.get("file_name")
    if file_name:
        return str(file_name)

    file_path = metadata.get("file_path")
    if file_path:
        return Path(str(file_path)).name

    return None


def inspect_retrieval(index, query: str) -> dict[str, Any]:
    """Run retrieval only so we can inspect candidates and similarity scores."""
    retriever = index.as_retriever(similarity_top_k=EVAL_TOP_K)
    raw_nodes = retriever.retrieve(query)

    processor = SimilarityPostprocessor(
        similarity_cutoff=EVAL_SIMILARITY_CUTOFF
    )
    filtered_nodes = processor.postprocess_nodes(
        raw_nodes,
        query_str=query,
    )

    def serialise(nodes):
        output = []
        for node in nodes:
            output.append(
                {
                    "score": node.score,
                    "file_name": _node_file_name(node),
                    "text_preview": node.node.get_text()[:300],
                }
            )
        return output

    return {
        "raw_candidates": serialise(raw_nodes),
        "filtered_candidates": serialise(filtered_nodes),
    }


def _source_check(case: dict, retrieval: dict) -> tuple[bool, str]:
    filtered = retrieval["filtered_candidates"]
    expected_files = case["expected_source_files"]

    if case["expect_no_match"]:
        passed = len(filtered) == 0
        return passed, (
            "no filtered source retrieved"
            if passed
            else "unexpected source passed similarity cutoff"
        )

    if not expected_files:
        return True, "no source assertion"

    retrieved_names = {
        _normalise(item["file_name"])
        for item in filtered
        if item.get("file_name")
    }

    for expected in expected_files:
        expected_norm = _normalise(expected)

        if any(
            expected_norm == actual or expected_norm in actual
            for actual in retrieved_names
        ):
            return True, f"expected source retrieved: {expected}"

    # Fallback for indexes that did not persist SimpleDirectoryReader metadata:
    joined_text = _normalise(
        " ".join(item["text_preview"] for item in filtered)
    )
    for expected in expected_files:
        title = Path(expected).stem
        if _normalise(title) in joined_text:
            return True, f"expected source title found in retrieved text: {title}"

    return False, (
        f"expected one of {expected_files}; "
        f"retrieved {[item.get('file_name') for item in filtered]}"
    )


def _answer_content_check(case: dict, rag_result: dict) -> tuple[bool, str]:
    answer = _normalise(str(rag_result.get("answer") or ""))

    for term in case.get("forbidden_answer_terms_any", []):
        if _normalise(term) in answer:
            return False, f"forbidden answer wording detected: '{term}'"

    return True, "no forbidden answer wording detected"


def evaluate_case(index, case: dict, retrieval_only: bool) -> dict[str, Any]:
    query = build_query_from_consultation_summary(case["summary"])
    retrieval = inspect_retrieval(index, query)

    source_pass, source_detail = _source_check(case, retrieval)

    result: dict[str, Any] = {
        "name": case["name"],
        "purpose": case["purpose"],
        "query": query,
        "retrieval": retrieval,
        "checks": {
            "source": {
                "pass": source_pass,
                "detail": source_detail,
            }
        },
    }

    if retrieval_only:
        result["pass"] = source_pass
        return result

    print("\n")
    print("#" * 72)
    print(f"RUNNING END-TO-END CASE: {case['name']}")
    print("#" * 72)
    print(f"Query: {query}")
    print()

    rag_result = ask_structured(index, query)

    answer_pass, answer_detail = _answer_content_check(case, rag_result)

    no_match_e2e_pass = True
    no_match_detail = "not a negative-control case"

    if case["expect_no_match"]:
        no_match_e2e_pass = not rag_result.get("sources")

        no_match_detail = (
            "RAG correctly returned no grounded source"
            if no_match_e2e_pass
            else "RAG returned grounded content for an unsupported case"
        )

    result["rag_result"] = rag_result
    result["checks"].update(
        {
            "parse": {
                "pass": parse_pass,
                "detail": (
                    "valid structured result"
                    if parse_pass
                    else "RAG response could not be parsed"
                ),
            },
            "answer_content": {
                "pass": answer_pass,
                "detail": answer_detail,
            },
            "negative_control": {
                "pass": no_match_e2e_pass,
                "detail": no_match_detail,
            },
        }
    )

    result["pass"] = all(
        check["pass"] for check in result["checks"].values()
    )
    return result


def _print_case(result: dict, retrieval_only: bool) -> None:
    status = "PASS" if result["pass"] else "FAIL"
    print(f"\n{'=' * 72}")
    print(f"{status}: {result['name']}")
    print(f"Purpose: {result['purpose']}")
    print(f"Query: {result['query']}")

    print("\nRetrieved candidates:")
    candidates = result["retrieval"]["raw_candidates"]
    if not candidates:
        print("  (none)")
    for candidate in candidates:
        score = candidate["score"]
        score_text = f"{score:.4f}" if score is not None else "None"
        print(
            f"  score={score_text} | "
            f"file={candidate['file_name'] or 'unknown'}"
        )

    print("\nChecks:")
    for name, check in result["checks"].items():
        marker = "PASS" if check["pass"] else "FAIL"
        print(f"  {marker:4} {name}: {check['detail']}")

    if not retrieval_only and "rag_result" in result:
        rag = result["rag_result"]
        print("\nRAG output:")
        print(f"  confidence: {rag.get('confidence')}")
        print(f"  answer: {rag.get('answer')}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Test vector retrieval without calling Bedrock synthesis.",
    )
    parser.add_argument(
        "--case",
        help="Run only one named case.",
    )
    parser.add_argument(
        "--output",
        default="rag_evaluation_results.json",
        help="JSON report path.",
    )
    args = parser.parse_args()

    selected_cases = RAG_CASES

    if args.case:
        selected_cases = [
            case for case in RAG_CASES
            if case["name"] == args.case
        ]
        if not selected_cases:
            available = ", ".join(case["name"] for case in RAG_CASES)
            raise SystemExit(
                f"Unknown case '{args.case}'. Available cases: {available}"
            )

    print("Loading existing RAG index...")
    index = load_index()

    results = []

    for case in selected_cases:
        result = evaluate_case(
            index,
            case,
            retrieval_only=args.retrieval_only,
        )
        results.append(result)
        _print_case(result, args.retrieval_only)

    passed = sum(1 for result in results if result["pass"])
    total = len(results)

    report = {
        "mode": (
            "retrieval_only"
            if args.retrieval_only
            else "end_to_end"
        ),
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "results": results,
    }

    output_path = Path(args.output)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\n{'=' * 72}")
    print(f"RESULT: {passed}/{total} cases passed")
    print(f"Report written to: {output_path}")


if __name__ == "__main__":
    main()

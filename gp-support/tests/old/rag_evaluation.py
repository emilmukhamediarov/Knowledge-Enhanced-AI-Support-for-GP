"""Evaluate the production RAG path; never rebuild or update the vector store.

Run from gp-support: python -m tests.rag_evaluation --help
Only the CLI loads model/database dependencies. Checks can be tested offline.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from typing import Any

from tests.rag_cases import RAG_CASES

EVAL_TOP_K = 2
EVAL_SIMILARITY_CUTOFF = 0.67
NO_MATCH_ANSWER = (
    "The knowledge base does not contain verified clinical guidance for this presentation."
)


def _normalise(value: str) -> str:
    return " ".join(value.casefold().split())


def _contains(text: str, term: str) -> bool:
    # Avoid matching e.g. 'fluid' in 'fluidless'; inflections belong in alternatives.
    return bool(re.search(r"(?<!\w)" + re.escape(_normalise(term)) + r"(?!\w)", text))


def _check(passed: bool, detail: str) -> dict:
    return {"pass": bool(passed), "detail": detail}


def _serialise_node(node) -> dict:
    metadata = getattr(node.node, "metadata", {}) or {}
    name = metadata.get("file_name") or metadata.get("file_path")
    return {
        "file_name": str(name).replace("\\", "/").rsplit("/", 1)[-1] if name else None,
        "node_id": getattr(node.node, "node_id", None),
        "score": float(node.score) if node.score is not None else None,
        "text": node.node.get_text(),
    }


class RecordingIndex:
    """Observe the real retrieval call without issuing a second query."""
    def __init__(self, index):
        self.index = index
        self.calls = []

    def as_retriever(self, **kwargs):
        underlying = self.index.as_retriever(**kwargs)
        owner = self

        class RecordingRetriever:
            def retrieve(self, query):
                nodes = underlying.retrieve(query)
                owner.calls.append({
                    "settings": kwargs,
                    "nodes": [_serialise_node(node) for node in nodes],
                })
                return nodes

        return RecordingRetriever()


def _source_check(case: dict, candidates: list[dict]) -> dict:
    names = {n["file_name"] for n in candidates if n.get("file_name")}
    expected = set(case["expected_source_files"])
    matched = expected & names
    passed = bool(matched) if case.get("source_match_mode", "any") == "any" else expected <= names
    return _check(passed, f"expected={sorted(expected)}; retrieved={sorted(names)}")


def _answer_content_check(case: dict, result: dict) -> dict:
    raw = result.get("answer")
    if not isinstance(raw, str) or not raw.strip():
        return _check(False, "answer must be a non-empty string")
    answer = _normalise(raw)
    problems = []
    for group in case.get("required_answer_groups", []):
        if not any(_contains(answer, term) for term in group):
            problems.append("missing: " + " / ".join(group))
    for term in case.get("forbidden_answer_terms_any", []):
        if _contains(answer, term):
            problems.append("forbidden wording: " + term)
    for pattern in case.get("forbidden_answer_patterns", []):
        if re.search(pattern, answer):
            problems.append("forbidden pattern: " + pattern)
    return _check(not problems, "; ".join(problems) or "lexical checks passed; semantic review still required")


def _query_context_check(case: dict, query: str) -> dict:
    """Check patient fields survive query construction without changing their meaning."""
    text = _normalise(query)
    missing = [t for t in case.get("required_query_terms", []) if not _contains(text, t)]
    forbidden = [t for t in case.get("forbidden_query_terms", []) if _contains(text, t)]
    return _check(not missing and not forbidden,
                  f"missing patient context: {missing}; unexpected patient context: {forbidden}")


def _grounding_sources(result: dict, raw_nodes: list[dict]) -> tuple[list[dict], bool]:
    """Keep exactly the source texts returned by production, with traceable metadata.

    Production exposes text rather than IDs. Ambiguous/unmatched text is preserved
    but fails provenance rather than guessing a document name.
    """
    sources = []
    traceable = True
    for text in result.get("sources", []):
        matches = [n for n in raw_nodes if n["text"] == text]
        identities = {(n["file_name"], n["node_id"]) for n in matches}
        if len(identities) == 1 and matches[0]["file_name"]:
            sources.append(dict(matches[0]))
        else:
            traceable = False
            sources.append({"file_name": None, "node_id": None, "score": None, "text": text})
    return sources, traceable


def evaluate_case(index, case: dict, retrieval_only: bool, runtime=None) -> dict[str, Any]:
    if runtime is None:
        from app.services import knowledge_rag as runtime
    result = {
        "name": case["name"], "category": case["category"],
        "purpose": case["purpose"], "summary": deepcopy(case["summary"]),
        "expected_source_files": case["expected_source_files"],
        "expect_no_match": case["expect_no_match"],
        "expect_insufficient_detail": case.get("expect_insufficient_detail", False),
        "checks": {},
    }
    started = time.perf_counter()
    recorder = RecordingIndex(index)
    try:
        query = runtime.build_query_from_consultation_summary(case["summary"])
        result["query"] = query
        if case.get("required_query_terms") or case.get("forbidden_query_terms"):
            result["checks"]["query_context"] = _query_context_check(case, query)
        if retrieval_only:
            from llama_index.core.postprocessor import SimilarityPostprocessor
            nodes = recorder.as_retriever(similarity_top_k=EVAL_TOP_K).retrieve(query)
            filtered = SimilarityPostprocessor(
                similarity_cutoff=EVAL_SIMILARITY_CUTOFF
            ).postprocess_nodes(nodes, query_str=query)
            candidates = [_serialise_node(n) for n in filtered]
            result["filtered_candidates"] = candidates
            if case["expect_no_match"]:
                result["checks"]["negative_retrieval"] = _check(not candidates, "no source should pass the cutoff")
            else:
                result["checks"]["source"] = _source_check(case, candidates)
        else:
            rag = runtime.ask_structured(recorder, query)
            result["rag_result"] = rag
            contract_ok = (
                isinstance(rag, dict)
                and rag.get("parse_error") is False
                and isinstance(rag.get("answer"), str)
                and bool(rag["answer"].strip())
                and isinstance(rag.get("sources"), list)
                and all(isinstance(s, str) for s in rag["sources"])
                and isinstance(rag.get("link"), list)
                and all(isinstance(s, str) for s in rag["link"])
            )
            result["checks"]["response_contract"] = _check(contract_ok, "non-empty answer, source/link lists, no parse error")
            raw_nodes = [n for call in recorder.calls for n in call["nodes"]]
            if contract_ok:
                sources, traceable = _grounding_sources(rag, raw_nodes)
                result["grounding_sources"] = sources
                result["checks"]["source_provenance"] = _check(traceable, "returned source texts map unambiguously to actual retrieved nodes")
                if case["expect_no_match"]:
                    # Production's no-match branch has a fixed response. Requiring exact
                    # normalised text also rejects a refusal followed by invented advice.
                    refused = (
                        not rag["sources"] and not rag["link"]
                        and _normalise(rag["answer"]) == _normalise(NO_MATCH_ANSWER)
                    )
                    result["checks"]["no_match"] = _check(refused, "empty sources/links and the complete production abstention response")
                else:
                    result["checks"]["source"] = _source_check(case, sources)
                    result["checks"]["answer_content"] = _answer_content_check(case, rag)
                    if case.get("expect_insufficient_detail"):
                        result["checks"]["insufficient_detail"] = _answer_content_check(case, rag)
        result["automatic_pass"] = all(c["pass"] for c in result["checks"].values())
    except Exception as exc:
        # Preserve other cases and diagnostics. Errors remain failures in denominators.
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
        result["automatic_pass"] = False
    result["retrieval_calls"] = recorder.calls
    result["latency_seconds"] = round(time.perf_counter() - started, 3)
    return result


def _metric(results: list[dict], check: str) -> dict:
    passed = sum(r.get("checks", {}).get(check, {}).get("pass") is True for r in results)
    return {"passed": passed, "total": len(results),
            "rate": passed / len(results) if results else None}


def aggregate(results: list[dict], retrieval_only: bool) -> dict:
    positive = [r for r in results if not r["expect_no_match"]]
    negative = [r for r in results if r["expect_no_match"]]
    detail = [r for r in results if r.get("expect_insufficient_detail")]
    return {
        "source_hit_rate": _metric(positive, "source"),
        "answer_content_pass_rate": _metric([] if retrieval_only else positive, "answer_content"),
        "no_match_handling_pass_rate": _metric([] if retrieval_only else negative, "no_match"),
        "negative_retrieval_pass_rate": _metric(negative if retrieval_only else [], "negative_retrieval"),
        "insufficient_detail_pass_rate": _metric([] if retrieval_only else detail, "insufficient_detail"),
        "errors": sum("error" in r for r in results),
        "per_category": {
            category: {"automatic_passed": sum(r["automatic_pass"] for r in results if r["category"] == category), "runs": count}
            for category, count in sorted(Counter(r["category"] for r in results).items())
        },
    }


def validate_cases(cases: list[dict], knowledge_dir: Path) -> None:
    names = [c["name"] for c in cases]
    if len(names) != len(set(names)):
        raise ValueError("duplicate case names")
    for case in cases:
        if case.get("source_match_mode", "any") not in {"any", "all"}:
            raise ValueError(f"invalid source_match_mode: {case['name']}")
        if bool(case["expected_source_files"]) == case["expect_no_match"]:
            raise ValueError(f"inconsistent expected sources: {case['name']}")
        if not case["expect_no_match"] and not case.get("required_answer_groups"):
            raise ValueError(f"missing answer requirements: {case['name']}")
        if not case.get("manual_checks") or not case.get("category"):
            raise ValueError(f"missing review criteria/category: {case['name']}")
        for group in case.get("required_answer_groups", []):
            if not group or any(not isinstance(t, str) or not t.strip() for t in group):
                raise ValueError(f"invalid answer group: {case['name']}")
        for pattern in case.get("forbidden_answer_patterns", []):
            re.compile(pattern)
        if case.get("comparison_case") and case["comparison_case"] not in names:
            raise ValueError(f"missing comparison case: {case['name']}")
        for reference in case.get("reference_evidence", []):
            name, excerpt = reference["file_name"], reference["excerpt"]
            if name not in case["expected_source_files"] or not excerpt.strip():
                raise ValueError(f"invalid reference evidence: {case['name']}")
            if excerpt not in (knowledge_dir / name).read_text(encoding="utf-8"):
                raise ValueError(f"reference excerpt no longer in {name}: {case['name']}")
        for name in case["expected_source_files"]:
            if Path(name).name != name or not (knowledge_dir / name).is_file():
                raise ValueError(f"missing/invalid local source: {name}")


def _fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument("--case", action="append", help="Case name; repeat to select several")
    parser.add_argument("--repeat", type=int, default=1, help="Independent runs per case (default: 1)")
    parser.add_argument("--list-cases", action="store_true", help="List/validate cases without loading models")
    parser.add_argument("--output", help="Optional JSON report path; omitted means terminal only")
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    root = Path(__file__).resolve().parents[1]
    knowledge_dir = root / "app/knowledge_base"
    validate_cases(RAG_CASES, knowledge_dir)
    cases = RAG_CASES
    if args.case:
        missing = set(args.case) - {c["name"] for c in cases}
        if missing:
            parser.error(f"unknown cases: {sorted(missing)}")
        cases = [c for c in cases if c["name"] in args.case]
    if args.list_cases:
        for case in cases:
            print(f"{case['name']} [{case['category']}]")
        print(f"{len(cases)} cases; local source files verified. Database index not checked.")
        return
    # Credentials/model dependencies are deliberately not imported for offline operations.
    from app.services import knowledge_rag as runtime
    index = runtime.load_index()
    report = {
        "schema_version": 2,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "retrieval_only" if args.retrieval_only else "end_to_end",
        "repeat": args.repeat,
        "retrieval_only_settings": {"top_k": EVAL_TOP_K, "similarity_cutoff": EVAL_SIMILARITY_CUTOFF},
        "production_code_sha256": _fingerprint(root / "app/services/knowledge_rag.py"),
        "case_file_sha256": _fingerprint(Path(__file__).with_name("rag_cases.py")),
        "local_knowledge_sha256": {p.name: _fingerprint(p) for p in sorted(knowledge_dir.glob("*.txt"))},
        "limitations": [
            "Lexical answer checks are not clinical accuracy or semantic correctness.",
            "Local document hashes do not verify database index freshness.",
            "Repeated runs are correlated observations, not independent patient samples.",
            "Source metadata is recovered by exact text matching; ambiguous matches fail provenance.",
            "Urgency advice is excluded by the production prompt and is not scored.",
        ],
        "results": [],
    }
    output = Path(args.output) if args.output else None
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
    for case in cases:
        for run in range(1, args.repeat + 1):
            result = evaluate_case(index, case, args.retrieval_only, runtime)
            result["run"] = run
            report["results"].append(result)
            report["metrics"] = aggregate(report["results"], args.retrieval_only)
            # Save checkpoints only when the caller explicitly requests a report.
            if output is not None:
                temporary = output.with_suffix(output.suffix + ".tmp")
                temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
                temporary.replace(output)
            print(f"{'PASS' if result['automatic_pass'] else 'FAIL'} {case['name']} (run {run})")
            print("Patient:", json.dumps(result["summary"], ensure_ascii=False))
            print("Query:", result.get("query", "(unavailable)"))
            rag = result.get("rag_result")
            if isinstance(rag, dict):
                print("Answer:", rag.get("answer", "(unavailable)"))
            evidence = result.get("grounding_sources", result.get("filtered_candidates", []))
            print("Evidence:")
            if not evidence:
                print("  (none)")
            for number, source in enumerate(evidence, 1):
                print(f"  [{number}] {source.get('file_name') or 'unknown'} (score={source.get('score')})")
                print(source["text"])
            for name, check in result["checks"].items():
                print(f"  {name}: {check['pass']} — {check['detail']}")
            if "error" in result:
                print(f"  error: {result['error']}")
    print(json.dumps(report["metrics"], indent=2))
    if output is not None:
        print(f"Report: {output}")
    if any(not r["automatic_pass"] for r in report["results"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

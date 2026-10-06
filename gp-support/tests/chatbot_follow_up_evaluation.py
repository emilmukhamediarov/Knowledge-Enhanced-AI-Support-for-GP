"""Evaluate dynamic follow-up behaviour for the Bitwise student report.

Put these three files in tests/. Run from the backend root:
  python -m tests.chatbot_follow_up_evaluation --output-dir C:/temp/bitwise-chat-eval
  python -m tests.chatbot_follow_up_evaluation --regrade PATH_TO_OLD_JSON --output-dir C:/temp/bitwise-chat-eval

Default: ten calls (one per case), production chat token limit, no model-based
judge, extraction, summarisation, embeddings or live RAG retrieval. Regrading
uses saved delivered replies only, with zero model calls. Offline unit tests
also use zero model calls. Use --case ID to limit calls, or --repeat 3 when
repeated evidence is wanted. Do not present a single run as a reliability claim.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

try:
    from .chatbot_follow_up_cases import CASES, BACKGROUND
except ImportError:  # Also supports direct execution of this file.
    from chatbot_follow_up_cases import CASES, BACKGROUND

BACKEND = Path(__file__).resolve().parents[1]
EVALUATOR_VERSION = "2.0"
COMPLETION = "pre-consultation information is complete"
SCOPE = (
    "Controlled English next-response evaluation using supplied fictional state/history; "
    "RAG guidance is injected. Not an endpoint, state-extraction, live-retrieval, "
    "multilingual, clinical-accuracy or full-conversation evaluation."
)
METRIC_NOTES = {
    "nonempty_reply": "A non-empty delivered reply was produced.",
    "completion_contract": "Completion phrase with no question when complete; no completion phrase otherwise.",
    "one_question": "Exactly one question mark in an intake reply (format proxy, not semantic proof).",
    "background_focus": "The question mentions at most one of history, medication and allergies.",
    "acceptable_next_question": "Question text matches at least one pre-specified acceptable topic pattern.",
    "question_constraints": "Question text avoids specified repeated known fields or inappropriate topic switches; acknowledgements allowed.",
    "forbidden_content": "Delivered reply avoids the case's specified assumption/prohibited-wording patterns.",
    "no_treatment_instruction": "No treatment-instruction pattern detected; a limited role-boundary screen, not a safety score.",
    "rag_follow_up_compliance": "Specified RAG clarification/non-repetition constraints hold in this controlled case.",
    "all_applicable_checks": "All applicable automatic rules pass; not general chatbot accuracy.",
}


def normalise(text):
    return " ".join((text or "").casefold().split())


def matches_any(text, patterns):
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def question_text(text):
    # Check the question, not a preceding acknowledgement of a known answer.
    return " ".join(part.strip() for part in re.findall(r"[^.!?\n]*\?", text))


def question_count(text):
    return text.count("?")


def contains_unsafe_advice(text):
    # Name retained for compatibility. This is only a limited pattern screen.
    patterns = (
        r"\byou (?:should|need to|must|can) (?:take|use|drink|try)\b",
        r"\btry taking\b",
        r"\bi recommend (?:taking|using|drinking)\b",
        r"\btake \d+(?:\.\d+)?\s*(?:mg|mcg|g|ml)\b",
        r"(?:^|[.!]\s+)\s*(?:take|use|try)\s+(?:some\s+)?(?:ibuprofen|paracetamol|aspirin|antibiotics?)\b",
        r"(?:^|[.!]\s+)\s*(?:stay hydrated|drink more water|monitor your symptoms)\b",
    )
    return matches_any(text, patterns)


def applicable_checks(case):
    checks = ["nonempty_reply", "completion_contract"]
    if not case["expect_complete"]:
        checks.extend(["one_question", "background_focus"])
    if case["expected_patterns"]:
        checks.append("acceptable_next_question")
    if case.get("forbidden_question_patterns"):
        checks.append("question_constraints")
    if case["forbidden_patterns"]:
        checks.append("forbidden_content")
    if case["check_advice"]:
        checks.append("no_treatment_instruction")
    if case["category"] == "rag_follow_up":
        checks.append("rag_follow_up_compliance")
    return checks


def grade(case, reply):
    reply = reply or ""
    text = normalise(reply)
    questions = question_text(reply)
    checks = {name: False for name in applicable_checks(case)}
    checks["nonempty_reply"] = bool(text)
    complete = COMPLETION in text
    checks["completion_contract"] = (
        complete and question_count(reply) == 0 if case["expect_complete"] else not complete
    )
    if "one_question" in checks:
        checks["one_question"] = question_count(reply) == 1
    if "background_focus" in checks:
        groups = (BACKGROUND[:2], BACKGROUND[2:5], BACKGROUND[5:])
        checks["background_focus"] = sum(matches_any(questions, group) for group in groups) <= 1
    if "acceptable_next_question" in checks:
        checks["acceptable_next_question"] = matches_any(questions, case["expected_patterns"])
    if "question_constraints" in checks:
        checks["question_constraints"] = not matches_any(questions, case["forbidden_question_patterns"])
    if "forbidden_content" in checks:
        checks["forbidden_content"] = not matches_any(reply, case["forbidden_patterns"])
    if "no_treatment_instruction" in checks:
        checks["no_treatment_instruction"] = not contains_unsafe_advice(reply)
    if "rag_follow_up_compliance" in checks:
        # Stay strict on the requested clarification. Formatting is reported separately.
        checks["rag_follow_up_compliance"] = bool(text) and bool(questions) and all(
            checks.get(name, True) for name in (
                "completion_contract", "acceptable_next_question",
                "question_constraints", "forbidden_content",
            )
        )
    return checks


def build_messages(case, prompts):
    current_state = deepcopy(case["state"])
    if hasattr(prompts, "build_system_prompt"):
        system = prompts.build_system_prompt("English (en-US)", current_state)
    else:
        system = prompts.SYSTEM_PROMPT + (
            "\n\nCurrent structured consultation state (use this to avoid repetition):\n"
            + json.dumps(current_state, ensure_ascii=False)
        )
    messages = [{"role": "system", "content": system}]
    if case.get("rag_guidance"):
        messages.append({"role": "system", "content": (
            "Retrieved clinical context for FOLLOW-UP QUESTION SELECTION only:\n"
            + case["rag_guidance"]
            + "\nUse it only to decide whether a clarification is useful. "
              "Do not diagnose, provide treatment, or assume an unstated patient fact."
        )})
    messages.extend(deepcopy(case["history"]))
    return messages


def evaluate_case(case, chat_service, prompts, chat_rules):
    started = time.monotonic()
    row = {
        "id": case["id"], "category": case["category"],
        "requirement": case["requirement"], "state": deepcopy(case["state"]),
        "history": deepcopy(case["history"]), "rag_guidance": case.get("rag_guidance"),
        "raw_reply": None, "reply": None, "checks": {}, "error": None,
        "manual_review": {"status": "not_reviewed", "notes": ""},
    }
    try:
        reply = chat_service.chat_aws(build_messages(case, prompts))
        if not isinstance(reply, str):
            raise TypeError("Chat response must be text")
        row["raw_reply"] = reply
        if hasattr(chat_rules, "remove_medical_advice"):
            reply = chat_rules.remove_medical_advice(reply)
        if hasattr(chat_rules, "keep_one_question"):
            reply = chat_rules.keep_one_question(reply)
        row["reply"] = reply
        row["checks"] = grade(case, reply)
    except Exception as exc:
        row["error"] = type(exc).__name__
        row["checks"] = {name: False for name in applicable_checks(case)}
    row["seconds"] = round(time.monotonic() - started, 3)
    return row


def regrade_rows(saved, chosen):
    by_id = {case["id"]: case for case in chosen}
    rows = []
    for old in saved["cases"]:
        if old["id"] not in by_id:
            continue
        case = by_id[old["id"]]
        # Prevent silently applying new scenario definitions to different inputs.
        for key in ("state", "history", "rag_guidance"):
            if old.get(key) != case.get(key):
                raise ValueError(f"Saved inputs differ for {old['id']}: {key}")
        row = deepcopy(old)
        row["requirement"] = case["requirement"]
        row["previous_checks"] = deepcopy(old["checks"])
        row["checks"] = (grade(case, old.get("reply")) if not old.get("error") else
                         {name: False for name in applicable_checks(case)})
        # Old review decisions, if any, were made against different criteria.
        row["manual_review"] = {"status": "not_reviewed", "notes": ""}
        rows.append(row)
    if not rows:
        raise ValueError("No matching saved responses")
    return rows


def metrics(rows):
    result = {}
    for key in sorted({key for row in rows for key in row["checks"]}):
        values = [row["checks"][key] for row in rows if key in row["checks"]]
        result[key] = {"passed": sum(values), "total": len(values),
                       "rate": sum(values) / len(values) if values else None}
    values = [bool(row["checks"]) and not row.get("error") and all(row["checks"].values()) for row in rows]
    result["all_applicable_checks"] = {"passed": sum(values), "total": len(values),
                                       "rate": sum(values) / len(values) if values else None}
    return result


def markdown(report):
    lines = ["# Chatbot dynamic follow-up evaluation", "", report["scope"], "",
             f"Evaluator: {report['evaluator_version']}. Mode: {report['mode']}.",
             f"Responses: {len(report['cases'])}. Errors: {sum(bool(r.get('error')) for r in report['cases'])}.",
             f"Model calls this execution: {report['model_calls_attempted']}.", "",
             "Rates describe these fixed cases only. Regraded pilot outputs are not a new model run.",
             "Delivered replies are graded after advice filtering and question truncation; raw replies are retained when available.",
             "The supplied state/RAG prompt is a controlled harness, not verification of the complete endpoint pipeline.", "",
             "| Metric | Passed / applicable | Rate |", "|---|---:|---:|"]
    for key, value in report["metrics"].items():
        rate = "n/a" if value["rate"] is None else f"{value['rate']:.1%}"
        lines.append(f"| {key} | {value['passed']} / {value['total']} | {rate} |")
    lines += ["", "| Scenario | Requirement | Passed / runs |", "|---|---|---:|"]
    for case_id in dict.fromkeys(row["id"] for row in report["cases"]):
        rows = [row for row in report["cases"] if row["id"] == case_id]
        passed = sum(not row.get("error") and all(row["checks"].values()) for row in rows)
        lines.append(f"| {case_id} | {rows[0]['requirement']} | {passed} / {len(rows)} |")
    lines += ["", "## Metric definitions", ""]
    lines += [f"- **{key}**: {METRIC_NOTES[key]}" for key in report["metrics"]]
    lines += ["", "## Limitations", "",
              "Ten fictional English scenarios provide a small requirements-based sample. Repeats are not independent patient cases.",
              "Patterns can miss paraphrases, assumptions and instructions. Review failed or ambiguous replies before interpreting scores.",
              "One question mark may still contain multiple requests; background_focus screens only the three named background fields.",
              "Fixed RAG context tests compliance with supplied guidance; it does not establish a causal improvement over a no-RAG baseline.",
              "Role-boundary results are limited wording screens. No clinical correctness or comprehensive safety claim is made."]
    by_id = {case["id"]: case for case in CASES}
    for row in report["cases"]:
        failed = ", ".join(key for key, passed in row["checks"].items() if not passed) or "None"
        lines += ["", f"## {row['id']} — run {row.get('repeat', 1)}", "",
                  f"Failed checks: {failed}. Error: {row.get('error') or 'None'}.", "",
                  "**Delivered reply**", "", row.get("reply") or "(unavailable)"]
        if row.get("raw_reply") is not None and row["raw_reply"] != row.get("reply"):
            lines += ["", "**Raw reply before filters**", "", row["raw_reply"]]
        lines += ["", "**Manual review prompts**", ""]
        lines += ["- " + note for note in by_id[row["id"]]["manual_review"]]
        lines += ["- Does the actual question meet the stated requirement, including alternative wording?"]
    return "\n".join(lines) + "\n"


def file_hash(path):
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", default=[], help="Scenario ID; may be repeated")
    parser.add_argument("--repeat", type=int, default=1, help="Live runs per case (default 1)")
    parser.add_argument("--regrade", type=Path, help="Regrade saved JSON; zero model calls")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    unknown = set(args.case) - {case["id"] for case in CASES}
    if unknown or args.repeat < 1:
        parser.error(f"Unknown cases {sorted(unknown)} or invalid repeat count")
    if args.regrade and args.repeat != 1:
        parser.error("--repeat applies to live runs only; regrading preserves saved runs")
    chosen = [case for case in CASES if not args.case or case["id"] in args.case]
    folder = args.output_dir.expanduser().resolve()
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report = {
        "created_utc": stamp, "evaluator_version": EVALUATOR_VERSION,
        "mode": "regrade" if args.regrade else "live", "scope": SCOPE,
        "cases_sha256": file_hash(Path(__file__).with_name("chatbot_follow_up_cases.py")),
        "evaluator_sha256": file_hash(__file__), "model_calls_attempted": 0,
        "cases": [], "metrics": {},
    }
    if args.regrade:
        try:
            saved = json.loads(args.regrade.read_text(encoding="utf-8"))
            report["cases"] = regrade_rows(saved, chosen)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            parser.error(f"Cannot regrade: {exc}")
        report["source_report"] = str(args.regrade.resolve())
        report["source_created_utc"] = saved.get("created_utc")
        report["source_report_sha256"] = file_hash(args.regrade)
    else:
        # These imports are deliberately lazy: unit tests/regrade need no app, keys or AWS.
        from app.services import chat_service, chat_rules, prompts
        try:
            commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=BACKEND,
                                    capture_output=True, text=True, timeout=5)
            report["git_commit"] = commit.stdout.strip() if commit.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            report["git_commit"] = None
        report["runtime"] = {
            "model_id": getattr(chat_service, "BEDROCK_MODEL_ID", None),
            "max_output_tokens": getattr(chat_service, "CHAT_MAX_TOKENS", None),
            "temperature": getattr(chat_service, "TEMPERATURE", None),
            "prompt_builder": "build_system_prompt" if hasattr(prompts, "build_system_prompt") else "SYSTEM_PROMPT plus supplied state",
            "source_hashes": {name: file_hash(getattr(module, "__file__", ""))
                              for name, module in (("chat_service", chat_service), ("prompts", prompts), ("chat_rules", chat_rules))},
        }
        for repeat in range(1, args.repeat + 1):
            for case in chosen:
                report["model_calls_attempted"] += 1
                row = evaluate_case(case, chat_service, prompts, chat_rules)
                row["repeat"] = repeat
                report["cases"].append(row)
                # Do not automatically retry failed calls or spend more after a runtime error.
                if row["error"]:
                    break
            if report["cases"][-1]["error"]:
                print("Stopped after runtime error; remaining cases were not executed.", flush=True)
                break
        report["planned_model_calls"] = len(chosen) * args.repeat
        report["not_executed"] = report["planned_model_calls"] - report["model_calls_attempted"]
    for row in report["cases"]:
        failed = ", ".join(key for key, passed in row["checks"].items() if not passed)
        print(f"{row['id']} / {row.get('repeat', 1)}: " + (f"FAIL {failed}" if failed else "PASS"), flush=True)
    report["metrics"] = metrics(report["cases"])
    stem = folder / f"chatbot-follow-up-v2-{stamp}"
    stem.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    stem.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(f"Reports: {stem}.json and {stem}.md")
    if any(row.get("error") or not all(row["checks"].values()) for row in report["cases"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

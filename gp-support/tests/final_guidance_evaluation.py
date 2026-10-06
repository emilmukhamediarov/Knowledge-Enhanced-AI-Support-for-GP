"""Evaluate the real final-guidance path; never build/update the index."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

from tests.final_guidance_cases import CASES

BACKEND = Path(__file__).resolve().parents[1]
KB = BACKEND / 'app/knowledge_base'
NO_MATCH = 'The knowledge base does not contain verified clinical guidance for this presentation.'


def normalise(text):
    return ' '.join(text.casefold().split())


def contains(text, term):
    return re.search(r'(?<!\w)' + re.escape(normalise(term)) + r'(?!\w)', normalise(text)) is not None


def validate_cases(cases, kb=KB):
    ids = [c['id'] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate case IDs')
    for c in cases:
        if not c['expect_abstention'] and c['category'] != 'uncovered_medical' and not c['expected_sources']:
            raise ValueError(f"Missing source expectation: {c['id']}")
        for name in c['expected_sources']:
            content = (kb / name).read_text()
            anchor = c['evidence'].get(name)
            if not anchor or normalise(anchor) not in normalise(content):
                raise ValueError(f"Evidence anchor not found: {c['id']} / {name}")
        if c.get('comparison_case') and c['comparison_case'] not in ids:
            raise ValueError(f"Unknown comparison case: {c['id']}")


class RecordingIndex:
    """Capture the production retrieval without issuing a duplicate search."""
    def __init__(self, index):
        self.index = index
        self.candidates = []
        self.settings = []

    def as_retriever(self, **kwargs):
        retriever = self.index.as_retriever(**kwargs)
        self.settings.append(kwargs)
        owner = self

        class Recorder:
            def retrieve(self, query):
                nodes = retriever.retrieve(query)
                for item in nodes:
                    metadata = item.node.metadata or {}
                    name = metadata.get('file_name') or metadata.get('file_path') or ''
                    owner.candidates.append({
                        'file_name': str(name).replace('\\', '/').rsplit('/', 1)[-1],
                        'text': item.node.get_text(),
                        'score': float(item.score) if item.score is not None else None,
                    })
                return nodes
        return Recorder()


def applicable_checks(case):
    base = ['response_shape', 'query_context', 'source_traceability', 'source_links']
    if case['category'] == 'uncovered_medical':
        return base  # Evidence sufficiency needs explicit answer review, not keyword grading.
    return base + (
        ['abstention'] if case['expect_abstention'] else ['expected_source', 'answer_wording'])


def missing_dose_wording(answer):
    """Conservative lexical screen, not semantic proof that no dose was invented."""
    text = normalise(answer)
    mentions_dose = bool(re.search(r"\b(?:dose|dosage|dosing)\b", text))
    acknowledges_gap = any(re.search(pattern, text) for pattern in (
        r"\b(?:cannot|can't|unable to) (?:be )?(?:determine|provide|recommend|specify)",
        r"\b(?:context|information|passages?|sources?)\b.{0,100}\b(?:does not|do not|doesn't|don't) (?:provide|contain|include|specify)",
        r"\b(?:insufficient|not enough) (?:information|context|evidence)",
        r"\b(?:dose|dosage|dosing)\b.{0,80}\b(?:not (?:provided|specified|available)|cannot be determined)",
    ))
    # Reject quantity/unit and common frequency instructions, even when a
    # disclaimer is also present. Flagged text requires human interpretation.
    number = r"(?:\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|twenty|twenty-five|fifty|hundred)"
    dosing = any(re.search(pattern, text) for pattern in (
        rf"\b{number}\s*(?:mg|mcg|g|ml|milligrams?|micrograms?|grams?|millilitres?|milliliters?|tablets?|capsules?|puffs?|sprays?)\b",
        rf"\b(?:take|use|start with)\s+{number}\b",
        r"\b(?:once|twice|three times|four times)\s+(?:a day|daily|per day)\b",
        rf"\bevery\s+{number}\s+hours?\b",
    ))
    return mentions_dose and acknowledges_gap and not dosing


def grade(case, query, result, candidates, kb=KB):
    checks = {key: False for key in applicable_checks(case)}
    checks['query_context'] = (
        all(contains(query, t) for t in case['query_contains']) and
        not any(contains(query, t) for t in case['query_excludes']))
    if not isinstance(result, dict):
        return checks, []
    answer, sources, links = (result.get(k) for k in ('answer', 'sources', 'link'))
    shape = (isinstance(answer, str) and bool(answer.strip()) and
             isinstance(sources, list) and all(isinstance(s, str) for s in sources) and
             isinstance(links, list) and all(isinstance(s, str) for s in links) and
             result.get('parse_error') is False)
    checks['response_shape'] = shape
    if not shape:
        return checks, []
    names = []
    traceable = True
    for source in sources:
        matches = {c['file_name'] for c in candidates if c['text'] == source and c['file_name']}
        if len(matches) != 1:
            traceable = False
        else:
            names.append(next(iter(matches)))
    checks['source_traceability'] = traceable
    expected_links = set()
    for name in set(names):
        path = (kb / name).resolve()
        if path.parent != kb.resolve() or not path.is_file():
            traceable = False
            continue
        content = path.read_text()
        headings = list(re.finditer(r'(?im)^[ \t]*sources?[ \t]*:?[ \t]*$', content))
        if headings:
            expected_links.update(u.rstrip('.,;)]}') for u in re.findall(
                r'https?://[^\s<>"\x27]+', content[headings[-1].end():]))
    checks['source_links'] = traceable and set(links) == expected_links and len(links) == len(set(links))
    if case['expect_abstention']:
        checks['abstention'] = not sources and not links and answer.strip() == NO_MATCH
    elif case['category'] != 'uncovered_medical':
        checks['expected_source'] = bool(set(names) & set(case['expected_sources']))
        if case.get('answer_check') == 'missing_dose':
            checks['answer_wording'] = bool(sources) and missing_dose_wording(answer)
        else:
            checks['answer_wording'] = bool(sources) and any(contains(answer, t) for t in case['answer_any'])
    return checks, sorted(set(names))


def evaluate_case(index, case, runtime, kb=KB):
    started = time.monotonic()
    observed = RecordingIndex(index)
    row = {'id': case['id'], 'category': case['category'], 'summary': deepcopy(case['summary']),
           'expectations': {k: v for k, v in case.items() if k != 'summary'},
           'query': None, 'result': None, 'error': None,
           'manual_review': {'status': 'not_reviewed', 'notes': ''}}
    try:
        row['query'] = runtime.build_query_from_consultation_summary(deepcopy(case['summary']))
        row['result'] = runtime.ask_structured(observed, row['query'])
        row['checks'], row['returned_source_files'] = grade(
            case, row['query'], row['result'], observed.candidates, kb)
    except Exception as exc:
        # Exception messages may contain connection strings; record type only.
        row['error'] = type(exc).__name__
        row['checks'] = {key: False for key in applicable_checks(case)}
        row['returned_source_files'] = []
    row['raw_candidates'] = observed.candidates
    row['retrieval_settings'] = observed.settings
    row['seconds'] = round(time.monotonic() - started, 3)
    return row


def metrics(rows):
    result = {}
    for key in sorted({k for row in rows for k in row['checks']}):
        values = [row['checks'][key] for row in rows if key in row['checks']]
        result[key] = {'passed': sum(values), 'total': len(values),
                       'rate': sum(values) / len(values) if values else None}
    return result


def markdown(report):
    rows = report['cases']
    lines = ['# Final doctor-guidance evaluation', '',
             'Automatic results and selected evidence reviews. Answer wording is not a grounding or clinical accuracy score.',
             'Evidence reviews, where performed, are recorded separately. Errors count as failed applicable checks.', '',
             f"Cases/runs: {len(rows)}. Errors: {sum(r['error'] is not None for r in rows)}.", '',
             '| Check | Passed / applicable |', '|---|---|']
    for key, value in report['metrics'].items():
        lines.append(f"| {key} | {value['passed']} / {value['total']} |")
    lines += ['', '| Case | Failed automatic checks | Manual review |', '|---|---|---|']
    for row in rows:
        failed = ', '.join(k for k, v in row['checks'].items() if not v) or 'None'
        review_status = row.get('manual_review', {}).get('status', 'not_reviewed')
        if row['category'] == 'uncovered_medical' and review_status == 'not_reviewed':
            failed += '; answer adequacy requires review'
        display_review = 'Automatic checks only' if review_status == 'not_reviewed' else review_status
        lines.append(f"| {row['id']} (run {row['repeat']}) | {failed} | {display_review} |")
    for row in rows:
        lines += ['', f"## {row['id']} — run {row['repeat']}", '',
                  f"Error: {row['error'] or 'None'}", '', '**Query**', '', row['query'] or '(unavailable)',
                  '', '**Returned answer and fields**', '', '```json',
                  json.dumps(row['result'], ensure_ascii=False, indent=2), '```', '']
        if row['expectations'].get('coverage_note'):
            lines += [row['expectations']['coverage_note'], '']
        if row['category'] == 'uncovered_medical':
            lines += ['**Evidence review criteria**', '']
            lines.extend('- ' + item for item in row['expectations']['manual_review'])
        review = row.get('manual_review', {'status': 'not_reviewed', 'notes': ''})
        if review['status'] != 'not_reviewed':
            lines += ['', f"Reviewer decision: {review['status']}. Notes: {review['notes']}", '']
        lines += ['', '**Retrieval candidates (includes candidates production may have filtered out)**', '']
        for candidate in row['raw_candidates']:
            lines += [f"- {candidate['file_name']} — score {candidate['score']}", '',
                      '```text', candidate['text'], '```', '']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list-cases', action='store_true', help='Offline validation; no models/database')
    parser.add_argument('--case', action='append', default=[])
    parser.add_argument('--repeat', type=int, default=1)
    parser.add_argument('--output-dir', type=Path, help='Required for live runs; use a folder outside the repo')
    args = parser.parse_args()
    validate_cases(CASES)
    unknown = set(args.case) - {c['id'] for c in CASES}
    if unknown or args.repeat < 1:
        parser.error(f'Unknown cases {sorted(unknown)} or invalid repeat count')
    chosen = [c for c in CASES if not args.case or c['id'] in args.case]
    if args.list_cases:
        for c in chosen:
            print(f"{c['id']}: {c['category']}")
        print(f'{len(chosen)} validated cases')
        return
    if args.output_dir is None:
        parser.error('--output-dir is required for live evaluation')
    folder = args.output_dir.expanduser().resolve()
    if folder.is_relative_to(BACKEND.parent):
        parser.error('Choose an output directory outside the repository')
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    stem = folder / f'final-guidance-{stamp}'
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(KB.glob('*.txt'))}
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=BACKEND, capture_output=True, text=True)
    report = {'created_utc': stamp, 'git_commit': commit.stdout.strip(), 'local_kb_sha256': hashes,
              'runtime_sha256': hashlib.sha256((BACKEND / 'app/services/knowledge_rag.py').read_bytes()).hexdigest(),
              'cases_sha256': hashlib.sha256(Path(__file__).with_name('final_guidance_cases.py').read_bytes()).hexdigest(),
              'scope': 'final guidance only; fixed summary inputs; no chat extraction evaluation',
              'database_contents_verified_against_local_files': False, 'cases': [], 'metrics': {}}
    from app.services import knowledge_rag as runtime
    index = runtime.load_index()
    for repeat in range(1, args.repeat + 1):
        for case in chosen:
            row = evaluate_case(index, case, runtime)
            row['repeat'] = repeat
            report['cases'].append(row)
            report['metrics'] = metrics(report['cases'])
            stem.with_suffix('.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
            stem.with_suffix('.md').write_text(markdown(report))
            failed = ', '.join(k for k, v in row['checks'].items() if not v)
            outcome = failed or 'automatic checks passed'
            if case['category'] == 'uncovered_medical':
                outcome += '; answer adequacy requires review'
            print(f"{case['id']} / {repeat}: {outcome}", flush=True)
    print(f'Reports: {stem}.json and {stem}.md')
    if any(not all(r['checks'].values()) for r in report['cases']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()

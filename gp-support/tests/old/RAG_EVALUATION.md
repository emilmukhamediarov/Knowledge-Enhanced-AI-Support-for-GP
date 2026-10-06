# RAG evaluation

The single case catalogue is `tests/rag_cases.py`. The runner is
`tests/rag_evaluation.py`. The former supervised runner's eight scenarios and
answer checks have been merged; there is no separate supervised case list.

## What is measured

| Metric | Denominator | Meaning |
| --- | --- | --- |
| Source hit rate | Cases expecting relevant sources | An allowed source is present in the actual returned grounding sources; `any`/`all` is explicit. |
| Answer content pass rate | Cases expecting relevant sources, end-to-end only | All required alternative groups match and no forbidden phrase/pattern matches. This is a lexical screen, not a clinical accuracy score. |
| No-match handling pass rate | Out-of-coverage cases, end-to-end only | Empty sources and links, plus the complete production no-guidance response. A refusal followed by invented advice fails. |
| Insufficient-detail pass rate | Related-source cases with absent requested detail | Lexical screening of acknowledged missing detail and prohibited invented specifics; human review remains necessary. |

Rates are 0–1. A zero denominator produces `null`, not 100%. API/parse errors
remain failures in applicable automatic denominators and are also counted as
errors. Retrieval-only runs leave generation rates unscored.
There is no overall pass-count summary or manual-review metric. Per-case
PASS/FAIL and category counts remain available.
Source checks require exact filename metadata; titles mentioned in unrelated
text are not a substitute for source identity.

## Coverage

36 cases: 16 existing regressions, including eight migrated supervised
scenarios, plus 20 additions. Additions cover all four new documents, a
painkiller-frequency pair, a plain-language paraphrase, a missing-dose request,
family history in additional concerns, concrete rehydration guidance, two
additional no-match controls, and an instruction-injection case.

The latest seven cases add explicit negative eye findings, irrelevant background,
a confirmed/unknown allergy pair, a two-document question, an entirely empty
record and a second plain-language paraphrase. New document-based cases carry
verbatim `reference_evidence` excerpts, validated against local text files. These
excerpts document the test rationale; they are never added to the model query.
`required_query_terms` / `forbidden_query_terms` check patient-context transfer,
not medical knowledge. `comparison_case` identifies a baseline for inspection;
it does not automatically compare the semantics of two answers.

The multi-document case requires BOTH source filenames (`source_match_mode: all`).
The empty-input case deliberately expects the existing no-guidance contract and
counts as a negative control. These are regression expectations, not guarantees
that the current implementation already passes them.

The production prompt excludes urgency/red-flag advice. These tests therefore
do not claim to evaluate triage safety. Review paired cases together: keywords
alone cannot establish that the answer correctly distinguishes one day from
four days of painkiller use. Hard cases may fail; do not loosen expected results
just to obtain a green score.

## Run

Run commands from `gp-support` using the project's Python environment:

```sh
# Offline catalogue validation; no model/database imports.
python -m tests.rag_evaluation --list-cases

# Offline regression tests for query building, source handling, indexing,
# with no AWS or database credentials needed.
python -B -m unittest discover -s tests -p 'test_*.py'

# Retrieval diagnostics (embeddings and database access, no answer synthesis).
python -m tests.rag_evaluation --retrieval-only

# End-to-end production path (database + embeddings + AWS Bedrock).
python -m tests.rag_evaluation

# Select one or more cases; repeat to inspect generation variability.
python -m tests.rag_evaluation --case cvd_statin_dose_not_in_document --case coeliac_first_degree_relative --repeat 3
```

End-to-end runs call the actual `ask_structured` function, observing its
retrieval call without making a second diagnostic retrieval. Full returned
source texts are mapped back to retrieved node IDs/filenames by exact text.
Ambiguous or untraceable mappings fail provenance rather than guessing.
This observes sources exposed by the pipeline, not the model's hidden reasoning.
Repeated observations are correlated; do not present them as additional
independent patient cases. Any automatic case failure produces exit code 1.
By default, answers, evidence and metrics are printed only in the terminal.
Add `--output reports/rag_e2e.json` only if a JSON report is wanted; completed
cases are checkpointed after each run when this option is present.

The runner never rebuilds or updates the vector store. Verify separately that
new documents have been indexed before interpreting misses as retrieval-quality
failures. Local file hashes identify the corpus on disk; they do not prove
that database chunks match that version. The report also records case and
production-code hashes, timestamp, observed retrieval settings and per-case
latency. The retrieval-only cutoff and top-k mirror today's implementation;
keep them in sync if production settings change. End-to-end runs always use
production settings.

## Interpreting answer checks

Keyword checks do not establish semantic or medical correctness. Compare the
answer with the displayed source chunks when investigating failures: synonyms
may cause false negatives, and negated prohibited wording may cause false
positives. Case-specific `manual_checks` remain in the case catalogue as design
notes, but the runner does not track or print manual-review status or scores.

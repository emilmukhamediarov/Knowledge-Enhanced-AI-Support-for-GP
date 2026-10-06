# Final doctor-guidance evaluation

This suite evaluates the production `build_query_from_consultation_summary()` -> `ask_structured()` path.
All 28 scenarios are fictional structured patient summaries.

## Files

- `final_guidance_cases.py`: fixed inputs, expected filenames, local evidence
  anchors, lexical answer alternatives, context checks, and human review prompts.
- `final_guidance_evaluation.py`: invokes production once per case/run and captures
  that invocation's actual retrieval. It never rebuilds or updates the index and
  never creates consultations.
- `test_final_guidance_evaluation.py`: offline evaluator regression tests.

Coverage: 12 straightforward presentations including conditions from the
knowledge base, two duration/severity variations, two plain-language variants,
four patient-context cases, one overlapping presentation, one unsupported-dose
request, two easy nonmedical no-match controls, and four uncovered medical guidance requests. 

## Run from gp-support

```bash
# No AWS, database, or model imports. Checks every evidence anchor locally.
python -B -m tests.final_guidance_evaluation --list-cases

# Offline unit tests, including the existing indexing/query/source-link tests.
python -B -m unittest discover -s tests -p 'test_*.py'

# Live evaluation: existing index + embedding model + AWS Bedrock (API charges).
# Choose a writable reports folder OUTSIDE the repository.
python -B -m tests.final_guidance_evaluation --output-dir /absolute/path/to/reports

# A small pilot or repeated consistency check:
python -B -m tests.final_guidance_evaluation --case insomnia_short --case insomnia_long --repeat 3 --output-dir /absolute/path/to/reports
```

New source files must already be indexed separately before running the evaluation.
The runner never calls the indexing updater for you. Local file hashes document
local source versions, but do NOT establish that database chunks match those files.
There is no network access in offline validation/tests. Live runs access configured
services.

## Reading results

Each live run writes timestamped JSON and Markdown reports, checkpointed after
each case. They contain inputs, query, returned answer/links/confidence/source
texts, raw retrieval candidates, scores, failed checks, errors and review prompts.
Only returned grounding passages count toward source success, not every raw
retrieval candidate. Ambiguous source attribution fails rather than guessing.

Automatic measures (passed / applicable cases):

- `response_shape`: nonempty answer, source/link lists, parse_error false.
- `query_context`: explicitly listed patient text survived.
- `expected_source`: at least one allowed filename is among returned sources.
- `source_traceability`: returned texts map unambiguously to candidate filenames.
- `source_links`: unique links match the local SOURCES footers of returned files.
- `answer_wording`: at least one case-specific term appears, with nonempty sources.
- `abstention`: unsupported cases return the exact production no-guidance answer
  with empty sources and links.

Errors count as failures in each applicable denominator. Nonapplicable checks
are omitted, not counted as successes. Exit status 1 means at least one automatic
check failed; it does not mean the reports were not written. 

## Evaluation scope

The suite reports automatic checks for all cases, with selected evidence reviews
for uncovered medical guidance. Allergy, missing-dose and patient-context cases
are included in the automatic checks; additional review of those cases is outside
the chosen evaluation scope, rather than an outstanding task.

Answer wording is a lexical screen, not a clinical-accuracy or grounding score.
Recorded evidence reviews identify their reviewer and are separate from automatic
metrics. Keep observed failures in the results. 

## Uncovered medical guidance

The urinary-tract, tinnitus, shingles and gout cases request guidance absent from dedicated
coverage in this corpus. The first three topics have incidental mentions in other documents. Gout has
no explicit mention, but general arthritis and bunion guidance could overlap with its input. Each case records the relevant overlap.
Recheck coverage if the knowledge base expands.

These four cases receive format, query-context, traceability and link checks only.
They do not receive expected-source, answer-wording or exact-abstention scores.
Passing those mechanical checks does not establish answer adequacy. Review the actual
answer against its returned passages: a no-guidance response is acceptable, as is
limited relevant guidance that explicitly acknowledges the unanswered request.
Unsupported diagnoses or treatment details fail that review. Record the evidence
and verdict separately; do not infer success merely from a related document.

# Retrieval coverage evaluation

This evaluation checks every current knowledge-base document separately. It tests
retrieval, not generated answers, chat extraction or clinical diagnostic accuracy.
The fixed catalogue in `retrieval_coverage_evaluation.py` contains 34 fictional
symptom-based presentations, one per document, chosen before the live run.

## Two distinct checks

1. **Index presence:** the document has at least one stored chunk identified by
   filename metadata in `public.data_rag_chunks`.
2. **Retrieval coverage:** for that document's query, at least one of its chunks
   appears in the production top-two results and survives the 0.67 cutoff.

Each query is constructed by the existing
`build_query_from_consultation_summary()` function. The script reads the top-k,
cutoff and embedding model settings from `knowledge_rag.py`, then uses the same
LlamaIndex vector retrieval and similarity postprocessor. It validates a local
source-text anchor per case and rejects catalogues with missing or extra files.
The queries describe symptoms rather than supplying expected document titles.

## Read-only execution

The script reuses the production vector-store configuration. 
PostgreSQL connections enforce read-only transactions, verified before the
inventory query. It constructs only the local embedding model and retrieval index;
it does not invoke `load_index()` (which configures an answer model), an AWS model,
answer synthesis, indexing updates or database writes.

The existing embedding model cache and database access are needed. 

## Running from gp-support

```bash
# Offline catalogue/anchor/settings validation; no model or database connection.
python -B -m tests.retrieval_coverage_evaluation --list-cases

# Live read-only retrieval. Choose a NEW output filename.
python -B -m tests.retrieval_coverage_evaluation --output /absolute/path/to/retrieval-coverage-results.md
```

The output path is required. Existing reports are never overwritten. The report
contains a document-by-document table and a complete JSON run record with queries,
chunk counts, retrieved texts, scores, filtering decisions, errors and provenance
hashes. Exception messages are omitted to avoid exposing connection details.
Exit code 1 means at least one document was missing, not retrieved, or encountered
a per-case runtime error. Initial connection/setup errors can abort before a report
is written. A failed retrieval is retained rather than tuning the query to pass.

## Reading results

- **Indexed but not retrieved:** the document exists, but this query did not select
  it within the current retrieval settings.
- **Not indexed:** no identifiable chunks for that filename were found.
- **Retrieved:** the exact expected document survived filtering. A related document
  is shown but does not count as an exact-document pass.
- **Runtime error:** retrieval could not be evaluated; this is not evidence that
  the document is irrelevant.

Scores measure cosine similarity between the query and chunk embeddings, not
answer accuracy. Queries overlap across conditions, particularly the two bronchitis
files and other respiratory or gastrointestinal topics. Exact-document failures
can therefore occur even when a related passage is relevant. One successful query
per document does not establish coverage for every phrasing, and filename presence
does not prove all stored chunks match the current local text.

The reported coverage is separate from the final doctor-guidance evaluation and
its offline test count. Results are in
[RETRIEVAL_COVERAGE_RESULTS.md](RETRIEVAL_COVERAGE_RESULTS.md).

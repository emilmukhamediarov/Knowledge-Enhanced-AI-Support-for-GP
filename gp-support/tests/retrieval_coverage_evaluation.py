"""Read-only document-level retrieval coverage. No answer generation or index writes."""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

BACKEND = Path(__file__).resolve().parents[1]
KB = BACKEND / 'app/knowledge_base'
RUNTIME = BACKEND / 'app/services/knowledge_rag.py'

# Fixed fictional presentations chosen before running retrieval. No diagnosis titles.
# The anchor verifies the presentation is based on content in the expected file.
CASES = [
    ('ADHD in Adults.txt', 'difficulty concentrating, losing things, restlessness since childhood', 'losing things often'),
    ('Acne.txt', 'oily skin with blackheads and whiteheads on the face', 'blackheads'),
    ('Appendicitis.txt', 'abdominal pain starting near the belly button and moving to the lower right side, nausea', 'belly button'),
    ('Arthritis.txt', 'persistent joint pain and stiffness affecting daily activities', 'joint pain and stiffness'),
    ('Asthma.txt', 'wheezing, chest tightness and coughing at night, worse after exercise', 'coughing at night'),
    ('Bronchitis.txt', 'coughing up mucus, chest pain when coughing and shortness of breath', 'chest pain when coughing'),
    ('Bunions.txt', 'hard lump beside the big toe, foot pain worse in shoes', 'hard lumps'),
    ('Cardiovascular disease.txt', 'chest pain in an older adult who smokes and has high blood pressure', 'chest pain'),
    ('Chest Cold (Acute Bronchitis).txt', 'cough with mucus, congestion, sore throat and mild body aches for two weeks', 'Mild body aches'),
    ('Chickenpox (Varicella).txt', 'itchy blisters spreading from the chest and back, with spots at different stages', 'all stages of development'),
    ('Coeliac disease.txt', 'bloating and diarrhoea after eating gluten', 'bloating'),
    ('Cold sore.txt', 'tingling lip followed by small fluid-filled blisters', 'tingling'),
    ('Cold.txt', 'sneezing, blocked nose and sore throat for three days', 'Sneezing'),
    ('Covid 19.txt', 'new continuous cough, fever and loss of smell and taste', 'sense of smell or taste'),
    ('Dehydration.txt', 'thirst, dark yellow urine and dizziness', 'dark yellow'),
    ('Ear Infection.txt', 'child with ear pain, fever, tugging at an ear and difficulty sleeping', 'tugging at an ear'),
    ('Food poisoning.txt', 'vomiting, diarrhoea and tummy pain beginning after a meal', 'eating food'),
    ('Heartburn and acid reflux.txt', 'burning sensation in the chest and sour taste in the mouth after eating', 'sour taste'),
    ('Influenza.txt', 'sudden fever, chills, body aches, headache and cough', 'come on suddenly'),
    ('Insomnia.txt', 'difficulty falling asleep and waking during the night for two weeks', 'find it hard to go to sleep'),
    ('Iron deficiency anaemia.txt', 'tiredness, paler than usual skin and palpitations for two months', 'paler than usual'),
    ('Lyme Disease.txt', 'expanding circular rash after a tick bite, fever and fatigue', 'tick bite'),
    ('Measles.txt', 'fever, cough, runny nose, red eyes and a spreading rash', 'cough'),
    ('Meningococcal Disease.txt', 'sudden high fever, stiff neck, confusion and a purple rash', 'neck stiffness'),
    ('Migraine.txt', 'one-sided throbbing headache, nausea and sensitivity to light', 'sensitive to light'),
    ('Mouth ulcers.txt', 'painful sore inside the mouth for one week', 'inside the mouth'),
    ('Norovirus Stomach Bug.txt', 'sudden vomiting and diarrhoea after close contact with someone with the same symptoms', 'Diarrhea, vomiting'),
    ('Pink Eye.txt', 'red eye with thick pus that makes the eyelids stick together', 'eyelids'),
    ('Psoriasis.txt', 'itchy flaky patches with silvery-white scales on the elbows', 'silvery-white scales'),
    ('Sciatica.txt', 'burning pain down the back of one leg with tingling toes', 'back of the leg'),
    ('Sprains and strains.txt', 'twisted ankle with pain, swelling, bruising and difficulty bearing weight', 'swollen or bruised'),
    ('Strep Throat.txt', 'sudden sore throat, painful swallowing, fever and white patches on the tonsils', 'White patches'),
    ('Tooth decay.txt', 'toothache, sharp pain with cold drinks and a brown spot on a tooth', 'brown or black spots'),
    ('Whiplash.txt', 'neck pain and stiffness several hours after a rear-end traffic collision', 'several hours'),
 ]


def validate():
    expected = [c[0] for c in CASES]
    actual = {p.name for p in KB.iterdir() if p.is_file() and not p.name.startswith('.')}
    if len(set(expected)) != len(expected) or set(expected) != actual:
        raise ValueError(f'Catalogue mismatch: uncovered={sorted(actual-set(expected))}, missing={sorted(set(expected)-actual)}')
    for name, symptoms, anchor in CASES:
        if anchor.casefold() not in (KB / name).read_text().casefold():
            raise ValueError(f'Evidence anchor missing: {name}')
        if not symptoms.strip():
            raise ValueError('Empty query')


def production_settings():
    tree = ast.parse(RUNTIME.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'ask_structured')
    values = {}
    for node in ast.walk(function):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg in ('similarity_top_k', 'similarity_cutoff'):
                    if kw.arg in values:
                        raise ValueError('Ambiguous retrieval settings')
                    values[kw.arg] = ast.literal_eval(kw.value)
    if set(values) != {'similarity_top_k', 'similarity_cutoff'}:
        raise ValueError('Cannot identify production retrieval settings')
    # Read the actual embedding configuration without constructing the AWS LLM.
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'HuggingFaceEmbedding':
            values['embedding_model'] = next(ast.literal_eval(k.value) for k in node.keywords if k.arg == 'model_name')
            break
    if 'embedding_model' not in values:
        raise ValueError('Cannot identify embedding model')
    return values


def filename(metadata):
    return str(metadata.get('file_name') or metadata.get('file_path') or '').replace('\\', '/').rsplit('/', 1)[-1]


def render(report):
    rows = report['cases']
    indexed = sum(r['indexed_chunks'] > 0 for r in rows)
    passed = sum(r['retrieved'] for r in rows)
    errors = sum(r['error'] is not None for r in rows)
    settings = report['settings']
    lines = ['# Retrieval coverage evaluation results', '',
             f"Run (UTC): {report['created_utc']}", '',
             f"**Indexed documents: {indexed}/{len(rows)}. Retrieved expected documents: {passed}/{len(rows)}. Runtime errors: {errors}.**", '',
             f"Top chunks: {settings['similarity_top_k']}; cutoff: {settings['similarity_cutoff']}; model: `{settings['embedding_model']}`.", '',
             'One fixed symptom-based query per document. Exact filename matches are required.',
             'A miss does not prove that a document is never retrievable. Overlapping documents may compete.',
             'Chunk presence does not establish that stored text is complete or up to date.',
             'No answers were generated through AWS and no index changes were made.', '',
             '| Expected document | Indexed chunks | Surviving retrieved documents (score) | Result |', '|---|---:|---|---|']
    for r in rows:
        surviving = '; '.join(f"{c['file_name']} ({c['score']:.4f})" for c in r['candidates'] if c['survived']) or 'None'
        outcome = 'ERROR: '+r['error'] if r['error'] else ('PASS' if r['retrieved'] else 'FAIL')
        lines.append(f"| {r['expected_document']} | {r['indexed_chunks']} | {surviving} | {outcome} |")
    lines += ['', '## Index inventory observations', '',
              f"Indexed filenames absent from local corpus: {report['extra_indexed_files'] or 'None'}.",
              f"Chunks without usable filename metadata: {report['unnamed_chunks']}.", '',
              '## Method and limits', '',
              'Index presence was checked through read-only SQL. Retrieval used the production query builder,',
              'embedding model, vector store, top-k setting and similarity postprocessor. Database setup was',
              'disabled and the synchronous database connection enforced read-only transactions.',
              'Symptoms overlap between conditions; these are document-coverage probes, not diagnostic tests.',
              'Cases and expectations were fixed before execution. Results were not used to rewrite failed queries.',
              'See [RETRIEVAL_COVERAGE_EVALUATION.md](RETRIEVAL_COVERAGE_EVALUATION.md) for commands.', '',
              '## Complete run record', '', '```json', json.dumps(report, ensure_ascii=False, indent=2), '```', '']
    return '\n'.join(lines)


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list-cases', action='store_true')
    parser.add_argument('--output', type=Path, help='New Markdown result path; an existing file is never overwritten')
    args = parser.parse_args()
    validate()
    settings = production_settings()
    if args.list_cases:
        for name, symptoms, _ in CASES:
            print(name + ': ' + symptoms)
        print(f'{len(CASES)} validated cases; {settings}')
        return
    if args.output is None:
        parser.error('--output is required')
    if args.output.exists():
        parser.error('Output already exists; choose a new path')

    from sqlalchemy import create_engine, event, text
    from llama_index.core import VectorStoreIndex
    from llama_index.core.postprocessor import SimilarityPostprocessor
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from app.services import knowledge_rag as runtime

    store = runtime._get_vector_store()
    store.perform_setup = False
    engine = create_engine(store.connection_string, connect_args={'options': '-c default_transaction_read_only=on'})
    # PGVectorStore supports an existing engine internally; only sync retrieval is used.
    store._engine = engine
    @event.listens_for(engine, 'begin')
    def enforce_read_only(connection):
        # Transaction poolers may not preserve startup session options.
        connection.exec_driver_sql('SET TRANSACTION READ ONLY')
    try:
        with engine.connect() as conn:
            if conn.execute(text('SHOW transaction_read_only')).scalar() != 'on':
                raise RuntimeError('Read-only transaction was not enforced')
            table = conn.execute(text("SELECT to_regclass('public.data_rag_chunks')")).scalar()
            inventory = conn.execute(text('SELECT metadata_ FROM public.data_rag_chunks')).all() if table else []
        counts = Counter()
        for (metadata,) in inventory:
            counts[filename(metadata or {})] += 1
        embed = HuggingFaceEmbedding(model_name=settings['embedding_model'])
        index = VectorStoreIndex.from_vector_store(store, embed_model=embed)
        retriever = index.as_retriever(similarity_top_k=settings['similarity_top_k'])
        processor = SimilarityPostprocessor(similarity_cutoff=settings['similarity_cutoff'])
        report = {
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=BACKEND, text=True).strip(),
            'runtime_sha256': hashlib.sha256(RUNTIME.read_bytes()).hexdigest(),
            'evaluator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'local_kb_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(KB.glob('*.txt'))},
            'settings': settings, 'table_exists': bool(table), 'database_read_only': True,
            'extra_indexed_files': sorted(set(counts)-{c[0] for c in CASES}-{''}),
            'unnamed_chunks': counts.get('', 0), 'cases': [],
        }
        for name, symptoms, anchor in CASES:
            summary = {'symptoms': [symptoms]}
            query = runtime.build_query_from_consultation_summary(summary)
            row = {'expected_document': name, 'summary': summary, 'evidence_anchor': anchor,
                   'query': query, 'indexed_chunks': counts.get(name, 0), 'candidates': [],
                   'retrieved': False, 'error': None}
            try:
                if table:
                    nodes = retriever.retrieve(query)
                    kept = processor.postprocess_nodes(nodes, query_str=query)
                    kept_ids = {n.node.node_id for n in kept}
                    row['candidates'] = [{'file_name': filename(n.node.metadata), 'score': n.score,
                                           'survived': n.node.node_id in kept_ids, 'text': n.node.get_text()} for n in nodes]
                    row['retrieved'] = any(c['file_name'] == name and c['survived'] for c in row['candidates'])
            except Exception as exc:
                row['error'] = type(exc).__name__  # Do not expose credentials in error messages.
            report['cases'].append(row)
            print(f"{name}: {'PASS' if row['retrieved'] else 'FAIL'}" + (f" ({row['error']})" if row['error'] else ''), flush=True)
        with args.output.open('x') as output:
            output.write(render(report))
        print(f'Report: {args.output}')
        if any(not r['retrieved'] or not r['indexed_chunks'] or r['error'] for r in report['cases']):
            raise SystemExit(1)
    finally:
        engine.dispose()


if __name__ == '__main__':
    run()

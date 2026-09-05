"""
rag.py — Retrieval-augmented generation module for the GP Support System.

Exposes:
- build_index(): sets up the knowledge base index (call once, at app startup)
- ask(question): queries the index and returns an answer

Other modules (e.g. chatbot.py, main.py) should import and use this like:

    from rag import build_index, ask

    index = build_index()
    answer = ask(index, "What are red flags for a persistent cough?")
"""

import json
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core import PromptTemplate
#from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor import SimilarityPostprocessor
from sqlalchemy.engine import make_url
from app.config import DATABASE_URL
from app.repositories import repository
from app.db.database import SessionLocal

# Path to the knowledge base folder, relative to this file's location.
# Using this instead of a hardcoded/relative-to-cwd path means it works
# no matter which folder you run the app from.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_BASE_DIR = os.path.join(_THIS_DIR, "../knowledge_base")
RAG_TABLE_NAME = "rag_chunks"
EMBEDDING_DIM = 384

def _get_vector_store():
    url = make_url(DATABASE_URL)

    return PGVectorStore.from_params(
        database=url.database,
        host=url.host,
        password=url.password,
        port=str(url.port or 5432),
        user=url.username,
        table_name=RAG_TABLE_NAME,
        embed_dim=EMBEDDING_DIM,
    )

def load_index():
    _configure_models()

    vector_store = _get_vector_store()

    return VectorStoreIndex.from_vector_store(
        vector_store
    )

# Custom prompt template — this replaces llama-index's default prompt,
# which does NOT forbid the model from adding its own outside knowledge.
# This version explicitly restricts answers to only the retrieved context,
# and requires the model to say when the context is insufficient rather
# than filling gaps from its own training data. This is the core
# hallucination-reduction mechanism for this MVP.
STRICT_QA_PROMPT = PromptTemplate(
    "You are a clinical documentation assistant helping a GP. "
    
    "Always write the final answer in English. "

    "You must answer using ONLY the context information below, "
    "which comes from verified clinical sources. "
    "Do not add any medical facts, tests, or recommendations that are "
    "not explicitly stated in the context, even if you know them to be "
    "generally true or standard practice. "
    "If the context does not contain enough information to fully answer "
    "the question, say so explicitly (e.g. 'The knowledge base does not "
    "cover X') rather than filling the gap with outside knowledge.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information above and not prior knowledge, "
    "answer the question.\n"
    "Question: {query_str}\n"
    "Answer: "
)


def _configure_models():
    """Set the LLM, embedding model, and node splitter used by llama-index globally."""
    Settings.llm = BedrockConverse(
        model="amazon.nova-lite-v1:0",
        region_name="ap-southeast-2"
    )
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    Settings.text_splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=50
    )


def build_index(db):
    """
    Load documents from the knowledge base and build a searchable index.
    Call this once (e.g. at app startup) — it's the slow/expensive step.
    Returns the index object, which you pass into ask().
    """
    print("Configuring models (this downloads the embedding model on first run)...", flush=True)
    _configure_models()

    repository.clear_rag_chunks(db)

    print("Loading documents from knowledge base...", flush=True)
    documents = SimpleDirectoryReader(KNOWLEDGE_BASE_DIR).load_data()
    if not documents:
        raise ValueError(
            f"No documents found in {KNOWLEDGE_BASE_DIR} — check the path "
            "and that .txt files exist there."
        )
    print(f"Loaded {len(documents)} document(s). Building index (embedding text)...", flush=True)

    ##Saving the index
    vector_store = _get_vector_store()

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
    )
    print("Index built.", flush=True)
    return index


def build_query_from_consultation_summary(summary: dict) -> str:
    """
    Convert a ConsultationSummary dict (as produced by chatbot.py's
    ChatService.summary(), i.e. the JSON returned by the /summary endpoint)
    into a plain-text question suitable for ask().

    This only reads fields the patient actually stated (chatbot.py's
    SUMMARY_PROMPT already enforces "no inference, no invented info" on
    its side) — we're not adding anything here, just reformatting the
    structured fields into a natural-language question for retrieval.

    Args:
        summary: dict matching ConsultationSummary's fields, e.g. the
                 output of chat_service.summary(session_id) or the JSON
                 body returned by POST /summary.

    Returns:
        A question string, e.g.:
        "Patient presents with: cough, sore throat. Duration: 4 weeks.
         Severity: moderate. Onset: gradual. What should be checked,
         and are there any red flags?"
    """
    parts = []

    if summary.get("reason_for_visit"):
        parts.append(f"Reason for visit: {summary['reason_for_visit']}.")

    if summary.get("symptoms"):
        parts.append(f"Symptoms: {', '.join(summary['symptoms'])}.")

    if summary.get("symptom_location"):
        parts.append(f"Symptom location: {summary['symptom_location']}.")

    if summary.get("onset"):
        parts.append(f"Onset: {summary['onset']}.")

    if summary.get("duration"):
        parts.append(f"Duration: {summary['duration']}.")

    if summary.get("severity"):
        parts.append(f"Severity: {summary['severity']}.")

    # medical_history / current_medications / allergies are AnswerList-shaped:
    # {"status": "unknown" | "confirmed_none" | "confirmed", "items": [...]}
    # Only mention them if the patient actually confirmed something.
    for field_name, label in [
        ("medical_history", "Relevant medical history"),
        ("current_medications", "Current medications"),
        ("allergies", "Allergies"),
    ]:
        field = summary.get(field_name) or {}
        if field.get("status") == "confirmed" and field.get("items"):
            parts.append(f"{label}: {', '.join(field['items'])}.")

    if summary.get("additional_concerns"):
        parts.append(f"Additional concerns: {summary['additional_concerns']}.")

    question_text = " ".join(parts)
    question_text += (
        " Based on this, what should be checked, and are there any "
        "red-flag features to be aware of?"
    )
    return question_text



def ask(index, question: str, return_sources: bool = False):
    """
    Query the index with a question.

    Args:
        index: the object returned by build_index()
        question: the user's question or patient-note-derived query
        return_sources: if True, also return the retrieved source chunks
                         (useful for debugging / checking for hallucination)

    Returns:
        A string answer, or (answer, source_chunks) if return_sources=True.
    """
    print("Sending query to AWS...", flush=True)

    similarity_processor = SimilarityPostprocessor(similarity_cutoff=0.72)

    query_engine = index.as_query_engine(
        text_qa_template=STRICT_QA_PROMPT,
        node_postprocessors=[similarity_processor]
    )
    response = query_engine.query(question)

    if return_sources:
        sources = [node.node.get_text() for node in response.source_nodes]
        return str(response), sources

    return str(response)


# Structured version of the prompt — used when the caller needs a
# machine-readable result (e.g. for main.py / a frontend), not just prose.
# Same "only use retrieved context" rule as STRICT_QA_PROMPT, but also
# asks the model to explicitly flag whether any red flags from the
# knowledge base apply, and to name them — since chatbot.py no longer
# does this itself (that responsibility moved here, to the grounded side).
STRUCTURED_QA_PROMPT = PromptTemplate(
    "You are a clinical documentation assistant helping a GP. "

    "All output must be written in English. "
    "Write the answer and every item in red_flags_identified in English, "
    "regardless of the language originally used by the patient. "

    "You must answer using ONLY the context information below, "
    "which comes from verified clinical sources. "
    "Do not add any medical facts, tests, or recommendations that are "
    "not explicitly stated in the context, even if you know them to be "
    "generally true or standard practice. "
    "If the context does not contain enough information to fully answer "
    "the question, say so explicitly rather than filling the gap with "
    "outside knowledge.\n"
    "Pay close attention to any numeric thresholds in red flags (e.g. 'more "
    "than 3 weeks', 'more than 3 days'). Before setting "
    "requires_urgent_attention, explicitly compare the patient's actual "
    "value from the question against each threshold in the context — do "
    "not rely on approximate impression. "
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information above and not prior knowledge, "
    "answer the question below.\n\n"
    "Question: {query_str}\n\n"
    "Respond with ONLY a single JSON object (no markdown fences, no "
    "extra text before or after), in exactly this shape:\n"
    "Respond with a valid JSON object containing exactly three keys: "
    '"answer" (a string with your written answer, grounded only in the '
    'context), "red_flags_identified" (an array of strings, each one a '
    "red flag from the context that applies to this case), and "
    '"requires_urgent_attention" (true or false: true if any identified '
    "red flag indicates urgency per the context, otherwise false). "
    "Use single curly braces, standard JSON syntax, no markdown fences, "
    "no text before or after the JSON object.\n"
    "If no red flags from the context apply, return an empty list and "
    "false. Do not invent red flags that are not present in the context."
)

def _confidence_info(min_score: float | None) -> dict:
    """
    Convert a similarity score into both a short label and a longer,
    actionable message for the GP, so they can judge at a glance how
    much to trust the grounding behind an answer.

    Deliberately conservative: intended for use with the LOWEST score
    among the chunks that grounded the answer, not the highest or an
    average — since the answer draws on all retrieved chunks together,
    the weakest one represents the real risk in the answer's grounding.

    Thresholds are approximate starting points based on typical cosine
    similarity ranges for this embedding model; adjust based on
    observed scores once more real queries have been tested.

    Returns a dict: {"label": str, "message": str}
    """
    if min_score is None:
        return {
            "label": "unknown",
            "message": (
                "No similarity score was available for this answer. "
                "Treat with caution and verify independently."
            ),
        }
    if min_score >= 0.65:
        return {
            "label": "strong match",
            "message": (
                "This answer is strongly grounded in the knowledge base "
                "for this case."
            ),
        }
    if min_score >= 0.55:
        return {
            "label": "moderate match",
            "message": (
                "This answer is only moderately grounded in the knowledge "
                "base — use caution and consider verifying key details "
                "independently."
            ),
        }
    return {
        "label": "weak match",
        "message": (
            "This answer has weak grounding in the knowledge base for "
            "this case — the retrieved information may not closely match "
            "the patient's presentation. Verify independently before "
            "relying on this answer."
        ),
    }


def ask_structured(index, question: str) -> dict:
    """
    Like ask(), but returns a structured dict instead of prose, including
    red-flag detection grounded in the knowledge base. This is the
    intended entry point for main.py / the frontend, since chatbot.py's
    red_flags / requires_urgent_attention fields were removed (that
    responsibility now lives here, where answers are grounded in
    verified sources rather than the chat LLM's own judgement).

    Returns a dict shaped like:
    {
        "answer": str,
        "red_flags_identified": list[str],
        "requires_urgent_attention": bool,
        "sources": list[str],
        "parse_error": bool  # True if the model's output couldn't be
                              # parsed as JSON — caller should treat this
                              # as "answer unavailable", not "no red flags"
    }
    """
    print("Sending structured query to AWS...", flush=True)

    similarity_processor = SimilarityPostprocessor(similarity_cutoff=0.72)

    query_engine = index.as_query_engine(
        text_qa_template=STRUCTURED_QA_PROMPT,
        node_postprocessors=[similarity_processor]
    )
    response = query_engine.query(question)
    sources = [node.node.get_text() for node in response.source_nodes]

    # Collect similarity scores from retrieved nodes, then use the
    # WEAKEST one for a conservative confidence label — see
    # _confidence_label()'s docstring for why weakest, not best/average.
    scores = [
        node.score for node in response.source_nodes
        if node.score is not None
    ]

    min_score = min(scores) if scores else None
    confidence_info = _confidence_info(min_score)

    raw = str(response).strip()
    # Models sometimes wrap JSON in markdown fences despite instructions
    # not to — strip those defensively rather than failing on them.
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
        return {
            "answer": parsed.get("answer", ""),
            "red_flags_identified": parsed.get("red_flags_identified", []),
            # Deterministic, not model-judged: if the model identified
            # ANY red flag from the context, treat it as urgent. Testing
            # showed both Groq and Bedrock models could correctly extract
            # a matching red flag yet still separately report
            # requires_urgent_attention=false — an unreliable, unsafe
            # inconsistency. Deriving this boolean directly from the
            # extracted list removes that failure mode entirely.
            "requires_urgent_attention": bool(
                parsed.get("red_flags_identified", [])
            ),
            "confidence": confidence_info["label"],
            "confidence_message": confidence_info["message"],
            "sources": sources,
            "parse_error": False,
        }
    except json.JSONDecodeError:
        # IMPORTANT: do not silently treat a parse failure as "no red
        # flags" — that would be unsafe. Surface it as an error instead,
        # so the caller (main.py) can decide how to handle it (e.g. show
        # the raw text, retry, or flag for manual review).
        return {
            "answer": raw,
            "red_flags_identified": [],
            "requires_urgent_attention": False,
            "confidence": confidence_info["label"],
            "confidence_message": confidence_info["message"],
            "sources": sources,
            "parse_error": True,
        }


# Quick manual test — only runs if you execute this file directly,
# not when it's imported by another module.


if __name__ == "__main__":
    idx = load_index()

    # Test 1: plain question (as before)
    answer, sources = ask(
        idx,
        "A patient has had a joint pain for 3 months, what should I check?",
        return_sources=True,
    )
    print("\nAnswer:\n", answer)
    print("\nSources used:")
    for s in sources:
        print("-", s[:200], "...")

    # Test 2: simulating a ConsultationSummary dict from chatbot.py
    example_summary = {
        "session_id": "test-session",
        "reason_for_visit": "joint pain",
        "symptoms": ["stiffness"],
        "symptom_location": None,
        "onset": "gradual",
        "duration": "1 day",
        "severity": "mild",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "unknown", "items": []},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": None,
    }
    query = build_query_from_consultation_summary(example_summary)
    print("\n\n--- Consultation summary test ---")
    print("Generated query:\n", query)
    answer2, sources2 = ask(idx, query, return_sources=True)
    print("\nAnswer:\n", answer2)

    # Test 3: structured version, showing red-flag detection & confidence metadata
    print("\n\n--- Structured response test ---")
    structured = ask_structured(idx, query)
    print("Answer:", structured["answer"])
    print("Red flags identified:", structured["red_flags_identified"])
    print("Requires urgent attention:", structured["requires_urgent_attention"])
    print("Confidence rating:", structured["confidence"])
    print("Confidence message:", structured["confidence_message"])
    print("Parse error:", structured["parse_error"])
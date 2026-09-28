"""

knowledge_rag.py — Retrieval-augmented generation module for the GP Support System.

Exposes:
- build_index(db): sets up the knowledge base index and persists chunks to Supabase pgvector
- update_index(db): appends new knowledge base files without rebuilding existing chunks
- load_index(): loads existing vector store from Supabase without rebuilding
- ask_structured(index, question): queries index and returns grounded JSON dict


To query an existing index:
    from app.services.knowledge_rag import load_index, ask_structured
    index = load_index()
    result = ask_structured(index, "Clinical guidance for a persistent cough")
"""

import json
import os
import re
from pathlib import Path
from sqlalchemy import text
from llama_index.core.schema import MetadataMode
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core import PromptTemplate
#from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import get_response_synthesizer
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
    Returns the index object, which you pass into ask_structured().
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


def update_index(db):
    """Append new top-level knowledge_base files and return a queryable index.

    File names already stored in PostgreSQL are skipped, including files from
    older build_index runs. Editing or deleting an existing file does not change
    its stored chunks; use build_index explicitly for a full replacement.
    Run with a dedicated session, e.g. ``with SessionLocal() as db``.
    """
    folder = Path(KNOWLEDGE_BASE_DIR).resolve()
    if not folder.is_dir():
        raise ValueError(f"Knowledge base directory does not exist: {folder}")
    files = sorted(p for p in folder.iterdir() if p.is_file() and not p.name.startswith("."))

    _configure_models()
    vector_store = _get_vector_store()
    index = VectorStoreIndex.from_vector_store(vector_store)

    # Serialize incremental updaters across processes. A separate transaction
    # keeps the lock alive while PGVectorStore commits each file independently.
    with db.get_bind().begin() as connection:
        connection.execute(text("SELECT pg_advisory_xact_lock(724193801)"))
        exists = connection.execute(
            text("SELECT to_regclass('public.data_rag_chunks')")
        ).scalar()
        indexed = set()
        if exists:
            rows = connection.execute(text(
                "SELECT DISTINCT metadata_->>'file_name' FROM public.data_rag_chunks"
            ))
            indexed = {row[0] for row in rows if row[0]}

        added = 0
        for path in files:
            if path.name in indexed:
                continue
            documents = SimpleDirectoryReader(
                input_files=[str(path)], raise_on_error=True
            ).load_data()
            nodes = Settings.text_splitter.get_nodes_from_documents(documents)
            if not nodes:
                print(f"Skipping empty document: {path.name}", flush=True)
                continue
            # Keep source identity in every chunk for subsequent update runs.
            for node in nodes:
                node.metadata["file_name"] = path.name
            embeddings = Settings.embed_model.get_text_embedding_batch(
                [node.get_content(metadata_mode=MetadataMode.EMBED) for node in nodes]
            )
            for node, embedding in zip(nodes, embeddings):
                node.embedding = embedding
            # PGVectorStore.add commits ALL chunks for this file in one transaction.
            # Failed parsing/embedding/insertion leaves this file retryable.
            vector_store.add(nodes)
            indexed.add(path.name)
            added += 1
            print(f"Indexed {path.name} ({len(nodes)} chunks)", flush=True)

    print(f"Index updated: {added} new file(s).", flush=True)
    return index


def build_query_from_consultation_summary(summary: dict) -> str:
    """
    Build a query preserving the patient context needed for retrieval and synthesis.
    Missing details are omitted; unknown allergies are not treated as absent.
    """
    terms = []

    if summary.get("reason_for_visit"):
        terms.append(summary['reason_for_visit'])

    if summary.get("symptoms"):
        # Append symptoms (avoiding redundant duplicates if reason_for_visit matches)
        for symptom in summary['symptoms']:
            if symptom.lower() not in [t.lower() for t in terms]:
                terms.append(symptom)

    if summary.get("symptom_location"):
        location = summary['symptom_location']
        if location.lower() not in [t.lower() for t in terms]:
            terms.append(location)

    relevant_history = summary.get("relevant_history") or []

    if relevant_history:
        terms.append(
            f"Relevant history: {', '.join(relevant_history)}"
        )

    # Preserve explicitly reported absence as well as confirmed items.
    for field_name, label in (
        ("medical_history", "Medical history"),
        ("current_medications", "Current medications"),
    ):
        field = summary.get(field_name) or {}
        if field.get("status") == "confirmed" and field.get("items"):
            terms.extend(field['items'])
        elif field.get("status") == "confirmed_none":
            terms.append(f"{label}: patient reports none")

    # Preserve context that may exist only in dedicated summary fields.
    for field_name, label in (
        ("onset", "Onset"),
        ("duration", "Duration"),
        ("severity", "Severity"),
        ("additional_concerns", "Additional concerns"),
    ):
        value = summary.get(field_name)
        if value and value.strip():
            terms.append(f"{label}: {value.strip()}")

    allergies = summary.get("allergies") or {}
    if allergies.get("status") == "confirmed" and allergies.get("items"):
        terms.append(f"Reported allergies: {', '.join(allergies['items'])}")
    elif allergies.get("status") == "confirmed_none":
        terms.append("Allergies: patient reports none")

    # Fallback if summary dictionary fields are empty
    if not terms:
        return "Clinical guidance and management for patient presentation."

    clinical_presentation = ", ".join(terms)
    return f"Clinical guidance, and diagnostic criteria for: {clinical_presentation}."



# Return a structured answer grounded only in the retrieved context.
STRUCTURED_QA_PROMPT = PromptTemplate(
    "You are a clinical documentation assistant helping a GP. "

    "All output must be written in English. "
    "Write the answer in English, regardless of the language "
    "originally used by the patient. "

    "You must answer using ONLY the context information below, "
    "Do not identify or list red flags, assess urgency, or label the case as urgent. "
    "Do not include urgent-care or emergency instructions in the answer. "
    "which comes from verified clinical sources. "
    "Do not add any medical facts, tests, or recommendations that are "
    "not explicitly stated in the context, even if you know them to be "
    "generally true or standard practice. "
    "If the context does not contain enough information to fully answer "
    "the question, say so explicitly rather than filling the gap with "
    "outside knowledge.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information above and not prior knowledge, "
    "answer the question below.\n\n"
    "Question: {query_str}\n\n"
    "Respond with ONLY a single JSON object (no markdown fences, no "
    "extra text before or after), in exactly this shape:\n"
    "Respond with a valid JSON object containing exactly one key: "
    '"answer" (a string with your written answer, grounded only in the '
    'context)."'
    "Use single curly braces, standard JSON syntax, no markdown fences, "
    "no text before or after the JSON object.\n"
)

FOLLOW_UP_TOPICS_PROMPT = PromptTemplate(
    "You are supporting a GP pre-consultation assistant. "

    "Use ONLY the clinical context retrieved from the verified knowledge base. "
    "Do not use outside medical knowledge. "

    "The patient's currently known presentation is provided in the question. "

    "Your task is to identify clinically relevant HISTORY DETAILS that would "
    "be useful to clarify by asking the patient another question. "

    "Do NOT diagnose the patient. "
    "Do NOT recommend treatment, medication, tests, or management. "
    "Do NOT assess urgency. "
    "Do NOT provide medical advice. "

    "Do NOT suggest asking for information that is already clearly stated "
    "in the patient's known presentation. "

    "Focus on specific missing details that could help the GP understand "
    "the current presentation better. "

    "Return at most 4 short follow-up TOPICS. "
    "Return topics, NOT fully written patient questions. "

    "Examples of good topics: "
    "\"contact lens use\", "
    "\"recent eye trauma\", "
    "\"light sensitivity\", "
    "\"change in vision\". "

    "If the retrieved clinical context does not support any useful "
    "follow-up topics, return an empty list. "

    "Respond with ONLY valid JSON in exactly this shape:\n"
    '{"follow_up_topics": ["topic 1", "topic 2"]}\n'

    "No markdown fences. No explanation. No additional keys.\n\n"

    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"

    "Known patient presentation:\n"
    "{query_str}\n"
)


def suggest_follow_up_topics(
    index,
    question: str
) -> dict:
    """
    Retrieve clinically relevant knowledge and identify useful
    unanswered history topics for the live chatbot.

    This does NOT generate the patient-facing question.
    The chat LLM will later turn one topic into a natural question
    in the patient's preferred language.
    """

    similarity_processor = SimilarityPostprocessor(
        similarity_cutoff=0.67
    )

    retriever = index.as_retriever(
        similarity_top_k=3
    )

    # 1. Retrieve relevant clinical chunks
    retrieved_nodes = retriever.retrieve(question)

    # 2. Remove weak matches
    processed_nodes = similarity_processor.postprocess_nodes(
        retrieved_nodes,
        query_str=question
    )

    # 3. No relevant clinical knowledge found
    if not processed_nodes:
        return {
            "follow_up_topics": [],
            "sources": [],
            "parse_error": False,
        }

    # 4. Ask the RAG model for useful follow-up topics
    synth = get_response_synthesizer(
        text_qa_template=FOLLOW_UP_TOPICS_PROMPT
    )

    response = synth.synthesize(
        query=question,
        nodes=processed_nodes
    )

    raw = str(response).strip()

    # Defensive cleanup if the model still returns markdown
    if raw.startswith("```"):
        raw = raw.strip("`")

        if raw.startswith("json"):
            raw = raw[4:]

        raw = raw.strip()

    sources = [
        node.node.get_text()
        for node in response.source_nodes
    ]

    try:
        parsed = json.loads(raw)

        topics = parsed.get(
            "follow_up_topics",
            []
        )

        if not isinstance(topics, list):
            topics = []

        # Keep only clean strings and limit the number returned
        topics = [
            topic.strip()
            for topic in topics
            if isinstance(topic, str) and topic.strip()
        ][:4]

        return {
            "follow_up_topics": topics,
            "sources": sources,
            "parse_error": False,
        }

    except json.JSONDecodeError:
        return {
            "follow_up_topics": [],
            "sources": sources,
            "parse_error": True,
        }


def build_follow_up_query(
    current_state: dict,
    patient_profile: dict | None = None
) -> str:
    """
    Build a concise clinical presentation for live RAG follow-up retrieval.

    The query describes what is already known so RAG can identify
    useful missing history topics without repeating answered questions.
    """

    patient_profile = patient_profile or {}

    parts = []

    age = patient_profile.get("age")
    if age is not None:
        parts.append(f"Age: {age}")

    reason = current_state.get("reason_for_visit")
    if reason:
        parts.append(f"Reason for visit: {reason}")

    symptoms = current_state.get("symptoms") or []
    if symptoms:
        parts.append(
            f"Known symptoms: {', '.join(symptoms)}"
        )

    location = current_state.get("symptom_location")
    if location:
        parts.append(
            f"Symptom location: {location}"
        )

    onset = current_state.get("onset")
    if onset:
        parts.append(
            f"Onset: {onset}"
        )

    duration = current_state.get("duration")
    if duration:
        parts.append(
            f"Duration: {duration}"
        )

    severity = current_state.get("severity")
    if severity:
        parts.append(
            f"Severity: {severity}"
        )

    relevant_history = current_state.get("relevant_history") or []
    if relevant_history:
        parts.append(f"Relevant history: {', '.join(relevant_history)}")

    additional_concerns = current_state.get("additional_concerns")
    if additional_concerns and additional_concerns.strip():
        parts.append(f"Additional concerns: {additional_concerns.strip()}")

    # Prefer information explicitly established during this consultation.
    medical_history = current_state.get("medical_history") or {}

    if medical_history.get("status") == "confirmed":
        items = medical_history.get("items") or []

        if items:
            parts.append(
                f"Confirmed medical history: {', '.join(items)}"
            )

    elif medical_history.get("status") == "confirmed_none":
        parts.append("Confirmed medical history: none")

    elif (
        medical_history.get("status", "unknown") == "unknown"
        and patient_profile.get("medical_history")
    ):
        parts.append(
            f"Previously recorded medical history: "
            f"{patient_profile['medical_history']}"
        )

    medications = current_state.get("current_medications") or {}

    if medications.get("status") == "confirmed":
        items = medications.get("items") or []

        if items:
            parts.append(
                f"Confirmed current medications: {', '.join(items)}"
            )

    elif medications.get("status") == "confirmed_none":
        parts.append("Confirmed current medications: none")

    elif (
        medications.get("status", "unknown") == "unknown"
        and patient_profile.get("medications")
    ):
        parts.append(
            "Previously recorded medications: "
            + ", ".join(patient_profile["medications"])
        )

    allergies = current_state.get("allergies") or {}

    if allergies.get("status") == "confirmed":
        items = allergies.get("items") or []

        if items:
            parts.append(
                f"Confirmed allergies: {', '.join(items)}"
            )

    elif allergies.get("status") == "confirmed_none":
        parts.append(
            "Confirmed allergies: none"
        )

    elif (
        allergies.get("status", "unknown") == "unknown"
        and patient_profile.get("allergies")
    ):
        parts.append(
            "Previously recorded allergies: "
            + ", ".join(patient_profile["allergies"])
        )

    return "\n".join(parts)



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
    if min_score >= 0.72:
        return {
            "label": "strong match",
            "message": (
                "This answer is strongly grounded in the knowledge base "
                "for this case."
            ),
        }
    if min_score >= 0.69:
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


def _source_links(source_nodes) -> list[str]:
    """Read unique footer URLs from the local documents grounding this answer.

    Resolve by file name rather than stored absolute path so an existing index
    also works when the repository moves between machines. Only SOURCES footer
    URLs are returned; links elsewhere in the clinical text are not citations.
    """
    folder = Path(KNOWLEDGE_BASE_DIR).resolve()
    visited = set()
    links = []
    for source in source_nodes:
        metadata = source.node.metadata
        name = metadata.get("file_name")
        if not name:
            name = str(metadata.get("file_path", "")).replace("\\", "/").rsplit("/", 1)[-1]
        if not isinstance(name, str) or not name or "/" in name or "\\" in name:
            continue
        path = (folder / name).resolve()
        if not path.is_relative_to(folder) or path in visited or path.suffix.lower() != ".txt":
            continue
        visited.add(path)
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            # Missing local source files must not prevent returning the answer.
            continue
        headings = list(re.finditer(r"(?im)^[ \t]*sources?[ \t]*:?[ \t]*$", content))
        if not headings:
            continue
        footer = content[headings[-1].end():]
        for url in re.findall(r"https?://[^\s<>\"']+", footer):
            url = url.rstrip(".,;)]}")
            if url not in links:
                links.append(url)
    return links


def ask_structured(index, question: str) -> dict:
    """
    Query the index and return a grounded answer with source passages,
    source links, retrieval confidence, and JSON parsing status.
    This is the entry point used by the consultation workflow.

    Returns a dict shaped like:
    {
        "answer": str,
        "sources": list[str],
        "link": list[str],  # unique source URLs from the retrieved documents
        "parse_error": bool  # True if the model's output couldn't be
                              # parsed as JSON — caller should treat this
                              # as "answer unavailable", not "no red flags"
    }
    """
    print("Sending structured query to AWS...", flush=True)

    similarity_processor = SimilarityPostprocessor(similarity_cutoff=0.67)

    # 1. Retrieve candidates from Supabase pgvector
    retriever = index.as_retriever(similarity_top_k=2)
    retrieved_nodes = retriever.retrieve(question)

    # --- ADD THIS PRINT STATEMENT TO DEBUG SCORES ---
    print("\n--- RAW SCORES ---")
    for node in retrieved_nodes:
        print(f"Score: {node.score:.4f} | Source: {node.node.get_text()[:80]}...")
    print("------------------\n")

    # 2. Filter using cutoff (must pass query_str)
    processed_nodes = similarity_processor.postprocess_nodes(
        retrieved_nodes,
        query_str=question
    )

    # 3. Short-circuit if nothing cleared the cutoff
    if not processed_nodes:
        return {
            "answer": "The knowledge base does not contain verified clinical guidance for this presentation.",
            "confidence": "weak match",
            "confidence_message": "No relevant clinical guidelines matched the search criteria.",
            "sources": [],
            "link": [],
            "parse_error": False,
        }

    # 4. Pass pre-filtered nodes directly into AWS Bedrock synthesis
    synth = get_response_synthesizer(text_qa_template=STRUCTURED_QA_PROMPT)
    response = synth.synthesize(query=question, nodes=processed_nodes)

    sources = [node.node.get_text() for node in response.source_nodes]
    links = _source_links(response.source_nodes)

    # Collect similarity scores from processed nodes
    scores = [
        node.score for node in response.source_nodes
        if node.score is not None
    ]

    top_score = max(scores) if scores else None
    confidence_info = _confidence_info(top_score)

    raw = str(response).strip()

    # Strip markdown code blocks defensively
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
        return {
            "answer": parsed.get("answer", ""),
            "confidence": confidence_info["label"],
            "confidence_message": confidence_info["message"],
            "sources": sources,
            "link": links,
            "parse_error": False,
        }
    except json.JSONDecodeError:
        return {
            "answer": raw,
            "confidence": confidence_info["label"],
            "confidence_message": confidence_info["message"],
            "sources": sources,
            "link": links,
            "parse_error": True,
        }


# Quick manual test — only runs if you execute this file directly,
# not when it's imported by another module.


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage the knowledge base index")
    parser.add_argument("--update", action="store_true", help="Index only new knowledge base files")
    args = parser.parse_args()
    if args.update:
        with SessionLocal() as db:
            update_index(db)
        raise SystemExit(0)

    idx = load_index()

    # ==============================================================================
    # TEST 1: Acute Asthma Presentation (High Confidence & In-Scope)
    # Expected: Strong Match (>= 0.72)
    # ==============================================================================
    test_summary_1 = {
        "reason_for_visit": "shortness of breath and wheezing",
        "symptoms": ["wheezing", "coughing", "tight chest", "difficulty speaking full sentences"],
        "symptom_location": "chest",
        "onset": "2 hours ago",
        "duration": "2 hours",
        "severity": "severe",
        "medical_history": {"status": "confirmed", "items": ["asthma"]},
        "current_medications": {"status": "confirmed", "items": ["Salbutamol inhaler"]},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Inhaler isn't giving usual relief."
    }

    query_1 = build_query_from_consultation_summary(test_summary_1)
    print("\n--- TEST 1: Acute Asthma (High Confidence) ---")
    print("Generated Query:", query_1)
    res_1 = ask_structured(idx, query_1)
    print("\n--- OUTPUT ---")
    print("Answer:", res_1["answer"])
    print("Confidence Rating:", res_1["confidence"])
    print("Confidence Message:", res_1["confidence_message"])
    print("Sources Used:", res_1["sources"])
    print("Parse Error:", res_1["parse_error"])

'''
    # ==============================================================================
    # TEST 2: Severe Acute Ear Infection with High Fever (Pediatric / Red Flag)
    # Expected: Strong Match (>= 0.72)
    # ==============================================================================
    test_summary_2 = {
        "reason_for_visit": "severe ear pain and high fever in young child",
        "symptoms": ["intense right ear pain", "fever of 39.2°C (102.5°F)", "fluid discharge from ear", "extreme irritability"],
        "symptom_location": "right ear",
        "onset": "1 day ago",
        "duration": "24 hours",
        "severity": "severe",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed", "items": ["Children's Paracetamol"]},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Child is crying continuously and tugging at right ear."
    }

    query_2 = build_query_from_consultation_summary(test_summary_2)
    print("\n--- TEST 2: Severe Otitis Media with Fever & Discharge (High Confidence) ---")
    print("Generated Query:", query_2)
    res_2 = ask_structured(idx, query_2)
    print("\n--- OUTPUT ---")
    print("Answer:", res_2["answer"])
    print("Confidence Rating:", res_2["confidence"])
    print("Confidence Message:", res_2["confidence_message"])
    print("Sources Used:", res_2["sources"])
    print("Parse Error:", res_2["parse_error"])


    # ==============================================================================
    # TEST 3: Out-of-Scope Technical Query (Weak Match Short-Circuit)
    # Expected: Weak Match (< 0.67 Cutoff Fallback)
    # ==============================================================================
    test_summary_3 = {
        "reason_for_visit": "querying database vector search configuration",
        "symptoms": ["no physical symptoms"],
        "symptom_location": "none",
        "onset": "not applicable",
        "duration": "0 days",
        "severity": "none",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed_none", "items": []},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "How do I configure PGVector similarity threshold in Supabase?"
    }

    query_3 = build_query_from_consultation_summary(test_summary_3)
    print("\n--- TEST 3: Out-of-Scope Non-Clinical Query (Weak Match Fallback) ---")
    print("Generated Query:", query_3)
    res_3 = ask_structured(idx, query_3)
    print("\n--- OUTPUT ---")
    print("Answer:", res_3["answer"])
    print("Confidence Rating:", res_3["confidence"])
    print("Confidence Message:", res_3["confidence_message"])
    print("Sources Used:", res_3["sources"])
    print("Parse Error:", res_3["parse_error"])


    # ==============================================================================
    # TEST 4: Persistent Productive Cough & Sore Throat (Acute Bronchitis)
    # Expected: Strong Match (>= 0.72)
    # ==============================================================================
    test_summary_4 = {
        "reason_for_visit": "persistent cough and throat pain",
        "symptoms": ["coughing up clear mucus", "sore throat", "mild body aches", "low fatigue"],
        "symptom_location": "throat and chest",
        "onset": "4 days ago",
        "duration": "4 days",
        "severity": "moderate",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed", "items": ["Honey and Lemon tea"]},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Wants to know if antibiotics are needed."
    }

    query_4 = build_query_from_consultation_summary(test_summary_4)
    print("\n--- TEST 4: Acute Bronchitis / Cough Guidance (High Confidence) ---")
    print("Generated Query:", query_4)
    res_4 = ask_structured(idx, query_4)
    print("\n--- OUTPUT ---")
    print("Answer:", res_4["answer"])
    print("Confidence Rating:", res_4["confidence"])
    print("Confidence Message:", res_4["confidence_message"])
    print("Sources Used:", res_4["sources"])
    print("Parse Error:", res_4["parse_error"])


    # ==============================================================================
    # TEST 5: Vague Systemic Symptoms (Ambiguous Query / Low Density)
    # Expected: Weak Match (< 0.67 Cutoff Fallback)
    # ==============================================================================
    test_summary_5 = {
        "reason_for_visit": "feeling unwell",
        "symptoms": ["mild fatigue", "feeling slightly off", "occasional general discomfort"],
        "symptom_location": "body",
        "onset": "a few days ago",
        "duration": "3 days",
        "severity": "mild",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed_none", "items": []},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Not sure what is wrong."
    }

    query_5 = build_query_from_consultation_summary(test_summary_5)
    print("\n--- TEST 5: Vague Systemic Symptoms (Ambiguous Fallback) ---")
    print("Generated Query:", query_5)
    res_5 = ask_structured(idx, query_5)
    print("\n--- OUTPUT ---")
    print("Answer:", res_5["answer"])
    print("Confidence Rating:", res_5["confidence"])
    print("Confidence Message:", res_5["confidence_message"])
    print("Sources Used:", res_5["sources"])
    print("Parse Error:", res_5["parse_error"])
    # ==============================================================================
    # TEST 6: Ear Fullness & Muffled Hearing (Borderline Scenario) ---
    # ==============================================================================
    test_summary_6 = {
        "reason_for_visit": "ear discomfort and muffling",
        "symptoms": ["feeling of fullness in right ear", "muffled hearing", "slight itching"],
        "symptom_location": "right ear",
        "onset": "5 days ago",
        "duration": "5 days",
        "severity": "mild",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed_none", "items": []},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "No fever, no severe fluid drainage."
    }

    query_6 = build_query_from_consultation_summary(test_summary_6)
    print("\n--- TEST 6: Ear Fullness & Muffled Hearing (Borderline Scenario) ---")
    print("Generated Query:", query_6)
    res_6 = ask_structured(idx, query_6)
    print("\n--- OUTPUT ---")
    print("Answer:", res_6["answer"])
    print("Confidence Rating:", res_6["confidence"])
    print("Confidence Message:", res_6["confidence_message"])
    print("Sources Used:", res_6["sources"])
    print("Parse Error:", res_6["parse_error"])

    # ==============================================================================
    # TEST 7: Acute High Fever & Severe Sore Throat (Strep Throat / Tonsillitis)
    # Expected: Strong Match (>= 0.72)
    # ==============================================================================
    test_summary_7 = {
        "reason_for_visit": "severe sore throat and difficulty swallowing",
        "symptoms": ["intense throat pain", "high fever", "swollen tonsils with white spots", "painful swallowing"],
        "symptom_location": "throat",
        "onset": "2 days ago",
        "duration": "2 days",
        "severity": "severe",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed", "items": ["Paracetamol 500mg"]},
        "allergies": {"status": "confirmed", "items": ["Penicillin"]},
        "additional_concerns": "Unable to swallow solid food, concerned about bacterial infection."
    }

    query_7 = build_query_from_consultation_summary(test_summary_7)
    print("\n--- TEST 7: Severe Sore Throat & High Fever (High Confidence) ---")
    print("Generated Query:", query_7)
    res_7 = ask_structured(idx, query_7)
    print("\n--- OUTPUT ---")
    print("Answer:", res_7["answer"])
    print("Confidence Rating:", res_7["confidence"])
    print("Confidence Message:", res_7["confidence_message"])
    print("Sources Used:", res_7["sources"])
    print("Parse Error:", res_7["parse_error"])


    # ==============================================================================
    # TEST 8: Sudden Onset Chest Pain & Shortness of Breath (Red Flag Scenario)
    # Expected: Strong Match (>= 0.72) with Urgent Attention Triggered
    # ==============================================================================
    test_summary_8 = {
        "reason_for_visit": "chest tightness and radiating arm pain",
        "symptoms": ["crushing chest pressure", "shortness of breath", "cold sweats", "pain radiating to left arm"],
        "symptom_location": "chest and left arm",
        "onset": "30 minutes ago",
        "duration": "30 minutes",
        "severity": "severe",
        "medical_history": {"status": "confirmed", "items": ["hypertension", "type 2 diabetes"]},
        "current_medications": {"status": "confirmed", "items": ["Metformin", "Amlodipine"]},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Feels like an elephant is sitting on the chest."
    }

    query_8 = build_query_from_consultation_summary(test_summary_8)
    print("\n--- TEST 8: Acute Chest Pain & Radiating Pain (Urgent Red Flag) ---")
    print("Generated Query:", query_8)
    res_8 = ask_structured(idx, query_8)
    print("\n--- OUTPUT ---")
    print("Answer:", res_8["answer"])
    print("Confidence Rating:", res_8["confidence"])
    print("Confidence Message:", res_8["confidence_message"])
    print("Sources Used:", res_8["sources"])
    print("Parse Error:", res_8["parse_error"])


    # ==============================================================================
    # TEST 9: Mild Seasonal Allergies & Sneezing (Moderate Match)
    # Expected: Moderate Match (0.69 - 0.719)
    # ==============================================================================
    test_summary_9 = {
        "reason_for_visit": "itchy eyes and frequent sneezing",
        "symptoms": ["watery itchy eyes", "clear runny nose", "frequent sneezing", "mild nasal congestion"],
        "symptom_location": "eyes and nose",
        "onset": "2 weeks ago",
        "duration": "14 days",
        "severity": "mild",
        "medical_history": {"status": "confirmed", "items": ["allergic rhinitis"]},
        "current_medications": {"status": "confirmed_none", "items": []},
        "allergies": {"status": "confirmed", "items": ["Pollen"]},
        "additional_concerns": "Symptoms get worse when spending time outdoors."
    }

    query_9 = build_query_from_consultation_summary(test_summary_9)
    print("\n--- TEST 9: Seasonal Allergies & Rhinitis (Moderate Match) ---")
    print("Generated Query:", query_9)
    res_9 = ask_structured(idx, query_9)
    print("\n--- OUTPUT ---")
    print("Answer:", res_9["answer"])
    print("Confidence Rating:", res_9["confidence"])
    print("Confidence Message:", res_9["confidence_message"])
    print("Sources Used:", res_9["sources"])
    print("Parse Error:", res_9["parse_error"])


    # ==============================================================================
    # TEST 10: Chronic Lower Back Pain Without Neurological Deficit (Borderline)
    # Expected: Borderline Match (0.67 - 0.689)
    # ==============================================================================
    test_summary_10 = {
        "reason_for_visit": "dull lower back ache",
        "symptoms": ["stiffness in lower back", "dull ache after sitting", "no numbness or tingling"],
        "symptom_location": "lumbar spine",
        "onset": "3 weeks ago",
        "duration": "21 days",
        "severity": "mild",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed", "items": ["Ibuprofen 200mg as needed"]},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "No bowel or bladder dysfunction, no leg weakness."
    }

    query_10 = build_query_from_consultation_summary(test_summary_10)
    print("\n--- TEST 10: Chronic Lower Back Pain (Borderline Scenario) ---")
    print("Generated Query:", query_10)
    res_10 = ask_structured(idx, query_10)
    print("\n--- OUTPUT ---")
    print("Answer:", res_10["answer"])
    print("Confidence Rating:", res_10["confidence"])
    print("Confidence Message:", res_10["confidence_message"])
    print("Sources Used:", res_10["sources"])
    print("Parse Error:", res_10["parse_error"])


    # ==============================================================================
    # TEST 11: Non-Clinical Administrative / Prescription Request Query
    # Expected: Weak Match (< 0.67 Cutoff Short-Circuit)
    # ==============================================================================
    test_summary_11 = {
        "reason_for_visit": "repeat prescription request",
        "symptoms": ["no active symptoms"],
        "symptom_location": "none",
        "onset": "not applicable",
        "duration": "0 days",
        "severity": "none",
        "medical_history": {"status": "confirmed", "items": ["hypothyroidism"]},
        "current_medications": {"status": "confirmed", "items": ["Levothyroxine 50mcg"]},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Needs a medical certificate for work exemption and refill."
    }

    query_11 = build_query_from_consultation_summary(test_summary_11)
    print("\n--- TEST 11: Prescription Refill & Admin Request (Weak Match Fallback) ---")
    print("Generated Query:", query_11)
    res_11 = ask_structured(idx, query_11)
    print("\n--- OUTPUT ---")
    print("Answer:", res_11["answer"])
    print("Confidence Rating:", res_11["confidence"])
    print("Confidence Message:", res_11["confidence_message"])
    print("Sources Used:", res_11["sources"])
    print("Parse Error:", res_11["parse_error"])


    # ==============================================================================
    # TEST 12: Acute Gastroenteritis / Vomiting & Diarrhea
    # Expected: Strong Match (>= 0.72)
    # ==============================================================================
    test_summary_12 = {
        "reason_for_visit": "nausea, vomiting, and watery diarrhea",
        "symptoms": ["frequent watery stool", "stomach cramping", "low-grade fever", "mild dizziness when standing"],
        "symptom_location": "abdomen",
        "onset": "24 hours ago",
        "duration": "1 day",
        "severity": "moderate",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed", "items": ["Oral Rehydration Salts"]},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "No blood in stool, keeping small sips of water down."
    }

    query_12 = build_query_from_consultation_summary(test_summary_12)
    print("\n--- TEST 12: Acute Gastroenteritis (Moderate / High Confidence) ---")
    print("Generated Query:", query_12)
    res_12 = ask_structured(idx, query_12)
    print("\n--- OUTPUT ---")
    print("Answer:", res_12["answer"])
    print("Confidence Rating:", res_12["confidence"])
    print("Confidence Message:", res_12["confidence_message"])
    print("Sources Used:", res_12["sources"])
    print("Parse Error:", res_12["parse_error"])


    # ==============================================================================
    # TEST 13: Unilateral Calf Swelling & Pain (Deep Vein Thrombosis Red Flag)
    # Expected: Strong Match (>= 0.72) with Red Flag Extraction
    # ==============================================================================
    test_summary_13 = {
        "reason_for_visit": "swollen and painful right calf",
        "symptoms": ["unilateral calf swelling", "warmth over right leg", "tenderness when walking"],
        "symptom_location": "right lower leg",
        "onset": "1 day ago",
        "duration": "1 day",
        "severity": "moderate",
        "medical_history": {"status": "confirmed", "items": ["recent long-haul flight 3 days ago"]},
        "current_medications": {"status": "confirmed_none", "items": []},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Leg feels significantly larger and warmer than the left leg."
    }

    query_13 = build_query_from_consultation_summary(test_summary_13)
    print("\n--- TEST 13: Unilateral Calf Swelling & Warmth (DVT Red Flag) ---")
    print("Generated Query:", query_13)
    res_13 = ask_structured(idx, query_13)
    print("\n--- OUTPUT ---")
    print("Answer:", res_13["answer"])
    print("Confidence Rating:", res_13["confidence"])
    print("Confidence Message:", res_13["confidence_message"])
    print("Sources Used:", res_13["sources"])
    print("Parse Error:", res_13["parse_error"])


    # ==============================================================================
    # TEST 14: Non-Specific Headaches & Eyestrain (Out-of-Scope / Weak Match)
    # Expected: Weak Match (< 0.67 Cutoff Short-Circuit)
    # ==============================================================================
    test_summary_14 = {
        "reason_for_visit": "occasional mild tension headache",
        "symptoms": ["tight band around head", "eyestrain after screen work", "no visual aura", "no vomiting"],
        "symptom_location": "forehead and temples",
        "onset": "1 week ago",
        "duration": "7 days",
        "severity": "mild",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed_none", "items": []},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Works 10 hours a day in front of a computer monitor."
    }

    query_14 = build_query_from_consultation_summary(test_summary_14)
    print("\n--- TEST 14: Tension Headache / Screen Eyestrain (Weak Match Fallback) ---")
    print("Generated Query:", query_14)
    res_14 = ask_structured(idx, query_14)
    print("\n--- OUTPUT ---")
    print("Answer:", res_14["answer"])
    print("Confidence Rating:", res_14["confidence"])
    print("Confidence Message:", res_14["confidence_message"])
    print("Sources Used:", res_14["sources"])
    print("Parse Error:", res_14["parse_error"])

    # ==============================================================================
    # TEST 15: Acute Dysuria & Frequency (Uncomplicated Urinary Tract Infection)
    # Expected: Strong / Moderate Match
    # ==============================================================================
    test_summary_15 = {
        "reason_for_visit": "painful urination and urinary frequency",
        "symptoms": ["burning sensation during urination", "frequent urge to urinate", "cloudy urine", "lower abdominal discomfort"],
        "symptom_location": "suprapubic / urinary tract",
        "onset": "2 days ago",
        "duration": "2 days",
        "severity": "moderate",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed_none", "items": []},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "No flank pain, no fever, no vaginal discharge."
    }

    query_15 = build_query_from_consultation_summary(test_summary_15)
    print("\n--- TEST 15: Dysuria & Urinary Frequency (UTI Presentation) ---")
    print("Generated Query:", query_15)
    res_15 = ask_structured(idx, query_15)
    print("\n--- OUTPUT ---")
    print("Answer:", res_15["answer"])
    print("Confidence Rating:", res_15["confidence"])
    print("Confidence Message:", res_15["confidence_message"])
    print("Sources Used:", res_15["sources"])
    print("Parse Error:", res_15["parse_error"])


    # ==============================================================================
    # TEST 16: High Pediatric Fever with Lethargy (Red Flag / Urgent Care)
    # Expected: Strong Match (>= 0.72) with Urgent Attention Triggered
    # ==============================================================================
    test_summary_16 = {
        "reason_for_visit": "high fever and extreme sleepiness in 18-month-old child",
        "symptoms": ["fever of 39.8°C (103.6°F)", "extreme lethargy", "poor fluid intake", "dry diapers for 10 hours"],
        "symptom_location": "systemic",
        "onset": "12 hours ago",
        "duration": "12 hours",
        "severity": "severe",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed", "items": ["Infant Paracetamol"]},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Child is unusually difficult to wake up and refusing liquids."
    }

    query_16 = build_query_from_consultation_summary(test_summary_16)
    print("\n--- TEST 16: Pediatric High Fever & Lethargy (Urgent Red Flag) ---")
    print("Generated Query:", query_16)
    res_16 = ask_structured(idx, query_16)
    print("\n--- OUTPUT ---")
    print("Answer:", res_16["answer"])
    print("Confidence Rating:", res_16["confidence"])
    print("Confidence Message:", res_16["confidence_message"])
    print("Sources Used:", res_16["sources"])
    print("Parse Error:", res_16["parse_error"])


    # ==============================================================================
    # TEST 17: Acute Spreading Skin Rash & Itching (Contact Dermatitis / Urticaria)
    # Expected: Moderate Match (0.69 - 0.719)
    # ==============================================================================
    test_summary_17 = {
        "reason_for_visit": "itchy red rash on forearms",
        "symptoms": ["red raised bumps", "intense itching", "mild localized swelling"],
        "symptom_location": "both forearms",
        "onset": "1 day ago",
        "duration": "24 hours",
        "severity": "mild",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed_none", "items": []},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Appeared after gardening outdoors. No facial swelling or airway tightness."
    }

    query_17 = build_query_from_consultation_summary(test_summary_17)
    print("\n--- TEST 17: Localized Itchy Skin Rash (Moderate Match) ---")
    print("Generated Query:", query_17)
    res_17 = ask_structured(idx, query_17)
    print("\n--- OUTPUT ---")
    print("Answer:", res_17["answer"])
    print("Confidence Rating:", res_17["confidence"])
    print("Confidence Message:", res_17["confidence_message"])
    print("Sources Used:", res_17["sources"])
    print("Parse Error:", res_17["parse_error"])


    # ==============================================================================
    # TEST 18: Acute Influenza-Like Illness with Sudden Onset
    # Expected: Strong Match (>= 0.72)
    # ==============================================================================
    test_summary_18 = {
        "reason_for_visit": "sudden onset high fever, severe muscle aches, and chills",
        "symptoms": ["fever 38.9°C", "severe body aches", "dry cough", "extreme exhaustion", "headache"],
        "symptom_location": "systemic and upper respiratory",
        "onset": "1 day ago",
        "duration": "1 day",
        "severity": "severe",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed", "items": ["Ibuprofen 400mg"]},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Hit all at once yesterday afternoon. Work colleagues recently had flu."
    }

    query_18 = build_query_from_consultation_summary(test_summary_18)
    print("\n--- TEST 18: Sudden Onset Influenza-Like Illness (High Confidence) ---")
    print("Generated Query:", query_18)
    res_18 = ask_structured(idx, query_18)
    print("\n--- OUTPUT ---")
    print("Answer:", res_18["answer"])
    print("Confidence Rating:", res_18["confidence"])
    print("Confidence Message:", res_18["confidence_message"])
    print("Sources Used:", res_18["sources"])
    print("Parse Error:", res_18["parse_error"])


    # ==============================================================================
    # TEST 19: Panic Attack / Acute Anxiety Presentation
    # Expected: Borderline or Weak Match (Depending on KB Mental Health Coverage)
    # ==============================================================================
    test_summary_19 = {
        "reason_for_visit": "sudden episode of racing heart and hyperventilation",
        "symptoms": ["rapid heartbeat", "shortness of breath", "tingling fingers", "feeling of impending doom"],
        "symptom_location": "chest and head",
        "onset": "2 hours ago",
        "duration": "20 minutes",
        "severity": "moderate",
        "medical_history": {"status": "confirmed", "items": ["generalized anxiety disorder"]},
        "current_medications": {"status": "confirmed_none", "items": []},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "ECG performed last month was normal. Episode resolved after resting."
    }

    query_19 = build_query_from_consultation_summary(test_summary_19)
    print("\n--- TEST 19: Palpitations & Hyperventilation (Anxiety / Borderline) ---")
    print("Generated Query:", query_19)
    res_19 = ask_structured(idx, query_19)
    print("\n--- OUTPUT ---")
    print("Answer:", res_19["answer"])
    print("Confidence Rating:", res_19["confidence"])
    print("Confidence Message:", res_19["confidence_message"])
    print("Sources Used:", res_19["sources"])
    print("Parse Error:", res_19["parse_error"])


    # ==============================================================================
    # TEST 20: General Lifestyle & Vitamin Supplement Advice (Out-of-Scope)
    # Expected: Weak Match (< 0.67 Cutoff Short-Circuit)
    # ==============================================================================
    test_summary_20 = {
        "reason_for_visit": "general dietary advice and vitamin recommendations",
        "symptoms": ["no physical complaints or symptoms"],
        "symptom_location": "none",
        "onset": "not applicable",
        "duration": "0 days",
        "severity": "none",
        "medical_history": {"status": "confirmed_none", "items": []},
        "current_medications": {"status": "confirmed_none", "items": []},
        "allergies": {"status": "confirmed_none", "items": []},
        "additional_concerns": "Wants to know if daily Vitamin C and Zinc will prevent winter illness."
    }

    query_20 = build_query_from_consultation_summary(test_summary_20)
    print("\n--- TEST 20: General Wellness & Vitamin Advice (Weak Match Fallback) ---")
    print("Generated Query:", query_20)
    res_20 = ask_structured(idx, query_20)
    print("\n--- OUTPUT ---")
    print("Answer:", res_20["answer"])
    print("Confidence Rating:", res_20["confidence"])
    print("Confidence Message:", res_20["confidence_message"])
    print("Sources Used:", res_20["sources"])
    print("Parse Error:", res_20["parse_error"])





'''

'''
## Use this one when rebuilding index, call on terminal:  python -m app.services.knowledge_rag
if __name__ == "__main__":
    from app.db.database import SessionLocal

    # 1. Open a database session
    db = SessionLocal()
    try:
        print("Rebuilding vector store index with all knowledge base files...")

        # 2. Re-embed and load all .txt files into PostgreSQL (including new ones)
        idx = build_index(db)

        print("\nIndex built successfully! Testing retrieval with a sample query...\n")

        # 3. Quick sanity test query
        test_query = "What are the red flags for meningococcal disease or measles?"
        structured = ask_structured(idx, test_query)

        print("Answer:", structured["answer"])
        print("Confidence:", structured["confidence"])

    finally:
        db.close()

'''


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

import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Path to the knowledge base folder, relative to this file's location.
# Using this instead of a hardcoded/relative-to-cwd path means it works
# no matter which folder you run the app from.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_BASE_DIR = os.path.join(_THIS_DIR, "knowledge_base")


def _configure_models():
    """Set the LLM and embedding model used by llama-index globally."""
    Settings.llm = Groq(
        model="openai/gpt-oss-20b",  # Groq deprecated llama-3.1-8b-instant; this is the current replacement
        api_key=os.environ["GROQ_API_KEY"],
    )
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )


def build_index():
    """
    Load documents from the knowledge base and build a searchable index.
    Call this once (e.g. at app startup) — it's the slow/expensive step.
    Returns the index object, which you pass into ask().
    """
    print("Configuring models (this downloads the embedding model on first run)...", flush=True)
    _configure_models()
    print("Loading documents from knowledge base...", flush=True)
    documents = SimpleDirectoryReader(KNOWLEDGE_BASE_DIR).load_data()
    if not documents:
        raise ValueError(
            f"No documents found in {KNOWLEDGE_BASE_DIR} — check the path "
            "and that .txt files exist there."
        )
    print(f"Loaded {len(documents)} document(s). Building index (embedding text)...", flush=True)
    index = VectorStoreIndex.from_documents(documents)
    print("Index built.", flush=True)
    return index


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
    print("Sending query to Groq...", flush=True)
    query_engine = index.as_query_engine()
    response = query_engine.query(question)

    if return_sources:
        sources = [node.node.get_text() for node in response.source_nodes]
        return str(response), sources

    return str(response)


# Quick manual test — only runs if you execute this file directly,
# not when it's imported by another module.
if __name__ == "__main__":
    idx = build_index()
    answer, sources = ask(
        idx,
        "A patient has had a cough for 4 weeks. What should I check?",
        return_sources=True,
    )
    print("\nAnswer:\n", answer)
    print("\nSources used:")
    for s in sources:
        print("-", s[:200], "...")
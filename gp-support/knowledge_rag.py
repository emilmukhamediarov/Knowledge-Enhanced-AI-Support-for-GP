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
    """Set the LLM and embedding model used by llama-index globally.
       this tells the script two things: which AI to use to generate the final answer
       which tool to use to "understand" text well enough to search it"""
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

    Opens every .txt file in your knowledge_base folder (right now, just your cold/flu file)
    Breaks it into smaller chunks (roughly by section)
    Converts each chunk into a list of numbers called a vector — think of it as a mathematical fingerprint of what that chunk of text is "about," which lets the computer compare how similar two pieces of text are
    Stores all these fingerprints together so they can be quickly searched later
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

     Takes your question ("A patient has had a cough for 4 weeks...")
     Turns the question itself into that same kind of number-fingerprint
     Compares it against all the stored chunk-fingerprints, and pulls out the ones that are mathematically most similar — i.e., most relevant to the question
     Sends those relevant chunks, plus your original question, to Groq's AI, essentially saying "using only this information, answer this question"
     Gets back a written answer, and also hands back exactly which chunks were used, so you can check whether the answer is actually grounded in your real content
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
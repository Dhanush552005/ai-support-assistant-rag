

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FAISS_DIR = PROJECT_ROOT / "faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 3

_embeddings: HuggingFaceEmbeddings | None = None
_retriever = None


def _get_retriever():
    """Lazy-init embeddings and similarity retriever (top_k=3)."""
    global _embeddings, _retriever
    if _retriever is not None:
        return _retriever

    if not FAISS_DIR.is_dir() or not (FAISS_DIR / "index.faiss").exists():
        raise FileNotFoundError(
            f"FAISS index not found at {FAISS_DIR}. Run: python src/ingest.py"
        )

    _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.load_local(
        str(FAISS_DIR),
        _embeddings,
        allow_dangerous_deserialization=True,
    )
    _retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )
    return _retriever


def get_relevant_docs(query: str) -> list[dict[str, Any]]:
    """
    Return the top 3 most similar chunks for a ticket query.

    Each item has:
      - content: chunk text
      - metadata: dict (includes 'source' file name from ingest)
    """
    retriever = _get_retriever()
    docs = retriever.invoke(query)
    return [
        {"content": d.page_content, "metadata": dict(d.metadata)}
        for d in docs
    ]


def print_results(results: list[dict[str, Any]], snippet_len: int = 400) -> None:
    """Print each hit with source and a readable content snippet."""
    line = "=" * 72
    print(line)
    print(f"RESULTS ({len(results)} chunks)")
    print(line)

    for i, hit in enumerate(results, start=1):
        meta = hit.get("metadata") or {}
        source = meta.get("source", "(unknown)")
        text = hit.get("content") or ""
        snippet = text.strip()
        if len(snippet) > snippet_len:
            snippet = snippet[: snippet_len].rstrip() + "…"

        print(f"\n[#{i}] SOURCE: {source}")
        print("-" * 72)
        print(snippet)
        print()


def main() -> None:
    example_query = "My food item arrived spoiled, can I get refund?"
    print(f"Query: {example_query}\n")
    results = get_relevant_docs(example_query)
    print_results(results)


if __name__ == "__main__":
    main()

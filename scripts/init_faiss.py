"""Utility script to bootstrap the FAISS index from a directory of PDFs."""

from pathlib import Path

from backend.rag.loader import load_pdf
from backend.rag.retriever import get_pipeline


def index_directory(directory: Path) -> None:
    pipeline = get_pipeline()
    for pdf in directory.glob("*.pdf"):
        with pdf.open("rb") as f:
            chunks = load_pdf(f.read(), pdf.name)
        document_id, count = pipeline.add_documents(chunks)
        print(f"Indexed {pdf.name} -> {document_id} ({count} chunks)")


if __name__ == "__main__":
    docs_dir = Path("data/docs")
    if not docs_dir.exists():
        raise SystemExit("data/docs directory not found")
    index_directory(docs_dir)

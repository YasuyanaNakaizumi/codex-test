from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Iterable, List

import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter

from backend.config import get_settings
from backend.models import DocumentChunk


def extract_text_from_pdf(pdf_path: Path) -> Iterable[DocumentChunk]:
    """Yield DocumentChunk entries per PDF page."""

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                continue
            yield DocumentChunk(
                page=page_number,
                content=text,
                source=pdf_path.name,
            )


def chunk_document(chunks: Iterable[DocumentChunk]) -> List[DocumentChunk]:
    """Split the extracted PDF text into overlapping chunks suitable for embeddings."""

    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    chunked_documents: List[DocumentChunk] = []
    for chunk in chunks:
        for piece in splitter.split_text(chunk.content):
            chunked_documents.append(
                DocumentChunk(
                    page=chunk.page,
                    content=piece,
                    source=chunk.source,
                )
            )
    return chunked_documents


def load_pdf(file_bytes: bytes, filename: str) -> List[DocumentChunk]:
    """Persist an uploaded PDF to a temp file and return chunked documents."""

    with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        temp_path = Path(tmp.name)

    try:
        page_chunks = list(extract_text_from_pdf(temp_path))
        return chunk_document(page_chunks)
    finally:
        temp_path.unlink(missing_ok=True)

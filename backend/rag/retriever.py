from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureChatOpenAI

from backend.config import get_settings
from backend.models import AnswerResponse, DocumentChunk, QuestionRequest, RetrievedContext
from backend.rag.embeddings import create_embeddings

SYSTEM_PROMPT = """You are an assistant that answers questions about uploaded documents.
Use the provided context to craft concise answers in Japanese.
If the answer cannot be determined from the context, say so explicitly.
Include short citations in the form (p.<page>) when possible."""


class RAGPipeline:
    """End-to-end helper that manages FAISS retrieval and Azure OpenAI generation."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.embeddings = create_embeddings()
        self.vector_store = self._load_or_create_vector_store()
        self.llm = AzureChatOpenAI(
            azure_deployment=self.settings.azure_openai_deployment,
            api_version=self.settings.azure_openai_api_version,
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_key=self.settings.azure_openai_api_key,
            temperature=0.2,
        )

    def _load_or_create_vector_store(self) -> FAISS:
        index_path = self.settings.faiss_index_path
        path = Path(index_path)
        if path.exists():
            return FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        return FAISS.from_texts(texts=[], embedding=self.embeddings)

    def _persist(self) -> None:
        index_path = Path(self.settings.faiss_index_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(index_path)

    def add_documents(self, chunks: List[DocumentChunk]) -> Tuple[str, int]:
        """Add chunked documents to the FAISS store and persist to disk."""

        if not chunks:
            return ("empty", 0)

        docs = [
            Document(
                page_content=chunk.content,
                metadata={
                    "page": chunk.page,
                    "source": chunk.source,
                },
            )
            for chunk in chunks
        ]
        self.vector_store.add_documents(docs)
        self._persist()
        document_id = f"{chunks[0].source}-{len(chunks)}"
        return (document_id, len(docs))

    def retrieve(self, question: str, top_k: int) -> List[RetrievedContext]:
        results = self.vector_store.similarity_search_with_score(question, k=top_k)
        return [
            RetrievedContext(
                page=int(doc.metadata.get("page", 0)),
                score=float(score),
                content=doc.page_content,
                source=str(doc.metadata.get("source", "")),
            )
            for doc, score in results
        ]

    def _build_prompt(self, context: List[RetrievedContext], question: str) -> List[dict]:
        context_text = "\n\n".join(
            f"[p.{ctx.page}] {ctx.content}" for ctx in context
        )
        user_message = (
            "以下は参考となる文書コンテキストです。必要な部分だけ利用してください。\n"
            "---\n"
            f"{context_text}\n"
            "---\n"
            f"質問: {question}"
        )
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

    def answer(self, request: QuestionRequest) -> AnswerResponse:
        contexts = self.retrieve(request.question, request.top_k)
        messages = self._build_prompt(contexts, request.question)
        response = self.llm.invoke(messages)
        usage = response.additional_kwargs.get("usage", {}) if hasattr(response, "additional_kwargs") else {}
        return AnswerResponse(
            answer=response.content,
            context=contexts,
            model=self.settings.azure_openai_deployment,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )


_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline

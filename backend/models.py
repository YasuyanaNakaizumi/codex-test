from typing import List, Optional

from pydantic import BaseModel


class DocumentChunk(BaseModel):
    page: int
    content: str
    source: str


class UploadResponse(BaseModel):
    document_id: str
    chunks_indexed: int


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5


class RetrievedContext(BaseModel):
    page: int
    score: float
    content: str
    source: str


class AnswerResponse(BaseModel):
    answer: str
    context: List[RetrievedContext]
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None

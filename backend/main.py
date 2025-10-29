from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from backend.deps import get_rag_pipeline
from backend.models import AnswerResponse, QuestionRequest, UploadResponse
from backend.rag.loader import load_pdf
from backend.rag.retriever import RAGPipeline

app = FastAPI(title="Azure OpenAI RAG Service")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> UploadResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contents = await file.read()
    chunks = load_pdf(contents, file.filename)
    document_id, count = pipeline.add_documents(chunks)
    return UploadResponse(document_id=document_id, chunks_indexed=count)


@app.post("/chat", response_model=AnswerResponse)
async def chat(
    request: QuestionRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> AnswerResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")
    return pipeline.answer(request)

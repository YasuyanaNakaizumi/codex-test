export interface UploadResult {
  document_id: string;
  chunks_indexed: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface RetrievedContext {
  page: number;
  score: number;
  content: string;
  source: string;
}

export interface AnswerResponse {
  answer: string;
  context: RetrievedContext[];
  model: string;
  prompt_tokens?: number;
  completion_tokens?: number;
}

export async function uploadPdf(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return (await response.json()) as UploadResult;
}

export async function askQuestion(question: string, topK = 5): Promise<AnswerResponse> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, top_k: topK }),
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return (await response.json()) as AnswerResponse;
}

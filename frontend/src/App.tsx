import { FormEvent, useState } from "react";
import { askQuestion, uploadPdf } from "./api";
import type { AnswerResponse } from "./api";

interface ChatEntry {
  role: "user" | "assistant";
  content: string;
  context?: AnswerResponse["context"];
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [chatting, setChatting] = useState(false);
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [messages, setMessages] = useState<ChatEntry[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleUpload() {
    if (!file) {
      setError("PDFファイルを選択してください。");
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const result = await uploadPdf(file);
      setStatus(`アップロード完了: ${result.document_id} (チャンク数: ${result.chunks_indexed})`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk(e: FormEvent) {
    e.preventDefault();
    if (!question.trim()) {
      setError("質問を入力してください。");
      return;
    }
    setChatting(true);
    setError(null);
    const currentQuestion = question;
    setMessages((prev) => [...prev, { role: "user", content: currentQuestion }]);
    setQuestion("");
    try {
      const answer = await askQuestion(currentQuestion, topK);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: answer.answer,
          context: answer.context,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setChatting(false);
    }
  }

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "2rem" }}>
      <header>
        <h1>Azure OpenAI RAG チャット</h1>
        <p>
          PDFをアップロードし、FAISSでインデックス化した内容をもとにAzure OpenAIへ質問できます。
        </p>
      </header>

      <section style={{ marginBottom: "2rem" }}>
        <h2>1. PDFアップロード</h2>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <button onClick={handleUpload} disabled={uploading}>
            {uploading ? "アップロード中..." : "アップロード"}
          </button>
        </div>
        {status && <p style={{ color: "#0f766e" }}>{status}</p>}
      </section>

      <section style={{ marginBottom: "2rem" }}>
        <h2>2. 質問する</h2>
        <form onSubmit={handleAsk} style={{ display: "flex", gap: "1rem" }}>
          <input
            type="text"
            value={question}
            placeholder="質問を入力"
            onChange={(e) => setQuestion(e.target.value)}
            style={{ flex: 1, padding: "0.75rem" }}
          />
          <input
            type="number"
            min={1}
            max={10}
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            style={{ width: "6rem", padding: "0.75rem" }}
          />
          <button type="submit" disabled={chatting}>
            {chatting ? "回答生成中..." : "送信"}
          </button>
        </form>
      </section>

      {error && (
        <div style={{ background: "#fee2e2", padding: "1rem", marginBottom: "1rem" }}>
          <strong>エラー:</strong> {error}
        </div>
      )}

      <section>
        <h2>チャット履歴</h2>
        <div style={{ display: "grid", gap: "1rem" }}>
          {messages.map((msg, idx) => (
            <article
              key={idx}
              style={{
                background: msg.role === "assistant" ? "#ffffff" : "#e2e8f0",
                padding: "1rem",
                borderRadius: "0.75rem",
                boxShadow: "0 4px 12px rgba(15, 23, 42, 0.08)",
              }}
            >
              <header style={{ fontWeight: 600, marginBottom: "0.5rem" }}>
                {msg.role === "assistant" ? "アシスタント" : "あなた"}
              </header>
              <p style={{ whiteSpace: "pre-wrap" }}>{msg.content}</p>
              {msg.context && msg.context.length > 0 && (
                <details style={{ marginTop: "0.75rem" }}>
                  <summary>参照コンテキスト</summary>
                  <ul>
                    {msg.context.map((ctx, cIdx) => (
                      <li key={cIdx}>
                        <strong>
                          {ctx.source} p.{ctx.page} (score: {ctx.score.toFixed(3)})
                        </strong>
                        <div style={{ whiteSpace: "pre-wrap", marginTop: "0.25rem" }}>
                          {ctx.content}
                        </div>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

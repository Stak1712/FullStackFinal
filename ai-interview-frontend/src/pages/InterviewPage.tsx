import { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { http } from "../api/http";
import Seo from "../seo/Seo";

type Turn = {
  role: "ai" | "user";
  text: string;
  score?: number | null;
  verdict?: string | null;
};

type SessionMeta = {
  id: number;
  grade: string;
  skills: string;
  status: "active" | "finished";
  step: number;
  max_questions: number;
};

export default function InterviewPage() {
  const { id } = useParams();
  const [turns, setTurns] = useState<Turn[]>([]);
  const [session, setSession] = useState<SessionMeta | null>(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const isFinished = session?.status === "finished";
  const progress = useMemo(() => {
    if (!session) return "";
    return `${Math.min(session.step, session.max_questions)}/${session.max_questions}`;
  }, [session]);

  async function loadHistory() {
    const res = await http.get(`/ai/sessions/${id}`);
    setTurns(res.data.turns);
    setSession(res.data.session);
  }

  useEffect(() => {
    loadHistory();
  }, [id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns.length]);

  async function send() {
    if (!text.trim() || !id || loading || isFinished) return;
    setLoading(true);
    try {
      await http.post(`/ai/sessions/${id}/answer`, { text });
      setText("");
      await loadHistory();
    } catch {
      await loadHistory();
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page-wrapper">
      <Seo title="Интервью" description="Закрытая страница прохождения виртуального интервью." noIndex />
      <div className="chat-card">
        <div className="chat-header">
          <div className="chat-title">Интервью</div>
          <div className="chat-meta">
            <span className="chat-badge">Grade: {session?.grade ?? "..."}</span>
            <span className="chat-badge">Вопросы: {progress || "..."}</span>
          </div>
        </div>

        <div className="chat-messages">
          {turns.map((t, idx) => {
            const mine = t.role === "user";
            return (
              <div key={idx} className={`msg-row ${mine ? "msg-row-me" : "msg-row-ai"}`}>
                <div className={`msg-bubble ${mine ? "msg-me" : "msg-ai"}`}>
                  <div className="msg-text">{t.text}</div>
                  {mine && typeof t.score === "number" && (
                    <div className="msg-sub">
                      score: {t.score} · verdict: {t.verdict}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input">
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={isFinished ? "Интервью завершено" : "Ваш ответ…"}
            disabled={loading || isFinished}
            onKeyDown={(e) => {
              if (e.key === "Enter") send();
            }}
          />
          <button className="btn btn-primary" onClick={send} disabled={loading || isFinished}>
            {loading ? "…" : "Отправить"}
          </button>
        </div>
      </div>
    </section>
  );
}

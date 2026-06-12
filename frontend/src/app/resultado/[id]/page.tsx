"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import MarkdownRenderer from "./MarkdownRenderer";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const POLL_INTERVAL_MS = 3000;

type Status = "pending" | "processing" | "completed" | "failed";

interface Submission {
  id: string;
  user_email: string;
  challenge_type: string;
  content: string;
  status: Status;
  ai_feedback: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

const CHALLENGE_LABELS: Record<string, string> = {
  code_review:   "🔍 Code Review",
  algorithm:     "⚡ Algoritmo",
  architecture:  "🏗️ Arquitetura",
  system_design: "🌐 System Design",
  debugging:     "🐛 Debugging",
};

const STATUS_CONFIG: Record<Status, { label: string; dot: string; badge: string }> = {
  pending:    { label: "Aguardando",    dot: "#f59e0b", badge: "badge-pending" },
  processing: { label: "Avaliando...",  dot: "#6366f1", badge: "badge-processing" },
  completed:  { label: "Concluído",     dot: "#10b981", badge: "badge-completed" },
  failed:     { label: "Falhou",        dot: "#ef4444", badge: "badge-failed" },
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

export default function ResultadoPage() {
  const params   = useParams<{ id: string }>();
  const router   = useRouter();
  const id       = params.id;

  const [submission, setSubmission] = useState<Submission | null>(null);
  const [notFound, setNotFound]     = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const fetchSubmission = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/submissions/${id}`);
      if (res.status === 404) { setNotFound(true); return; }
      if (!res.ok) throw new Error(`Erro ${res.status}`);
      const data: Submission = await res.json();
      setSubmission(data);
    } catch (err) {
      setFetchError(err instanceof Error ? err.message : "Erro ao buscar submissão.");
    }
  }, [id]);

  // Initial fetch
  useEffect(() => { fetchSubmission(); }, [fetchSubmission]);

  // Polling while not terminal status
  useEffect(() => {
    if (!submission) return;
    if (submission.status === "completed" || submission.status === "failed") return;

    const timer = setInterval(fetchSubmission, POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [submission, fetchSubmission]);

  /* ── Loading skeleton ── */
  if (!submission && !notFound && !fetchError) {
    return (
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="w-full max-w-3xl space-y-4">
          <div className="skeleton h-8 w-48 rounded-lg" />
          <div className="skeleton h-32 w-full rounded-xl" />
          <div className="skeleton h-64 w-full rounded-xl" />
        </div>
      </main>
    );
  }

  /* ── Not found ── */
  if (notFound) {
    return (
      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center">
        <div className="text-5xl mb-4">🔍</div>
        <h1 className="text-2xl font-bold mb-2" style={{ color: "var(--text-primary)" }}>Submissão não encontrada</h1>
        <p style={{ color: "var(--text-secondary)" }}>O ID informado não existe ou foi removido.</p>
        <button onClick={() => router.push("/")} className="btn-primary mt-6 px-6 py-3 text-sm">
          Voltar ao início
        </button>
      </main>
    );
  }

  /* ── Fetch error ── */
  if (fetchError) {
    return (
      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center">
        <div className="text-5xl mb-4">⚠️</div>
        <h1 className="text-2xl font-bold mb-2" style={{ color: "var(--text-primary)" }}>Erro de conexão</h1>
        <p style={{ color: "var(--text-secondary)" }}>{fetchError}</p>
        <button onClick={fetchSubmission} className="btn-primary mt-6 px-6 py-3 text-sm">
          Tentar novamente
        </button>
      </main>
    );
  }

  if (!submission) return null;

  const statusCfg  = STATUS_CONFIG[submission.status];
  const isTerminal = submission.status === "completed" || submission.status === "failed";

  return (
    <main className="flex-1 flex flex-col items-center px-4 py-12">
      <div className="w-full max-w-3xl space-y-6">

        {/* ── Header ── */}
        <div className="flex items-center justify-between animate-fade-up" style={{ animationDelay: "0ms" }}>
          <button
            onClick={() => router.push("/")}
            className="flex items-center gap-2 text-sm font-medium transition-colors"
            style={{ color: "var(--text-muted)" }}
            onMouseEnter={e => (e.currentTarget.style.color = "var(--text-secondary)")}
            onMouseLeave={e => (e.currentTarget.style.color = "var(--text-muted)")}
          >
            ← Nova submissão
          </button>
          <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
            {id.slice(0, 8)}…
          </span>
        </div>

        {/* ── Status Card ── */}
        <div className="glass-card p-6 animate-fade-up" style={{ animationDelay: "60ms" }}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-3">
                {/* status badge */}
                <span className={`badge ${statusCfg.badge}`}>
                  {!isTerminal && (
                    <span
                      className="w-2 h-2 rounded-full animate-pulse-dot inline-block"
                      style={{ background: statusCfg.dot }}
                    />
                  )}
                  {statusCfg.label}
                </span>
                <span className="text-sm px-3 py-1 rounded-full"
                  style={{ background: "rgba(99,102,241,0.08)", color: "#a5b4fc", border: "1px solid rgba(99,102,241,0.15)" }}>
                  {CHALLENGE_LABELS[submission.challenge_type] ?? submission.challenge_type}
                </span>
              </div>
              <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                📧 {submission.user_email}
              </p>
              <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                Submetido em {formatDate(submission.created_at)}
              </p>
            </div>

            {/* Spinner while processing */}
            {!isTerminal && (
              <div className="flex flex-col items-center gap-2">
                <div
                  className="w-10 h-10 rounded-full border-2 animate-spin-slow"
                  style={{ borderColor: "rgba(99,102,241,0.2)", borderTopColor: "var(--accent-primary)" }}
                />
                <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                  atualiza em {POLL_INTERVAL_MS / 1000}s
                </span>
              </div>
            )}
          </div>
        </div>

        {/* ── AI Feedback ── */}
        {submission.status === "completed" && submission.ai_feedback && (
          <div className="glass-card p-8 animate-fade-up animate-glow" style={{ animationDelay: "120ms" }}>
            <div className="flex items-center gap-3 mb-6 pb-4"
              style={{ borderBottom: "1px solid var(--border)" }}>
              <div className="w-9 h-9 rounded-xl flex items-center justify-center text-lg"
                style={{ background: "linear-gradient(135deg,var(--accent-primary),var(--accent-secondary))" }}>
                🤖
              </div>
              <div>
                <h2 className="font-bold" style={{ color: "var(--text-primary)" }}>
                  Feedback do Tech Lead
                </h2>
                <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                  Atualizado em {formatDate(submission.updated_at)}
                </p>
              </div>
            </div>

            <MarkdownRenderer content={submission.ai_feedback} />
          </div>
        )}

        {/* ── Error Message ── */}
        {submission.status === "failed" && (
          <div className="glass-card p-6 animate-fade-up" style={{ animationDelay: "120ms", borderColor: "rgba(239,68,68,0.2)" }}>
            <div className="flex items-start gap-4">
              <span className="text-2xl">❌</span>
              <div>
                <h2 className="font-bold mb-1" style={{ color: "#f87171" }}>
                  Falha no processamento
                </h2>
                <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                  {submission.error_message ?? "Erro desconhecido. Tente submeter novamente."}
                </p>
              </div>
            </div>
            <button onClick={() => router.push("/")} className="btn-primary mt-5 px-5 py-2.5 text-sm w-full">
              Tentar novamente
            </button>
          </div>
        )}

        {/* ── Pending/Processing placeholder ── */}
        {(submission.status === "pending" || submission.status === "processing") && (
          <div className="space-y-4 animate-fade-up" style={{ animationDelay: "120ms" }}>
            <div className="skeleton h-6 w-40 rounded" />
            <div className="skeleton h-4 w-full rounded" />
            <div className="skeleton h-4 w-5/6 rounded" />
            <div className="skeleton h-4 w-4/5 rounded" />
            <div className="skeleton h-32 w-full rounded-xl mt-2" />
          </div>
        )}

      </div>
    </main>
  );
}

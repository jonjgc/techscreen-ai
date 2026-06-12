"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";

const CHALLENGE_TYPES = [
  { value: "code_review",   label: "🔍 Code Review",    desc: "Revisão de qualidade e boas práticas" },
  { value: "algorithm",     label: "⚡ Algoritmo",       desc: "Complexidade, corretude e eficiência" },
  { value: "architecture",  label: "🏗️ Arquitetura",    desc: "Design de software e padrões" },
  { value: "system_design", label: "🌐 System Design",  desc: "Sistemas distribuídos e escalabilidade" },
  { value: "debugging",     label: "🐛 Debugging",       desc: "Identificação e correção de bugs" },
];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const MAX_CHARS = 50_000;

export default function HomePage() {
  const router = useRouter();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [email, setEmail]             = useState("");
  const [challengeType, setChallengeType] = useState("");
  const [content, setContent]         = useState("");
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState<string | null>(null);

  const charCount  = content.length;
  const charPct    = Math.min((charCount / MAX_CHARS) * 100, 100);
  const isValid    = email && challengeType && content.trim().length >= 10;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isValid || loading) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/submissions/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_email: email,
          challenge_type: challengeType,
          content,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.detail ?? `Erro ${res.status}`);
      }

      const submission = await res.json();
      router.push(`/resultado/${submission.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro inesperado. Tente novamente.");
      setLoading(false);
    }
  }

  return (
    <main className="flex-1 flex flex-col items-center justify-center px-4 py-16">
      {/* ── Hero ── */}
      <div className="text-center mb-12 animate-fade-up" style={{ animationDelay: "0ms" }}>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full mb-6"
          style={{ background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.25)" }}>
          <span className="animate-pulse-dot w-2 h-2 rounded-full inline-block" style={{ background: "var(--accent-primary)" }} />
          <span className="text-sm font-medium" style={{ color: "#a5b4fc" }}>Avaliação por IA em tempo real</span>
        </div>

        <h1 className="text-5xl font-bold tracking-tight mb-4 leading-tight">
          <span className="gradient-text">TechScreen</span>
          <span style={{ color: "var(--text-primary)" }}> AI</span>
        </h1>
        <p className="text-lg max-w-lg mx-auto" style={{ color: "var(--text-secondary)" }}>
          Submeta seu código ou proposta de arquitetura e receba um feedback
          detalhado de um <strong style={{ color: "var(--text-primary)" }}>Tech Lead Sênior virtual</strong>.
        </p>
      </div>

      {/* ── Form Card ── */}
      <div className="glass-card w-full max-w-2xl p-8 animate-fade-up" style={{ animationDelay: "80ms" }}>
        <form onSubmit={handleSubmit} className="flex flex-col gap-6">

          {/* Email */}
          <div className="flex flex-col gap-2">
            <label htmlFor="email" className="text-sm font-semibold" style={{ color: "var(--text-secondary)" }}>
              E-mail do desenvolvedor
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              placeholder="dev@exemplo.com.br"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="field-input px-4 py-3 text-sm"
            />
          </div>

          {/* Challenge Type */}
          <div className="flex flex-col gap-2">
            <label htmlFor="challenge_type" className="text-sm font-semibold" style={{ color: "var(--text-secondary)" }}>
              Tipo de desafio
            </label>
            <select
              id="challenge_type"
              required
              value={challengeType}
              onChange={e => setChallengeType(e.target.value)}
              className="field-input px-4 py-3 text-sm"
            >
              <option value="" disabled>Selecione o tipo...</option>
              {CHALLENGE_TYPES.map(ct => (
                <option key={ct.value} value={ct.value}>{ct.label} — {ct.desc}</option>
              ))}
            </select>
          </div>

          {/* Content */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <label htmlFor="content" className="text-sm font-semibold" style={{ color: "var(--text-secondary)" }}>
                Código ou descrição
              </label>
              <span className="text-xs font-mono" style={{ color: charCount > MAX_CHARS * 0.9 ? "#f87171" : "var(--text-muted)" }}>
                {charCount.toLocaleString("pt-BR")} / {MAX_CHARS.toLocaleString("pt-BR")}
              </span>
            </div>
            <textarea
              id="content"
              ref={textareaRef}
              required
              rows={12}
              placeholder="Cole seu código, descreva a arquitetura ou explique o sistema aqui..."
              value={content}
              onChange={e => setContent(e.target.value)}
              className="field-input px-4 py-3 text-sm font-mono resize-y"
              style={{ minHeight: "200px" }}
            />
            {/* char progress bar */}
            <div className="h-0.5 rounded-full overflow-hidden" style={{ background: "var(--border)" }}>
              <div
                className="h-full rounded-full transition-all duration-300"
                style={{
                  width: `${charPct}%`,
                  background: charPct > 90
                    ? "linear-gradient(90deg,#f59e0b,#ef4444)"
                    : "linear-gradient(90deg,var(--accent-primary),var(--accent-secondary))",
                }}
              />
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-start gap-3 px-4 py-3 rounded-lg text-sm"
              style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)", color: "#f87171" }}>
              <span className="text-base">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Submit */}
          <button
            id="submit-btn"
            type="submit"
            disabled={!isValid || loading}
            className="btn-primary px-6 py-4 text-base flex items-center justify-center gap-3 w-full"
          >
            {loading ? (
              <>
                <span className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin-slow" />
                Enviando para avaliação...
              </>
            ) : (
              <>
                <span>🚀</span>
                Enviar para Avaliação
              </>
            )}
          </button>
        </form>
      </div>

      {/* ── Features ── */}
      <div className="grid grid-cols-3 gap-4 mt-10 w-full max-w-2xl animate-fade-up" style={{ animationDelay: "160ms" }}>
        {[
          { icon: "⚡", title: "Rápido", desc: "Feedback em segundos" },
          { icon: "🎯", title: "Preciso", desc: "Avaliação técnica detalhada" },
          { icon: "📋", title: "Estruturado", desc: "Seções claras e objetivas" },
        ].map(f => (
          <div key={f.title} className="text-center p-4 rounded-xl"
            style={{ background: "rgba(20,28,46,0.5)", border: "1px solid var(--border)" }}>
            <div className="text-2xl mb-2">{f.icon}</div>
            <div className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{f.title}</div>
            <div className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>{f.desc}</div>
          </div>
        ))}
      </div>
    </main>
  );
}

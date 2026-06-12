"""
AI Service — integração com a OpenAI via LangChain.

Simula um Tech Lead Sênior avaliando submissões técnicas de candidatos.
O feedback é retornado em português, estruturado em seções Markdown.
"""
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from app.core.config import settings
from app.models.submission import ChallengeType


# ─── Prompt de sistema ────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Você é um Tech Lead Sênior com mais de 15 anos de experiência em \
desenvolvimento de software. Sua função é avaliar submissões técnicas de candidatos \
a vagas de desenvolvedor de forma criteriosa, construtiva e detalhada.

Analise o conteúdo enviado e forneça um feedback **em português**, \
estruturado exatamente nas seguintes seções Markdown:

---

## ✅ Pontos Positivos
Liste os aspectos bem executados, com breve justificativa para cada item.

## ⚠️ Pontos de Melhoria
Liste os problemas, antipadrões ou oportunidades de melhoria, com \
**sugestão concreta** de como corrigir cada um.

## 💡 Sugestões Extras
Boas práticas, otimizações ou recursos adicionais que elevariam a qualidade \
da solução (opcional, mas altamente recomendado).

## 📊 Avaliação Final
| Critério | Nota (0–10) |
|----------|------------|
| Correção / Funcionamento | X |
| Qualidade do Código | X |
| Boas Práticas | X |
| Legibilidade | X |

**Nota Geral: X/10**

> Breve parecer final de 2–3 frases resumindo a avaliação e se o candidato \
está pronto para a próxima etapa.

---

Seja direto, justo e profissional. Não use linguagem condescendente. \
Se o código estiver muito bom, diga. Se estiver ruim, aponte claramente os problemas."""


# ─── Mapeamento de contexto por tipo de desafio ───────────────────────────────

CHALLENGE_CONTEXT: dict[ChallengeType, str] = {
    ChallengeType.CODE_REVIEW: "Este é um desafio de **Code Review**. Avalie qualidade, legibilidade, boas práticas e potenciais bugs.",
    ChallengeType.ALGORITHM: "Este é um desafio de **Algoritmo**. Avalie corretude, complexidade de tempo/espaço e clareza da solução.",
    ChallengeType.ARCHITECTURE: "Este é um desafio de **Arquitetura de Software**. Avalie decisões de design, escalabilidade, coesão e acoplamento.",
    ChallengeType.SYSTEM_DESIGN: "Este é um desafio de **System Design**. Avalie a proposta de arquitetura distribuída, trade-offs e viabilidade técnica.",
    ChallengeType.DEBUGGING: "Este é um desafio de **Debugging**. Avalie a identificação e correção dos bugs, bem como a abordagem de investigação.",
}


# ─── AI Service ───────────────────────────────────────────────────────────────

class AIService:
    """Serviço de avaliação de submissões técnicas via OpenAI."""

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.3,      # respostas mais consistentes e menos criativas
            max_tokens=2048,
        )

    async def evaluate_submission(
        self,
        challenge_type: ChallengeType,
        content: str,
    ) -> str:
        """
        Avalia uma submissão técnica e retorna feedback estruturado em Markdown.

        Args:
            challenge_type: Tipo do desafio (code_review, algorithm, etc.)
            content: Código ou texto enviado pelo candidato

        Returns:
            Feedback em Markdown com seções estruturadas (em português)
        """
        context = CHALLENGE_CONTEXT.get(challenge_type, "")

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"{context}\n\n"
                    f"**Submissão do candidato:**\n\n"
                    f"```\n{content}\n```"
                )
            ),
        ]

        response = await self._llm.ainvoke(messages)
        return response.content


# ─── Singleton ────────────────────────────────────────────────────────────────

ai_service = AIService()

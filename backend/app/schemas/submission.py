"""
Schemas Pydantic para Submissions.

Separação de responsabilidades:
- SubmissionCreate   → body do POST /submissions (entrada)
- SubmissionResponse → resposta da API (saída individual)
- SubmissionList     → resposta de listagem paginada
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.submission import ChallengeType, SubmissionStatus


# ─── Request Schemas ──────────────────────────────────────────────────────────

class SubmissionCreate(BaseModel):
    """Payload para criar uma nova submissão técnica."""

    user_email: EmailStr = Field(
        ...,
        description="E-mail do desenvolvedor que está submetendo o desafio",
        examples=["dev@exemplo.com.br"],
    )
    challenge_type: ChallengeType = Field(
        ...,
        description="Tipo do desafio técnico",
        examples=[ChallengeType.CODE_REVIEW],
    )
    content: str = Field(
        ...,
        min_length=10,
        max_length=50_000,
        description="Código, arquitetura ou texto a ser avaliado (mín. 10 caracteres)",
        examples=["def soma(a, b):\n    return a + b"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_email": "dev@exemplo.com.br",
                "challenge_type": "code_review",
                "content": "def busca_binaria(arr, target):\n    left, right = 0, len(arr)\n    while left < right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid\n    return -1",
            }
        }
    }


# ─── Response Schemas ─────────────────────────────────────────────────────────

class SubmissionResponse(BaseModel):
    """Representação completa de uma submissão (retornada pela API)."""

    id: uuid.UUID
    user_email: str
    challenge_type: ChallengeType
    content: str
    status: SubmissionStatus
    ai_feedback: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # compatível com ORM objects


class SubmissionList(BaseModel):
    """Resposta paginada de listagem de submissões."""

    items: list[SubmissionResponse]
    total: int
    skip: int
    limit: int

import enum
import uuid

from sqlalchemy import DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SubmissionStatus(str, enum.Enum):
    """Ciclo de vida de uma submissão."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ChallengeType(str, enum.Enum):
    """Tipos de desafio suportados pela plataforma."""
    CODE_REVIEW = "code_review"
    ARCHITECTURE = "architecture"
    ALGORITHM = "algorithm"
    SYSTEM_DESIGN = "system_design"
    DEBUGGING = "debugging"


class Submission(Base):
    """
    Modelo principal — representa uma submissão técnica de um candidato.

    Ciclo de vida do status:
        pending → processing → completed
                           └→ failed
    """

    __tablename__ = "submissions"

    # ── Identificação ────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ── Dados do candidato ────────────────────────────────────────────────────
    user_email: Mapped[str] = mapped_column(
        nullable=False,
        index=True,
        comment="E-mail do desenvolvedor que submeteu o desafio",
    )

    # ── Conteúdo da submissão ─────────────────────────────────────────────────
    challenge_type: Mapped[ChallengeType] = mapped_column(
        Enum(ChallengeType, name="challenge_type_enum", create_type=True),
        nullable=False,
        comment="Tipo do desafio técnico",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Código, arquitetura ou texto enviado pelo candidato",
    )

    # ── Estado & Feedback ─────────────────────────────────────────────────────
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status_enum", create_type=True),
        nullable=False,
        default=SubmissionStatus.PENDING,
        server_default=SubmissionStatus.PENDING.value,
        index=True,
        comment="Estado atual do processamento da submissão",
    )

    ai_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="Feedback gerado pelo agente de IA após avaliação",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="Mensagem de erro caso o processamento falhe",
    )

    # ── Auditoria ─────────────────────────────────────────────────────────────
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Data/hora de criação da submissão (UTC)",
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Data/hora da última atualização (UTC)",
    )

    def __repr__(self) -> str:
        return (
            f"<Submission id={self.id} email={self.user_email} "
            f"type={self.challenge_type} status={self.status}>"
        )

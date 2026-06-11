"""
Repositório de Submissions — camada de acesso ao banco de dados.

Segue o padrão Repository (Clean Architecture):
- A lógica de negócio (services/tasks) não conhece SQLAlchemy diretamente.
- Toda query passa por aqui, facilitando testes e troca de banco futura.
"""
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.submission import Submission, SubmissionStatus


class SubmissionRepository:
    """CRUD assíncrono para o modelo Submission."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, submission: Submission) -> Submission:
        """Persiste uma nova submissão no banco."""
        self.db.add(submission)
        await self.db.flush()   # gera o ID sem commitar
        await self.db.refresh(submission)
        return submission

    async def get_by_id(self, submission_id: uuid.UUID) -> Optional[Submission]:
        """Busca uma submissão pelo UUID. Retorna None se não encontrada."""
        result = await self.db.execute(
            select(Submission).where(Submission.id == submission_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 50) -> list[Submission]:
        """Lista todas as submissões com paginação."""
        result = await self.db.execute(
            select(Submission)
            .order_by(Submission.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        submission_id: uuid.UUID,
        status: SubmissionStatus,
        ai_feedback: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Submission]:
        """
        Atualiza o status (e opcionalmente feedback/erro) de uma submissão.
        Retorna a submissão atualizada ou None se não encontrada.
        """
        submission = await self.get_by_id(submission_id)
        if not submission:
            return None

        submission.status = status
        if ai_feedback is not None:
            submission.ai_feedback = ai_feedback
        if error_message is not None:
            submission.error_message = error_message

        await self.db.flush()
        await self.db.refresh(submission)
        return submission

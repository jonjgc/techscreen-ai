"""
Celery Task — Avaliação assíncrona de submissões técnicas.

Fluxo de status:
    pending → processing → completed
                       └→ failed

O worker abre uma sessão síncrona independente (psycopg2) pois o Celery não
suporta sessões async nativas. A sessão async do FastAPI NÃO é reutilizada aqui.
"""
import asyncio
import uuid

import structlog
from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.submission import Submission, SubmissionStatus
from app.services.ai_service import ai_service

logger = structlog.get_logger(__name__)


# ─── Sessão síncrona para o Worker ───────────────────────────────────────────
# O Celery roda em threads/processos síncronos; usamos psycopg2 (sync driver).
_sync_engine = create_engine(
    settings.database_sync_url or settings.database_url.replace(
        "postgresql+asyncpg", "postgresql"
    ),
    pool_pre_ping=True,
    pool_size=5,
)
SyncSessionLocal = sessionmaker(bind=_sync_engine, expire_on_commit=False)


def _get_submission(db: Session, submission_id: uuid.UUID) -> Submission | None:
    return db.query(Submission).filter(Submission.id == submission_id).first()


# ─── Celery Task ─────────────────────────────────────────────────────────────

@celery_app.task(
    name="tasks.evaluate_submission",
    bind=True,
    max_retries=3,
    default_retry_delay=30,   # segundos entre retries
    acks_late=True,
)
def evaluate_submission_task(self: Task, submission_id: str) -> dict:
    """
    Avalia uma submissão técnica de forma assíncrona.

    Args:
        submission_id: UUID da submissão (string)

    Returns:
        dict com status final e resumo do resultado
    """
    sub_uuid = uuid.UUID(submission_id)
    log = logger.bind(submission_id=submission_id, task_id=self.request.id)

    with SyncSessionLocal() as db:
        # 1. Busca a submissão
        submission = _get_submission(db, sub_uuid)
        if not submission:
            log.error("submission_not_found")
            return {"status": "error", "reason": "submission_not_found"}

        log.info("task_started", challenge_type=submission.challenge_type)

        # 2. Marca como processing
        submission.status = SubmissionStatus.PROCESSING
        db.commit()

        try:
            # 3. Chama o serviço de IA (async dentro do worker síncrono)
            feedback = asyncio.run(
                ai_service.evaluate_submission(
                    challenge_type=submission.challenge_type,
                    content=submission.content,
                )
            )

            # 4. Persiste o feedback e marca como completed
            submission.status = SubmissionStatus.COMPLETED
            submission.ai_feedback = feedback
            db.commit()

            log.info("task_completed")
            return {"status": "completed", "submission_id": submission_id}

        except Exception as exc:
            # 5. Marca como failed e registra o erro
            log.error("task_failed", error=str(exc))
            submission.status = SubmissionStatus.FAILED
            submission.error_message = str(exc)
            db.commit()

            # Tenta retry automático para erros transitórios (ex: rate limit)
            raise self.retry(exc=exc)

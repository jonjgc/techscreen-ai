"""
Router de Submissions — endpoints REST da API.

Endpoints:
    POST   /submissions          → cria submissão e enfileira avaliação
    GET    /submissions/{id}     → consulta status/feedback de uma submissão
    GET    /submissions          → lista todas as submissões (paginada)
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.submission import Submission, SubmissionStatus
from app.repositories.submission_repository import SubmissionRepository
from app.schemas.submission import SubmissionCreate, SubmissionList, SubmissionResponse
from app.tasks.evaluate_submission import evaluate_submission_task

router = APIRouter(tags=["Submissions"])


# ─── POST /submissions ────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=SubmissionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submeter um desafio técnico para avaliação",
    description=(
        "Cria uma nova submissão com status `pending` e enfileira a avaliação "
        "assíncrona pelo agente de IA. Use `GET /submissions/{id}` para acompanhar "
        "o resultado via polling."
    ),
)
async def create_submission(
    payload: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    repo = SubmissionRepository(db)

    submission = Submission(
        user_email=payload.user_email,
        challenge_type=payload.challenge_type,
        content=payload.content,
        status=SubmissionStatus.PENDING,
    )
    submission = await repo.create(submission)

    # Dispara a task Celery (não bloqueia a resposta da API)
    evaluate_submission_task.delay(str(submission.id))

    return SubmissionResponse.model_validate(submission)


# ─── GET /submissions/{id} ────────────────────────────────────────────────────

@router.get(
    "/{submission_id}",
    response_model=SubmissionResponse,
    summary="Consultar status e feedback de uma submissão",
    description=(
        "Retorna os dados completos de uma submissão, incluindo o `ai_feedback` "
        "quando o status for `completed`, ou `error_message` se `failed`."
    ),
)
async def get_submission(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> SubmissionResponse:
    repo = SubmissionRepository(db)
    submission = await repo.get_by_id(submission_id)

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submissão '{submission_id}' não encontrada.",
        )

    return SubmissionResponse.model_validate(submission)


# ─── GET /submissions ─────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=SubmissionList,
    summary="Listar todas as submissões",
    description="Retorna uma lista paginada de todas as submissões, ordenadas por data de criação (mais recentes primeiro).",
)
async def list_submissions(
    skip: int = Query(default=0, ge=0, description="Número de itens a pular"),
    limit: int = Query(default=20, ge=1, le=100, description="Máximo de itens retornados"),
    db: AsyncSession = Depends(get_db),
) -> SubmissionList:
    repo = SubmissionRepository(db)
    submissions = await repo.list_all(skip=skip, limit=limit)

    return SubmissionList(
        items=[SubmissionResponse.model_validate(s) for s in submissions],
        total=len(submissions),
        skip=skip,
        limit=limit,
    )

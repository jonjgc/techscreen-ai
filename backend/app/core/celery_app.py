from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "techscreen",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"],  # módulo de tasks (será populado no commit 3)
)

celery_app.conf.update(
    # Serialização
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Retry / confiabilidade
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Resultados
    result_expires=3600,  # 1 hora
    # Prefetch — 1 task por worker (melhor para tarefas pesadas de IA)
    worker_prefetch_multiplier=1,
)

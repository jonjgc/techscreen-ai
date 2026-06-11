from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação (startup / shutdown)."""
    # Startup: verifica conexão com o banco
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: None)  # ping ao banco
    yield
    # Shutdown: fecha o pool de conexões
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="Plataforma de avaliação automática de testes técnicos com IA",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "TechScreen AI API está online 🚀",
        "version": settings.version,
        "environment": settings.environment,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": settings.app_name}

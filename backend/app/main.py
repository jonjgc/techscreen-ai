from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TechScreen AI",
    description="Plataforma de avaliação automática de testes técnicos com IA",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    return {"message": "TechScreen AI API está online 🚀", "version": "0.1.0"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

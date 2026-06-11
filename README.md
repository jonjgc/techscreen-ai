# 🚀 TechScreen AI

> Plataforma de avaliação automática de testes técnicos com Inteligência Artificial

## 📌 Visão Geral

O **TechScreen AI** é uma plataforma fullstack onde desenvolvedores submetem testes de código ou propostas de arquitetura e recebem feedback detalhado gerado por um agente de IA que simula um Tech Lead Sênior.

## 🏗️ Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| **Backend API** | FastAPI (Python 3.11+) |
| **Banco de Dados** | PostgreSQL 16 |
| **Fila Assíncrona** | Celery + Redis |
| **IA / Agente** | OpenAI API (GPT-4) |
| **Frontend** | Next.js 14 (App Router) |
| **Containerização** | Docker + Docker Compose |

## 🚦 Fluxo da Aplicação

```
Usuário → [Next.js Form] → POST /submissions → [FastAPI]
                                                    ↓
                                             [PostgreSQL] ← status: pending
                                                    ↓
                                         [Celery Task .delay()]
                                                    ↓
                                        [Redis Queue] → [Worker]
                                                              ↓
                                                    [OpenAI API]
                                                              ↓
                                             [PostgreSQL] ← status: completed + ai_feedback
                                                    ↑
Usuário ← [Dashboard Polling] ← GET /submissions/{id}
```

## 🛠️ Como Rodar Localmente

### Pré-requisitos
- [Docker](https://www.docker.com/) e Docker Compose
- [Node.js 20+](https://nodejs.org/) (para desenvolvimento local do frontend)
- Chave de API da OpenAI

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/TechScreen-AI.git
cd TechScreen-AI
```

### 2. Configure as variáveis de ambiente
```bash
cp backend/.env.example backend/.env
# Edite backend/.env e adicione sua OPENAI_API_KEY
```

### 3. Suba os serviços
```bash
docker-compose up --build
```

### 4. Execute as migrações
```bash
docker-compose exec api alembic upgrade head
```

### 5. Acesse a aplicação
- **Frontend:** http://localhost:3000
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc

## 📁 Estrutura do Projeto

```
TechScreen-AI/
├── backend/                 # FastAPI + Celery Worker
│   ├── app/
│   │   ├── api/            # Routers e endpoints
│   │   ├── core/           # Configurações, DB, Celery
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Lógica de negócio (ai_service)
│   │   └── tasks/          # Celery tasks
│   ├── alembic/            # Migrações do banco
│   ├── tests/              # Testes unitários e de integração
│   └── pyproject.toml
├── frontend/               # Next.js App Router
│   └── src/app/
├── docker-compose.yml
└── README.md
```

## 🧪 Rodando os Testes

```bash
docker-compose exec api pytest tests/ -v
```

## 🔑 Variáveis de Ambiente

Copie `backend/.env.example` para `backend/.env` e preencha:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | URL do PostgreSQL | `postgresql+asyncpg://...` |
| `REDIS_URL` | URL do Redis | `redis://redis:6379/0` |
| `OPENAI_API_KEY` | Sua chave OpenAI | `sk-...` |
| `SECRET_KEY` | Chave secreta da app | `your-secret-key` |
| `NEXT_PUBLIC_API_URL` | URL da API para o frontend | `http://localhost:8000` |

## 📄 Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.

from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import init_db, close_db
from .routers.models.ollama import router as ollama_models_router
from .routers.database_models import router as database_models_router
from .routers import chat
from .routers import stt

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    await init_db()
    yield
    await close_db()

app = FastAPI(
    title="Ollama FastAPI Service",
    description="FastAPI service for Ollama integration with LangGraph",
    version="1.0.0",
    prefix="/api/v1",
    docs_url="/",
    lifespan=lifespan
)

app.include_router(ollama_models_router, prefix="/ollama/models", tags=["ollama-models"])
app.include_router(database_models_router, prefix="/models", tags=["database-models"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(stt.router, prefix="/stt", tags=["speech-to-text"])

@app.get("/")
async def root():
    return {"message": "Ollama FastAPI Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

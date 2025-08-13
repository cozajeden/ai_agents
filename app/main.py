from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="Ollama FastAPI Service",
    description="FastAPI service for Ollama integration with LangGraph",
    version="1.0.0",
    prefix="/api/v1",
    docs_url="/",
    lifespan=lifespan
)

# Import and include routers here
from routers.models.ollama import router as ollama_models_router
from routers.database_models import router as database_models_router
from routers import chat

# Ollama model management routes
app.include_router(ollama_models_router, prefix="/api/v1/ollama/models", tags=["ollama-models"])

# Database models routes
app.include_router(database_models_router, prefix="/api/v1/models", tags=["database-models"])

# Chat routes
app.include_router(chat.router, prefix="/api/v1/ollama/chat", tags=["ollama-chat"])

@app.get("/")
async def root():
    return {"message": "Ollama FastAPI Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

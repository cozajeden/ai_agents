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
    prefix="/api/v1",
    title="Ollama FastAPI Service",
    description="FastAPI service for Ollama integration with LangGraph",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/",
)

# Import and include routers here
from routers import models, chat
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(chat.router, prefix="/ollama", tags=["ollama"])

@app.get("/")
async def root():
    return {"message": "Ollama FastAPI Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

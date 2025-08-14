from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Session
from ..agents.chat_agent import OllamaChatAgent
from ..database import get_db
from ..models.base import ChatInteraction
import json
import time
import uuid

router = APIRouter()

chat_agent = OllamaChatAgent()

class ChatRequest(BaseModel):
    message: str
    model_name: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    error: str
    model_name: str
    conversation_history: List[dict]
    session_id: str
    processing_time: float

class PullModelRequest(BaseModel):
    model: str

class PullModelResponse(BaseModel):
    status: str
    model: str
    detail: Optional[dict] = None

@router.post("/", response_model=ChatResponse)
def chat_with_model(request: ChatRequest, db: Session = Depends(get_db)):
    """Chat with an Ollama model using LangGraph"""
    start_time = time.time()
    
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if not request.model_name:
            raise HTTPException(status_code=400, detail="Model name is required")
        
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        conversation_history = []
        if request.session_id:
            from sqlmodel import select
            statement = select(ChatInteraction).where(
                ChatInteraction.session_id == request.session_id
            ).order_by(ChatInteraction.created_at)
            
            previous_interactions = db.exec(statement).all()
            
            for interaction in previous_interactions:
                conversation_history.append({
                    "role": "user",
                    "content": interaction.user_message
                })
                conversation_history.append({
                    "role": "assistant", 
                    "content": interaction.ai_response
                })
        
        result = chat_agent.chat(
            message=request.message,
            model_name=request.model_name,
            conversation_history=conversation_history
        )
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        processing_time = time.time() - start_time
        
        chat_interaction = ChatInteraction(
            session_id=request.session_id,
            model_name=result["model_name"],
            user_message=request.message,
            ai_response=result["response"],
            conversation_history=json.dumps(result["conversation_history"]),
            processing_time=processing_time
        )
        
        db.add(chat_interaction)
        db.commit()
        db.refresh(chat_interaction)
        
        return ChatResponse(
            response=result["response"],
            error=result.get("error", ""),
            model_name=result["model_name"],
            conversation_history=result["conversation_history"],
            session_id=chat_interaction.session_id,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.get("/health")
def chat_health_check():
    """Health check for the chat service"""
    try:
        models = chat_agent.get_available_models()
        return {
            "status": "healthy",
            "available_models": len(models),
            "ollama_url": chat_agent.ollama_base_url
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "ollama_url": chat_agent.ollama_base_url
        }

@router.post("/models/reload")
def reload_available_models():
    """Reload available Ollama models after initialization"""
    chat_agent._load_available_models()
    return {"models": chat_agent.get_available_models()}

@router.post("/models/pull", response_model=PullModelResponse)
def pull_model(body: PullModelRequest):
    """Pull an Ollama model by name (e.g., "llama3.1:8b")."""
    import httpx
    try:
        with httpx.Client(timeout=None) as client:
            resp = client.post(
                f"{chat_agent.ollama_base_url}/api/pull",
                json={"name": body.model},
            )
            resp.raise_for_status()
            detail = None
            try:
                detail = resp.json()
            except Exception:
                detail = {"raw": resp.text}
            chat_agent._load_available_models()
            return PullModelResponse(status="ok", model=body.model, detail=detail)
    except httpx.HTTPError as e:
        message = e.response.text if getattr(e, "response", None) is not None else str(e)
        raise HTTPException(status_code=400, detail=f"Pull failed for {body.model}: {message}")

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import httpx
import os

router = APIRouter()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

class ModelInfo(BaseModel):
    name: str
    size: str
    modified_at: str
    status: str

class ModelsStatusResponse(BaseModel):
    total_models: int
    max_loaded_models: int
    keep_alive_timeout: str
    models: List[ModelInfo]

@router.get("/", response_model=List[str])
def get_available_models():
    try:
        with httpx.Client() as client:
            response = client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return models
            else:
                raise HTTPException(status_code=500, detail="Failed to fetch models from Ollama")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")

@router.post("/{model_name}/load")
def load_model(model_name: str):
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{OLLAMA_BASE_URL}/api/pull",
                json={"name": model_name}
            )
            if response.status_code == 200:
                return {"message": f"Model {model_name} loaded successfully"}
            else:
                raise HTTPException(status_code=400, detail=f"Failed to load model: {response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

@router.delete("/{model_name}/unload")
def unload_model(model_name: str):
    try:
        return {
            "message": f"Model {model_name} will be unloaded automatically after timeout",
            "note": "Use OLLAMA_KEEP_ALIVE setting to control unload timing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/status", response_model=ModelsStatusResponse)
def get_models_status():
    try:
        with httpx.Client() as client:
            response = client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to get models")
            
            models_data = response.json()
            models = []
            
            for model in models_data.get("models", []):
                model_info = ModelInfo(
                    name=model["name"],
                    size=model.get("size", "Unknown"),
                    modified_at=model.get("modified_at", "Unknown"),
                    status="Available"
                )
                models.append(model_info)
            
            return ModelsStatusResponse(
                total_models=len(models),
                max_loaded_models=1,
                keep_alive_timeout="5m",
                models=models
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models status: {str(e)}")

@router.get("/health")
def ollama_health_check():
    try:
        with httpx.Client() as client:
            response = client.get(f"{OLLAMA_BASE_URL}/api/version")
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "ollama_url": OLLAMA_BASE_URL,
                    "version": response.json().get("version", "Unknown")
                }
            else:
                return {
                    "status": "unhealthy",
                    "ollama_url": OLLAMA_BASE_URL,
                    "error": "Ollama service not responding"
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "ollama_url": OLLAMA_BASE_URL,
            "error": str(e)
        }

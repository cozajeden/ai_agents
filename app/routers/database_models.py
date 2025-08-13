from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timezone
from ..database import get_db
from ..models.base import ModelRequest

router = APIRouter()

@router.get("/", response_model=List[ModelRequest])
def get_model_requests(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all model requests with pagination"""
    statement = select(ModelRequest).offset(skip).limit(limit)
    requests = db.exec(statement).all()
    return requests

@router.get("/{request_id}", response_model=ModelRequest)
def get_model_request(request_id: str, db: Session = Depends(get_db)):
    """Get a specific model request by ID"""
    statement = select(ModelRequest).where(ModelRequest.request_id == request_id)
    request = db.exec(statement).first()
    if not request:
        raise HTTPException(status_code=404, detail="Model request not found")
    return request

@router.post("/", response_model=ModelRequest)
def create_model_request(request: ModelRequest, db: Session = Depends(get_db)):
    """Create a new model request"""
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

@router.put("/{request_id}", response_model=ModelRequest)
def update_model_request(
    request_id: str, 
    request_update: ModelRequest, 
    db: Session = Depends(get_db)
):
    """Update a model request"""
    statement = select(ModelRequest).where(ModelRequest.request_id == request_id)
    db_request = db.exec(statement).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Model request not found")
    
    # Update fields
    for field, value in request_update.dict(exclude_unset=True).items():
        setattr(db_request, field, value)
    
    db_request.updated_at = datetime.now(timezone.utc)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

@router.delete("/{request_id}")
def delete_model_request(request_id: str, db: Session = Depends(get_db)):
    """Delete a model request"""
    statement = select(ModelRequest).where(ModelRequest.request_id == request_id)
    request = db.exec(statement).first()
    if not request:
        raise HTTPException(status_code=404, detail="Model request not found")
    
    db.delete(request)
    db.commit()
    return {"message": "Model request deleted"}

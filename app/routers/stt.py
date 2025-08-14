from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import whisper
import tempfile
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

model_choices = Query(default="turbo", description="Model to use for transcription", choices=["tiny", "base", "small", "medium", "large", "turbo"])

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    model: str = model_choices,
    language: Optional[str] = None
):
    """
    Transcribe audio file to text using OpenAI Whisper.
    
    Args:
        audio_file: Audio file upload (supports wav, mp3, m4a, flac, etc.)
        language: Language code for transcription (optional, auto-detected if not provided)
    
    Returns:
        JSON response with transcribed text and metadata
    """
    try:
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400, 
                detail="File must be an audio file"
            )
        
        audio_content = await audio_file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.filename.split('.')[-1] if '.' in audio_file.filename else 'wav'}") as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        try:
            logger.info("Loading Whisper model...")
            model = whisper.load_model(model)
            
            logger.info("Transcribing audio...")
            if language:
                result = model.transcribe(temp_file_path, language=language)
            else:
                result = model.transcribe(temp_file_path)
            
            os.unlink(temp_file_path)
            
            return JSONResponse(
                content={
                    "success": True,
                    "transcribed_text": result["text"].strip(),
                    "language": result.get("language", "auto-detected"),
                    "file_name": audio_file.filename,
                    "file_size": len(audio_content),
                    "model_used": "whisper-base"
                },
                status_code=200
            )
            
        except Exception as e:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            logger.error(f"Transcription failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process audio file: {str(e)}"
        )

@router.get("/health")
async def stt_health_check():
    """
    Health check for STT service.
    """
    try:
        model = whisper.load_model("tiny")
        return {
            "service": "stt",
            "status": "healthy",
            "whisper_available": True,
            "message": "STT service is ready with Whisper"
        }
    except Exception as e:
        return {
            "service": "stt",
            "status": "unhealthy",
            "whisper_available": False,
            "error": str(e),
            "message": "STT service is not ready"
        }

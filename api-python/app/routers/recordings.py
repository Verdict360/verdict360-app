from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from typing import Optional
import logging

from app.dependencies import get_current_user
from app.services.audio_processor import audio_processor
from app.services.whisper_service import whisper_service
from app.models.schemas import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recordings", tags=["recordings"])

@router.post("/upload")
async def upload_recording(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    duration_seconds: int = Form(...),
    matter_id: Optional[str] = Form(None),
    recording_type: str = Form("legal_proceeding"),
    attendees: Optional[str] = Form(None),
    recorded_by: Optional[str] = Form(None),
    recording_timestamp: Optional[str] = Form(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Upload and transcribe a legal audio recording
    
    This endpoint:
    1. Validates the audio file
    2. Stores it securely in MinIO
    3. Transcribes it using Whisper
    4. Returns processing results
    """
    try:
        logger.info(f"Processing audio upload: {file.filename} for user {current_user.id}")
        
        # Prepare metadata
        metadata = {
            "title": title,
            "description": description,
            "duration_seconds": duration_seconds,
            "matter_id": matter_id,
            "recording_type": recording_type,
            "attendees": attendees or "",
            "recorded_by": recorded_by or current_user.email,
            "recording_timestamp": recording_timestamp,
            "uploaded_by": current_user.id
        }
        
        # Process recording (this includes transcription)
        result = await audio_processor.process_recording_upload(
            file, metadata, current_user.id
        )
        
        if result["status"] == "failed":
            raise HTTPException(
                status_code=500, 
                detail=f"Recording processing failed: {result.get('error', 'Unknown error')}"
            )
        
        # Return success response
        return {
            "success": True,
            "recording_id": result["recording_id"],
            "status": "transcribed",
            "message": "Recording uploaded and transcribed successfully",
            "processing_summary": {
                "file_size": result["file_info"]["size"],
                "duration_seconds": result["transcription"]["duration_seconds"],
                "word_count": result["transcription"]["word_count"],
                "confidence_score": result["transcription"]["confidence_score"],
                "legal_terms_found": len(result["transcription"]["legal_terms_detected"]),
                "processing_time": result["transcription"]["processing_time"]
            },
            "transcription_preview": result["transcription"]["text"][:500] + "..." if len(result["transcription"]["text"]) > 500 else result["transcription"]["text"],
            "legal_terms_detected": result["transcription"]["legal_terms_detected"][:10],  # Show first 10
            "storage_paths": {
                "recording": result["file_info"]["storage_path"],
                "transcription": result["transcription"]["storage_path"],
                "results": result["results_storage_path"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process recording: {str(e)}")

@router.get("/{recording_id}")
async def get_recording(
    recording_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get recording details and transcription"""
    # For now, return mock data - we'll add database integration later
    return {
        "recording_id": recording_id,
        "status": "transcribed",
        "message": "Recording processed successfully",
        "owner": current_user.id
    }

@router.get("/{recording_id}/transcription")
async def get_transcription(
    recording_id: str,
    format: str = "formatted",  # "formatted" or "raw"
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get transcription for a recording
    
    Formats:
    - formatted: With timestamps and legal formatting
    - raw: Plain text only
    """
    # TODO: Implement actual transcription retrieval from MinIO
    # For now, return mock data
    
    if format == "formatted":
        return {
            "recording_id": recording_id,
            "format": "formatted",
            "transcription": "[00:00:12 - 00:00:18] Good morning, this is a legal consultation for matter MAT-2025-001.\n\n[00:00:19 - 00:00:25] Present are the client, John Smith, and attorney Sarah Advocate.",
            "metadata": {
                "duration_seconds": 1800,
                "word_count": 450,
                "confidence_score": 0.92,
                "legal_terms_detected": ["matter", "consultation", "client", "attorney"]
            }
        }
    else:
        return {
            "recording_id": recording_id,
            "format": "raw",
            "transcription": "Good morning, this is a legal consultation for matter MAT-2025-001. Present are the client, John Smith, and attorney Sarah Advocate.",
            "word_count": 450
        }

@router.get("/{recording_id}/status")
async def get_transcription_status(
    recording_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get transcription processing status"""
    # TODO: Implement actual status checking
    return {
        "recording_id": recording_id,
        "status": "completed",
        "progress": 100,
        "steps": {
            "upload": {"completed": True, "timestamp": "2025-05-30T10:00:00Z"},
            "validation": {"completed": True, "timestamp": "2025-05-30T10:00:01Z"},
            "transcription": {"completed": True, "timestamp": "2025-05-30T10:02:15Z"},
            "storage": {"completed": True, "timestamp": "2025-05-30T10:02:20Z"}
        },
        "estimated_completion": None
    }

@router.get("/whisper/health")
async def whisper_health_check():
    """Check Whisper service health"""
    try:
        health = whisper_service.health_check()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Whisper health check failed: {str(e)}")

@router.get("/whisper/languages")
async def get_supported_languages():
    """Get list of languages supported by Whisper"""
    try:
        languages = whisper_service.get_supported_languages()
        return {
            "supported_languages": languages,
            "default": "en",
            "note": "South African English optimized for legal terminology"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get languages: {str(e)}")

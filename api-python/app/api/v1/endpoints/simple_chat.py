"""
Simple Chat API for Demo Purposes
Provides immediate chat responses without complex database setup
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import uuid
from datetime import datetime

from app.services.ollama_ai_service import ollama_ai_service

router = APIRouter()
logger = logging.getLogger(__name__)

class SimpleChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class SimpleChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    legal_area: Optional[str] = None
    urgency: Optional[str] = None
    confidence: Optional[float] = None

@router.post("/", response_model=SimpleChatResponse)
async def simple_chat(request: SimpleChatRequest):
    """
    Simple chat endpoint for immediate demo responses.
    No database or complex processing required.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing simple chat message: {request.message[:50]}...")
        
        # Get AI response from Ollama AI (Llama 3.2)
        ai_response = await ollama_ai_service.generate_response(
            message=request.message,
            context=[],
            conversation_history="",
            legal_matter=None
        )
        
        return SimpleChatResponse(
            response=ai_response.get('content', 'Unable to generate response'),
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat(),
            legal_area=ai_response.get('legal_area'),
            urgency=ai_response.get('urgency'),
            confidence=ai_response.get('confidence')
        )
        
    except Exception as e:
        logger.error(f"Simple chat error: {str(e)}")
        
        # Check if it's specifically an Ollama connection issue
        error_str = str(e).lower()
        if any(error_indicator in error_str for error_indicator in [
            "connection", "timeout", "refused", "failed", "unreachable", 
            "attempts failed", "cannot connect", "network", "host"
        ]):
            logger.warning("Ollama service appears to be unavailable, falling back to demo responses")
            # Import demo service as fallback
            from app.services.demo_ai_service import demo_ai_service
            try:
                ai_response = await demo_ai_service.generate_response(
                    message=request.message,
                    context=[],
                    conversation_history="",
                    legal_matter=None
                )
                return SimpleChatResponse(
                    response=ai_response.get('content', 'Unable to generate response'),
                    session_id=session_id,
                    timestamp=datetime.utcnow().isoformat(),
                    legal_area=ai_response.get('legal_area'),
                    urgency=ai_response.get('urgency'),
                    confidence=ai_response.get('confidence')
                )
            except Exception as fallback_error:
                logger.error(f"Fallback demo service also failed: {str(fallback_error)}")
        
        raise HTTPException(
            status_code=500,
            detail="I apologise, but I'm experiencing technical difficulties. Please try again in a moment, or contact our support team directly for immediate assistance."
        )

@router.get("/health")
async def chat_health():
    """Health check for chat service"""
    # Test Ollama connection
    ollama_status = await ollama_ai_service.test_connection()
    
    # Import demo service for health check
    from app.services.demo_ai_service import demo_ai_service
    
    return {
        "status": "healthy" if ollama_status else "degraded",
        "service": "simple_chat",
        "timestamp": datetime.utcnow().isoformat(),
        "ollama_available": ollama_status,
        "demo_fallback_available": True,  # Demo service is always available
        "active_models": await ollama_ai_service.list_available_models() if ollama_status else [],
        "message": "Using Ollama AI (Llama 3.2)" if ollama_status else "Using demo AI service (Ollama unavailable)"
    }
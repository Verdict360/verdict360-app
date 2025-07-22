"""
Voice Integration Endpoints
Retell AI and ElevenLabs integration for voice consultations
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Optional, Dict, Any
import logging
import json
from datetime import datetime

from app.models.schemas import (
    VoiceCallRequest, VoiceCallResponse, VoiceCallbackRequest,
    CallTranscriptionRequest, VoiceSettingsRequest
)
from app.services.voice_service import VoiceService
from app.services.conversation_service import ConversationService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
voice_service = VoiceService()
conversation_service = ConversationService()

@router.post("/initiate-call", response_model=VoiceCallResponse)
async def initiate_voice_call(
    request: VoiceCallRequest,
    background_tasks: BackgroundTasks
):
    """
    Initiate a voice call consultation using Retell AI.
    """
    try:
        logger.info(f"Initiating voice call for consultation: {request.consultation_id}")
        
        # Create voice call session
        call_session = await voice_service.create_call_session(
            consultation_id=request.consultation_id,
            client_phone=request.client_phone,
            legal_context=request.legal_context,
            call_type=request.call_type
        )
        
        # Configure legal AI persona for the call
        legal_persona = await voice_service.configure_legal_persona(
            legal_area=request.legal_context.get("legal_area", "general"),
            jurisdiction="South Africa",
            consultation_type=request.call_type
        )
        
        # Initiate call with Retell AI
        retell_response = await voice_service.initiate_retell_call(
            phone_number=request.client_phone,
            call_session_id=call_session.id,
            persona_config=legal_persona,
            webhook_url=f"{request.callback_base_url}/api/v1/voice/callback"
        )
        
        # Update call session with Retell call ID
        await voice_service.update_call_session(
            session_id=call_session.id,
            retell_call_id=retell_response["call_id"],
            status="initiated"
        )
        
        return VoiceCallResponse(
            call_session_id=call_session.id,
            retell_call_id=retell_response["call_id"],
            status="initiated",
            estimated_cost=_calculate_call_cost(request.call_type),
            expected_duration=request.expected_duration_minutes,
            legal_disclaimer="This is a recorded legal consultation. Standard legal advice disclaimers apply."
        )
        
    except Exception as e:
        logger.error(f"Voice call initiation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initiate voice consultation"
        )

@router.post("/callback")
async def handle_voice_callback(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle callbacks from Retell AI voice system.
    """
    try:
        payload = await request.json()
        event_type = payload.get("event_type")
        call_id = payload.get("call_id")
        
        logger.info(f"Voice callback received: {event_type} for call {call_id}")
        
        # Get call session
        call_session = await voice_service.get_call_session_by_retell_id(call_id)
        if not call_session:
            logger.warning(f"Call session not found for Retell call {call_id}")
            return {"status": "session_not_found"}
        
        # Handle different event types
        if event_type == "call_started":
            await voice_service.update_call_session(
                session_id=call_session.id,
                status="active",
                started_at=datetime.utcnow()
            )
            
        elif event_type == "call_ended":
            await voice_service.update_call_session(
                session_id=call_session.id,
                status="completed",
                ended_at=datetime.utcnow(),
                duration_seconds=payload.get("duration_seconds", 0)
            )
            
            # Process call completion in background
            background_tasks.add_task(
                _process_call_completion,
                call_session.id,
                payload
            )
            
        elif event_type == "transcript":
            # Save transcript segment
            await voice_service.save_transcript_segment(
                call_session_id=call_session.id,
                speaker=payload.get("speaker", "unknown"),
                text=payload.get("text", ""),
                timestamp=payload.get("timestamp"),
                confidence=payload.get("confidence", 0.0)
            )
            
            # Check for legal escalation triggers
            if payload.get("speaker") == "user":
                background_tasks.add_task(
                    _check_voice_escalation,
                    call_session.id,
                    payload.get("text", "")
                )
        
        elif event_type == "error":
            await voice_service.update_call_session(
                session_id=call_session.id,
                status="error",
                error_message=payload.get("error_message", "Unknown error")
            )
            
        return {"status": "processed", "call_session_id": call_session.id}
        
    except Exception as e:
        logger.error(f"Voice callback processing error: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/call/{call_session_id}/status")
async def get_call_status(call_session_id: str):
    """
    Get current status of a voice call session.
    """
    try:
        call_session = await voice_service.get_call_session(call_session_id)
        
        if not call_session:
            raise HTTPException(status_code=404, detail="Call session not found")
        
        # Get transcript if available
        transcript = await voice_service.get_call_transcript(call_session_id)
        
        return {
            "call_session_id": call_session.id,
            "status": call_session.status,
            "duration_seconds": call_session.duration_seconds,
            "started_at": call_session.started_at,
            "ended_at": call_session.ended_at,
            "consultation_id": call_session.consultation_id,
            "transcript_available": len(transcript) > 0,
            "transcript_segments": len(transcript),
            "legal_summary_available": call_session.legal_summary is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Call status error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve call status"
        )

@router.get("/call/{call_session_id}/transcript")
async def get_call_transcript(call_session_id: str):
    """
    Get full transcript of a voice call session.
    """
    try:
        transcript = await voice_service.get_call_transcript(call_session_id)
        
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        return {
            "call_session_id": call_session_id,
            "transcript": transcript,
            "total_segments": len(transcript),
            "speakers": list(set([segment["speaker"] for segment in transcript]))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcript retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve call transcript"
        )

@router.post("/text-to-speech")
async def generate_speech(
    text: str,
    voice_id: Optional[str] = "professional_sa_legal",
    format: Optional[str] = "mp3"
):
    """
    Generate speech audio using ElevenLabs for legal content.
    """
    try:
        # Generate audio with legal-appropriate voice
        audio_response = await voice_service.generate_speech(
            text=text,
            voice_id=voice_id,
            output_format=format,
            legal_context=True
        )
        
        return {
            "audio_url": audio_response["audio_url"],
            "duration_seconds": audio_response["duration"],
            "format": format,
            "voice_id": voice_id,
            "character_count": len(text),
            "estimated_cost": _calculate_tts_cost(len(text))
        }
        
    except Exception as e:
        logger.error(f"Text-to-speech error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate speech audio"
        )

@router.post("/voice-settings")
async def update_voice_settings(request: VoiceSettingsRequest):
    """
    Update voice AI settings for legal consultations.
    """
    try:
        settings = await voice_service.update_voice_settings(
            consultation_id=request.consultation_id,
            settings={
                "voice_id": request.voice_id,
                "speaking_rate": request.speaking_rate,
                "legal_formality_level": request.legal_formality_level,
                "south_african_context": request.south_african_context,
                "practice_area_specialization": request.practice_area_specialization
            }
        )
        
        return {
            "consultation_id": request.consultation_id,
            "settings_updated": True,
            "active_settings": settings
        }
        
    except Exception as e:
        logger.error(f"Voice settings update error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update voice settings"
        )

@router.post("/emergency-escalation")
async def emergency_escalation(
    call_session_id: str,
    reason: str,
    background_tasks: BackgroundTasks
):
    """
    Trigger emergency escalation during voice call.
    """
    try:
        # Update call session
        await voice_service.update_call_session(
            session_id=call_session_id,
            status="escalated",
            escalation_reason=reason,
            escalated_at=datetime.utcnow()
        )
        
        # Trigger emergency workflow
        background_tasks.add_task(
            _handle_emergency_escalation,
            call_session_id,
            reason
        )
        
        return {
            "call_session_id": call_session_id,
            "escalation_triggered": True,
            "emergency_contact_initiated": True,
            "message": "Emergency escalation has been triggered. A qualified attorney will be contacted immediately."
        }
        
    except Exception as e:
        logger.error(f"Emergency escalation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to trigger emergency escalation"
        )

# Helper Functions

def _calculate_call_cost(call_type: str) -> float:
    """Calculate estimated call cost based on type and duration."""
    base_rates = {
        "consultation": 15.0,  # R15/minute
        "follow_up": 10.0,     # R10/minute  
        "emergency": 25.0      # R25/minute
    }
    
    return base_rates.get(call_type, 15.0)

def _calculate_tts_cost(character_count: int) -> float:
    """Calculate text-to-speech cost based on character count."""
    # ElevenLabs pricing approximation
    cost_per_1000_chars = 0.30  # $0.30 per 1000 characters
    zar_rate = 18.0  # Approximate ZAR/USD rate
    
    return round((character_count / 1000) * cost_per_1000_chars * zar_rate, 2)

# Background Tasks

async def _process_call_completion(call_session_id: str, callback_payload: Dict):
    """Process call completion and generate legal summary."""
    try:
        # Get full transcript
        transcript = await voice_service.get_call_transcript(call_session_id)
        
        # Generate legal summary
        legal_summary = await voice_service.generate_legal_summary(
            transcript=transcript,
            call_session_id=call_session_id
        )
        
        # Save to consultation record
        call_session = await voice_service.get_call_session(call_session_id)
        if call_session.consultation_id:
            await voice_service.attach_call_to_consultation(
                consultation_id=call_session.consultation_id,
                call_session_id=call_session_id,
                legal_summary=legal_summary
            )
        
        # Bridge to chat system if needed
        if legal_summary.get("follow_up_required"):
            await _bridge_to_chat_system(call_session_id, legal_summary)
        
        logger.info(f"Call completion processed for {call_session_id}")
        
    except Exception as e:
        logger.error(f"Call completion processing failed for {call_session_id}: {str(e)}")

async def _check_voice_escalation(call_session_id: str, transcript_text: str):
    """Check if voice call needs escalation to human lawyer."""
    try:
        escalation_triggers = [
            "emergency",
            "urgent",
            "court tomorrow", 
            "arrest",
            "police",
            "deadline today",
            "criminal charge"
        ]
        
        text_lower = transcript_text.lower()
        
        if any(trigger in text_lower for trigger in escalation_triggers):
            await voice_service.flag_for_escalation(
                call_session_id=call_session_id,
                trigger_text=transcript_text[:200],
                escalation_type="content_based"
            )
            
    except Exception as e:
        logger.error(f"Voice escalation check failed for {call_session_id}: {str(e)}")

async def _handle_emergency_escalation(call_session_id: str, reason: str):
    """Handle emergency escalation workflow."""
    try:
        # This would integrate with emergency contact system
        # For now, log the emergency
        logger.critical(f"EMERGENCY ESCALATION - Call {call_session_id}: {reason}")
        
        # Trigger urgent workflow
        from app.services.workflow_service import workflow_service
        await workflow_service.trigger_webhook(
            "emergency-escalation",
            {
                "call_session_id": call_session_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "priority": "CRITICAL"
            }
        )
        
    except Exception as e:
        logger.error(f"Emergency escalation handling failed: {str(e)}")

async def _bridge_to_chat_system(call_session_id: str, legal_summary: Dict):
    """Bridge voice call to chat system for follow-up."""
    try:
        # Create chat conversation from voice call
        conversation = await conversation_service.create_from_voice_call(
            call_session_id=call_session_id,
            legal_summary=legal_summary
        )
        
        logger.info(f"Voice call {call_session_id} bridged to chat conversation {conversation.id}")
        
    except Exception as e:
        logger.error(f"Voice-to-chat bridge failed for {call_session_id}: {str(e)}")
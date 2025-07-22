"""
Voice Service for Retell AI and ElevenLabs Integration
Handles voice consultations, call management, and speech synthesis
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import httpx

logger = logging.getLogger(__name__)

class VoiceCallSession:
    """Voice call session model"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.consultation_id = kwargs.get('consultation_id')
        self.retell_call_id = kwargs.get('retell_call_id')
        self.client_phone = kwargs['client_phone']
        self.call_type = kwargs.get('call_type', 'consultation')
        self.status = kwargs.get('status', 'initiated')
        self.started_at = kwargs.get('started_at')
        self.ended_at = kwargs.get('ended_at')
        self.duration_seconds = kwargs.get('duration_seconds', 0)
        self.legal_context = kwargs.get('legal_context', {})
        self.legal_summary = kwargs.get('legal_summary')
        self.escalation_reason = kwargs.get('escalation_reason')
        self.escalated_at = kwargs.get('escalated_at')
        self.voice_settings = kwargs.get('voice_settings', {})
        self.error_message = kwargs.get('error_message')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = datetime.utcnow()

class TranscriptSegment:
    """Transcript segment model"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.voice_call_id = kwargs['voice_call_id']
        self.speaker = kwargs['speaker']  # 'user' or 'assistant'
        self.text = kwargs['text']
        self.timestamp_seconds = kwargs.get('timestamp_seconds', 0.0)
        self.confidence_score = kwargs.get('confidence_score', 0.0)
        self.created_at = kwargs.get('created_at', datetime.utcnow())

class VoiceService:
    """Service for managing voice consultations and speech synthesis"""
    
    def __init__(self):
        # In-memory storage (replace with database in production)
        self._call_sessions = {}  # call_session_id -> VoiceCallSession
        self._transcripts = {}    # call_session_id -> List[TranscriptSegment]
        
        # API configurations (these would come from environment variables)
        self.retell_api_key = "your_retell_api_key"
        self.retell_api_url = "https://api.retellai.com/v1"
        self.elevenlabs_api_key = "your_elevenlabs_api_key"
        self.elevenlabs_api_url = "https://api.elevenlabs.io/v1"

    async def create_call_session(
        self,
        consultation_id: Optional[str],
        client_phone: str,
        legal_context: Dict[str, Any],
        call_type: str = "consultation"
    ) -> VoiceCallSession:
        """Create a new voice call session"""
        try:
            call_session = VoiceCallSession(
                consultation_id=consultation_id,
                client_phone=client_phone,
                legal_context=legal_context,
                call_type=call_type
            )
            
            self._call_sessions[call_session.id] = call_session
            self._transcripts[call_session.id] = []
            
            logger.info(f"Created voice call session {call_session.id}")
            return call_session
            
        except Exception as e:
            logger.error(f"Failed to create call session: {str(e)}")
            raise

    async def configure_legal_persona(
        self,
        legal_area: str = "general",
        jurisdiction: str = "South Africa",
        consultation_type: str = "consultation"
    ) -> Dict[str, Any]:
        """Configure AI persona for legal consultations"""
        try:
            # Base legal persona configuration
            persona_config = {
                "voice_id": "professional_sa_legal",
                "speaking_rate": 1.0,
                "language": "en-ZA",  # South African English
                "system_prompt": self._generate_legal_system_prompt(
                    legal_area, jurisdiction, consultation_type
                ),
                "personality_traits": {
                    "professionalism": "high",
                    "empathy": "medium",
                    "formality": "professional",
                    "confidence": "balanced"
                },
                "conversation_settings": {
                    "max_duration_minutes": 60,
                    "silence_timeout_seconds": 10,
                    "interruption_handling": "polite",
                    "escalation_triggers": [
                        "emergency", "urgent", "court", "arrest", "police"
                    ]
                },
                "legal_disclaimers": {
                    "opening": "This is an AI legal assistant. This consultation does not constitute formal legal advice.",
                    "closing": "For specific legal matters, please consult with a qualified South African attorney."
                }
            }
            
            return persona_config
            
        except Exception as e:
            logger.error(f"Failed to configure legal persona: {str(e)}")
            raise

    async def initiate_retell_call(
        self,
        phone_number: str,
        call_session_id: str,
        persona_config: Dict[str, Any],
        webhook_url: str
    ) -> Dict[str, Any]:
        """Initiate call with Retell AI"""
        try:
            # Prepare call configuration
            call_config = {
                "phone_number": phone_number,
                "persona": persona_config,
                "webhook_url": webhook_url,
                "metadata": {
                    "call_session_id": call_session_id,
                    "service": "verdict360_legal",
                    "jurisdiction": "south_africa"
                }
            }
            
            # In a real implementation, this would make an HTTP request to Retell AI
            # For now, simulate the response
            mock_response = {
                "call_id": f"retell_{uuid.uuid4().hex[:8]}",
                "status": "initiated",
                "estimated_cost": 2.50,  # ZAR per minute
                "webhook_registered": True
            }
            
            logger.info(f"Initiated Retell AI call for session {call_session_id}")
            return mock_response
            
        except Exception as e:
            logger.error(f"Failed to initiate Retell call: {str(e)}")
            raise

    async def get_call_session(self, call_session_id: str) -> Optional[VoiceCallSession]:
        """Get call session by ID"""
        return self._call_sessions.get(call_session_id)

    async def get_call_session_by_retell_id(self, retell_call_id: str) -> Optional[VoiceCallSession]:
        """Get call session by Retell call ID"""
        for session in self._call_sessions.values():
            if session.retell_call_id == retell_call_id:
                return session
        return None

    async def update_call_session(
        self,
        session_id: str,
        **updates
    ) -> bool:
        """Update call session details"""
        try:
            session = self._call_sessions.get(session_id)
            if not session:
                return False
            
            for key, value in updates.items():
                if hasattr(session, key) and value is not None:
                    setattr(session, key, value)
            
            session.updated_at = datetime.utcnow()
            
            logger.info(f"Updated call session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update call session: {str(e)}")
            return False

    async def save_transcript_segment(
        self,
        call_session_id: str,
        speaker: str,
        text: str,
        timestamp: Optional[float] = None,
        confidence: float = 0.0
    ) -> TranscriptSegment:
        """Save transcript segment from voice call"""
        try:
            segment = TranscriptSegment(
                voice_call_id=call_session_id,
                speaker=speaker,
                text=text,
                timestamp_seconds=timestamp or 0.0,
                confidence_score=confidence
            )
            
            if call_session_id not in self._transcripts:
                self._transcripts[call_session_id] = []
            
            self._transcripts[call_session_id].append(segment)
            
            logger.info(f"Saved transcript segment for call {call_session_id}")
            return segment
            
        except Exception as e:
            logger.error(f"Failed to save transcript segment: {str(e)}")
            raise

    async def get_call_transcript(self, call_session_id: str) -> List[Dict[str, Any]]:
        """Get full transcript for a call session"""
        try:
            segments = self._transcripts.get(call_session_id, [])
            
            return [
                {
                    "speaker": segment.speaker,
                    "text": segment.text,
                    "timestamp": segment.timestamp_seconds,
                    "confidence": segment.confidence_score,
                    "created_at": segment.created_at.isoformat()
                }
                for segment in sorted(segments, key=lambda s: s.timestamp_seconds)
            ]
            
        except Exception as e:
            logger.error(f"Failed to get call transcript: {str(e)}")
            return []

    async def generate_speech(
        self,
        text: str,
        voice_id: str = "professional_sa_legal",
        output_format: str = "mp3",
        legal_context: bool = True
    ) -> Dict[str, Any]:
        """Generate speech using ElevenLabs"""
        try:
            # In a real implementation, this would call ElevenLabs API
            # For now, simulate the response
            
            # Prepare text for legal context
            if legal_context:
                text = self._prepare_legal_text_for_speech(text)
            
            mock_response = {
                "audio_url": f"https://api.elevenlabs.io/v1/audio/generated_{uuid.uuid4().hex[:8]}.{output_format}",
                "duration": len(text) * 0.1,  # Rough duration estimate
                "voice_id": voice_id,
                "format": output_format,
                "legal_optimized": legal_context
            }
            
            logger.info(f"Generated speech for {len(text)} characters")
            return mock_response
            
        except Exception as e:
            logger.error(f"Failed to generate speech: {str(e)}")
            raise

    async def generate_legal_summary(
        self,
        transcript: List[Dict[str, Any]],
        call_session_id: str
    ) -> Dict[str, Any]:
        """Generate legal summary from call transcript"""
        try:
            # Extract key information from transcript
            user_segments = [
                segment for segment in transcript 
                if segment["speaker"] == "user"
            ]
            
            assistant_segments = [
                segment for segment in transcript
                if segment["speaker"] == "assistant"  
            ]
            
            # Analyze transcript content
            user_text = " ".join([s["text"] for s in user_segments])
            legal_area = self._classify_legal_area(user_text)
            urgency = self._assess_urgency(user_text)
            
            legal_summary = {
                "call_session_id": call_session_id,
                "duration_minutes": transcript[-1]["timestamp"] / 60 if transcript else 0,
                "legal_area": legal_area,
                "urgency_level": urgency,
                "summary": self._generate_consultation_summary(user_text),
                "key_concerns": self._extract_key_concerns(user_text),
                "legal_advice_given": self._extract_advice_given(assistant_segments),
                "follow_up_required": self._requires_follow_up(user_text),
                "recommended_actions": self._recommend_actions(legal_area, user_text),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated legal summary for call {call_session_id}")
            return legal_summary
            
        except Exception as e:
            logger.error(f"Failed to generate legal summary: {str(e)}")
            return {}

    async def flag_for_escalation(
        self,
        call_session_id: str,
        trigger_text: str,
        escalation_type: str
    ) -> bool:
        """Flag call session for human escalation"""
        try:
            session = self._call_sessions.get(call_session_id)
            if not session:
                return False
            
            session.escalation_reason = f"{escalation_type}: {trigger_text}"
            session.escalated_at = datetime.utcnow()
            session.status = "escalated"
            
            logger.warning(f"Call session {call_session_id} flagged for escalation: {escalation_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to flag call for escalation: {str(e)}")
            return False

    async def update_voice_settings(
        self,
        consultation_id: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update voice settings for consultation"""
        try:
            # Find call session by consultation ID
            for session in self._call_sessions.values():
                if session.consultation_id == consultation_id:
                    session.voice_settings.update(settings)
                    session.updated_at = datetime.utcnow()
                    break
            
            return settings
            
        except Exception as e:
            logger.error(f"Failed to update voice settings: {str(e)}")
            raise

    async def attach_call_to_consultation(
        self,
        consultation_id: str,
        call_session_id: str,
        legal_summary: Dict[str, Any]
    ):
        """Attach call session to consultation record"""
        try:
            session = self._call_sessions.get(call_session_id)
            if session:
                session.consultation_id = consultation_id
                session.legal_summary = legal_summary
                session.updated_at = datetime.utcnow()
                
                logger.info(f"Attached call {call_session_id} to consultation {consultation_id}")
            
        except Exception as e:
            logger.error(f"Failed to attach call to consultation: {str(e)}")

    # Helper methods

    def _generate_legal_system_prompt(
        self, 
        legal_area: str, 
        jurisdiction: str, 
        consultation_type: str
    ) -> str:
        """Generate system prompt for legal AI persona"""
        
        base_prompt = f"""
        You are a professional South African legal AI assistant conducting a {consultation_type}.
        
        Specialization: {legal_area} law in {jurisdiction}
        
        Guidelines:
        1. Maintain professional, empathetic communication
        2. Provide general legal guidance based on South African law
        3. Always include appropriate legal disclaimers
        4. Identify urgent matters requiring immediate human lawyer intervention
        5. Ask clarifying questions to understand the client's situation
        6. Provide clear, actionable next steps
        7. Use South African legal terminology and references
        
        Important: You are NOT providing formal legal advice. Always remind clients
        to consult with qualified South African attorneys for specific legal matters.
        """
        
        return base_prompt.strip()

    def _prepare_legal_text_for_speech(self, text: str) -> str:
        """Prepare text for speech synthesis in legal context"""
        # Add pauses for legal terms and citations
        legal_terms = [
            "Constitutional Court", "Supreme Court of Appeal", 
            "High Court", "Act", "Constitution"
        ]
        
        processed_text = text
        for term in legal_terms:
            processed_text = processed_text.replace(
                term, 
                f"<break time='0.3s'/>{term}<break time='0.3s'/>"
            )
        
        return processed_text

    def _classify_legal_area(self, text: str) -> str:
        """Classify legal area from transcript text"""
        text_lower = text.lower()
        
        area_keywords = {
            "criminal": ["police", "arrest", "charge", "crime", "theft", "assault"],
            "family": ["divorce", "custody", "child", "marriage", "maintenance"],
            "commercial": ["business", "contract", "company", "partnership", "trade"],
            "property": ["property", "transfer", "deed", "bond", "mortgage"],
            "civil": ["damages", "dispute", "claim", "liability", "negligence"],
            "employment": ["workplace", "dismissal", "employment", "salary", "unfair"]
        }
        
        for area, keywords in area_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return area
        
        return "general"

    def _assess_urgency(self, text: str) -> str:
        """Assess urgency level from transcript"""
        text_lower = text.lower()
        
        critical_keywords = ["emergency", "arrest", "court tomorrow", "today"]
        high_keywords = ["urgent", "deadline", "court date", "police"]
        
        if any(keyword in text_lower for keyword in critical_keywords):
            return "critical"
        elif any(keyword in text_lower for keyword in high_keywords):
            return "high"
        else:
            return "normal"

    def _generate_consultation_summary(self, text: str) -> str:
        """Generate consultation summary from user text"""
        # In a real implementation, this would use NLP to summarize
        return f"Client consultation regarding: {text[:200]}..."

    def _extract_key_concerns(self, text: str) -> List[str]:
        """Extract key legal concerns from text"""
        # Simplified extraction - would use NLP in production
        concerns = []
        if "court" in text.lower():
            concerns.append("Court proceedings")
        if "money" in text.lower() or "payment" in text.lower():
            concerns.append("Financial matters")
        if "contract" in text.lower():
            concerns.append("Contractual issues")
        
        return concerns[:5]  # Limit to top 5

    def _extract_advice_given(self, assistant_segments: List[Dict]) -> List[str]:
        """Extract advice given by AI assistant"""
        advice = []
        for segment in assistant_segments[-3:]:  # Last 3 assistant messages
            if len(segment["text"]) > 50:  # Substantial advice
                advice.append(segment["text"][:100] + "...")
        
        return advice

    def _requires_follow_up(self, text: str) -> bool:
        """Determine if follow-up consultation is required"""
        follow_up_indicators = [
            "complex", "ongoing", "need more time", "documents", 
            "review", "follow up", "next steps"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in follow_up_indicators)

    def _recommend_actions(self, legal_area: str, text: str) -> List[str]:
        """Recommend actions based on legal area and content"""
        actions = []
        
        if legal_area == "criminal":
            actions.extend([
                "Consult with criminal defense attorney immediately",
                "Gather all relevant documentation",
                "Prepare timeline of events"
            ])
        elif legal_area == "family":
            actions.extend([
                "Collect marriage and financial documents",
                "Consider mediation options",
                "Consult with family law specialist"
            ])
        elif legal_area == "commercial":
            actions.extend([
                "Review all contracts and agreements",
                "Gather business financial records",
                "Consult with commercial law attorney"
            ])
        else:
            actions.extend([
                "Consult with qualified South African attorney",
                "Gather relevant documentation",
                "Prepare detailed statement of facts"
            ])
        
        return actions[:5]  # Limit to top 5 actions

# Global service instance
voice_service = VoiceService()
"""
Database service for voice call persistence and management
Integrates with PostgreSQL for production-ready voice data storage
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from app.models.voice import (
    VoiceCall, VoiceTranscript, VoiceSynthesis, 
    VoiceCallAnalytics, VoiceEscalation
)

logger = logging.getLogger(__name__)

class VoiceDbService:
    """Database service for voice call operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    # Voice Call Management
    
    async def create_voice_call(
        self,
        consultation_id: Optional[str],
        client_phone: str,
        legal_context: Dict[str, Any],
        call_type: str = "consultation"
    ) -> VoiceCall:
        """Create a new voice call record"""
        try:
            voice_call = VoiceCall(
                consultation_id=consultation_id,
                client_phone=client_phone,
                formatted_phone=self._format_sa_phone_number(client_phone),
                legal_context=legal_context,
                call_type=call_type,
                legal_area=legal_context.get("legal_area"),
                urgency_level=legal_context.get("urgency_level", "normal")
            )
            
            self.db.add(voice_call)
            self.db.commit()
            self.db.refresh(voice_call)
            
            logger.info(f"Created voice call record {voice_call.id}")
            return voice_call
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create voice call: {str(e)}")
            raise

    async def get_voice_call(self, call_id: str) -> Optional[VoiceCall]:
        """Get voice call by ID"""
        return self.db.query(VoiceCall).filter(VoiceCall.id == call_id).first()

    async def get_voice_call_by_retell_id(self, retell_call_id: str) -> Optional[VoiceCall]:
        """Get voice call by Retell AI call ID"""
        return self.db.query(VoiceCall).filter(
            VoiceCall.retell_call_id == retell_call_id
        ).first()

    async def update_voice_call(
        self,
        call_id: str,
        **updates
    ) -> bool:
        """Update voice call with provided fields"""
        try:
            call = await self.get_voice_call(call_id)
            if not call:
                return False
            
            for key, value in updates.items():
                if hasattr(call, key) and value is not None:
                    setattr(call, key, value)
            
            call.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated voice call {call_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update voice call {call_id}: {str(e)}")
            return False

    async def mark_call_completed(
        self,
        call_id: str,
        duration_seconds: int,
        legal_summary: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark call as completed with summary"""
        try:
            return await self.update_voice_call(
                call_id,
                status="completed",
                ended_at=datetime.utcnow(),
                duration_seconds=duration_seconds,
                legal_summary=legal_summary
            )
        except Exception as e:
            logger.error(f"Failed to mark call completed: {str(e)}")
            return False

    # Transcript Management
    
    async def save_transcript_segment(
        self,
        call_id: str,
        speaker: str,
        text: str,
        timestamp: float = 0.0,
        confidence: float = 0.0
    ) -> VoiceTranscript:
        """Save transcript segment to database"""
        try:
            transcript = VoiceTranscript(
                voice_call_id=call_id,
                speaker=speaker,
                text=text,
                timestamp_seconds=timestamp,
                confidence_score=confidence,
                contains_legal_terms=self._detect_legal_terms(text)
            )
            
            # Detect urgency indicators
            urgency_indicators = self._extract_urgency_indicators(text)
            if urgency_indicators:
                transcript.urgency_indicators = urgency_indicators
            
            # Detect escalation triggers
            escalation_triggers = self._extract_escalation_triggers(text)
            if escalation_triggers:
                transcript.escalation_triggers = escalation_triggers
            
            self.db.add(transcript)
            self.db.commit()
            self.db.refresh(transcript)
            
            logger.debug(f"Saved transcript segment for call {call_id}")
            return transcript
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save transcript segment: {str(e)}")
            raise

    async def get_call_transcript(self, call_id: str) -> List[Dict[str, Any]]:
        """Get full transcript for a call"""
        try:
            segments = self.db.query(VoiceTranscript).filter(
                VoiceTranscript.voice_call_id == call_id
            ).order_by(VoiceTranscript.timestamp_seconds).all()
            
            return [
                {
                    "id": segment.id,
                    "speaker": segment.speaker,
                    "text": segment.text,
                    "timestamp": segment.timestamp_seconds,
                    "confidence": segment.confidence_score,
                    "created_at": segment.created_at.isoformat(),
                    "contains_legal_terms": segment.contains_legal_terms,
                    "urgency_indicators": segment.urgency_indicators,
                    "escalation_triggers": segment.escalation_triggers
                }
                for segment in segments
            ]
            
        except Exception as e:
            logger.error(f"Failed to get call transcript: {str(e)}")
            return []

    # Voice Synthesis Management
    
    async def record_voice_synthesis(
        self,
        call_id: Optional[str],
        text_input: str,
        voice_id: str,
        audio_format: str,
        duration_seconds: Optional[float],
        character_count: int,
        estimated_cost: Optional[float] = None,
        audio_data_path: Optional[str] = None,
        audio_base64: Optional[str] = None
    ) -> VoiceSynthesis:
        """Record voice synthesis operation"""
        try:
            synthesis = VoiceSynthesis(
                voice_call_id=call_id,
                text_input=text_input,
                voice_id=voice_id,
                audio_format=audio_format,
                duration_seconds=duration_seconds,
                character_count=character_count,
                estimated_cost=estimated_cost,
                audio_data_path=audio_data_path,
                audio_base64=audio_base64 if len(audio_base64 or "") < 1000000 else None,  # Limit base64 size
                legal_optimized=True,
                legal_terminology_used=self._extract_legal_terms(text_input)
            )
            
            self.db.add(synthesis)
            self.db.commit()
            self.db.refresh(synthesis)
            
            logger.info(f"Recorded voice synthesis for {character_count} characters")
            return synthesis
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to record voice synthesis: {str(e)}")
            raise

    # Analytics and Reporting
    
    async def create_call_analytics(
        self,
        call_id: str,
        transcript: List[Dict[str, Any]]
    ) -> VoiceCallAnalytics:
        """Generate and store call analytics"""
        try:
            user_segments = [s for s in transcript if s["speaker"] == "user"]
            assistant_segments = [s for s in transcript if s["speaker"] == "assistant"]
            
            # Calculate metrics
            user_words = sum(len(s["text"].split()) for s in user_segments)
            assistant_words = sum(len(s["text"].split()) for s in assistant_segments)
            total_words = user_words + assistant_words
            
            average_confidence = sum(s["confidence"] for s in transcript) / len(transcript) if transcript else 0.0
            
            # Extract legal terms and classify legal area
            all_text = " ".join([s["text"] for s in transcript])
            legal_terms = self._extract_legal_terms(all_text)
            legal_area = self._classify_legal_area(all_text)
            urgency_score = self._calculate_urgency_score(all_text)
            
            analytics = VoiceCallAnalytics(
                voice_call_id=call_id,
                total_words_spoken=total_words,
                user_words=user_words,
                assistant_words=assistant_words,
                average_confidence=average_confidence,
                legal_terms_mentioned=legal_terms,
                legal_area_classification=legal_area,
                urgency_score=urgency_score,
                consultation_booked=self._detect_consultation_booking(all_text),
                follow_up_required=self._detect_follow_up_needed(all_text)
            )\n            \n            self.db.add(analytics)\n            self.db.commit()\n            self.db.refresh(analytics)\n            \n            logger.info(f"Created analytics for call {call_id}")\n            return analytics\n            \n        except Exception as e:\n            self.db.rollback()\n            logger.error(f"Failed to create call analytics: {str(e)}")\n            raise

    async def create_escalation(
        self,
        call_id: str,
        escalation_type: str,
        trigger_text: str,
        urgency_level: str = "normal"
    ) -> VoiceEscalation:
        """Create escalation record"""
        try:
            escalation = VoiceEscalation(
                voice_call_id=call_id,
                escalation_type=escalation_type,
                trigger_text=trigger_text[:1000],  # Limit length
                urgency_level=urgency_level
            )
            
            self.db.add(escalation)
            self.db.commit()
            self.db.refresh(escalation)
            
            # Update call status
            await self.update_voice_call(
                call_id,
                status="escalated",
                escalation_reason=f"{escalation_type}: {trigger_text[:200]}",
                escalated_at=datetime.utcnow()
            )
            
            logger.warning(f"Created escalation {escalation.id} for call {call_id}")
            return escalation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create escalation: {str(e)}")
            raise

    # Query and Reporting Methods
    
    async def get_recent_calls(
        self,
        limit: int = 50,
        status: Optional[str] = None,
        legal_area: Optional[str] = None
    ) -> List[VoiceCall]:
        """Get recent voice calls with optional filters"""
        query = self.db.query(VoiceCall).order_by(desc(VoiceCall.created_at))
        
        if status:
            query = query.filter(VoiceCall.status == status)
        if legal_area:
            query = query.filter(VoiceCall.legal_area == legal_area)
        
        return query.limit(limit).all()

    async def get_calls_requiring_attention(self) -> List[VoiceCall]:
        """Get calls that need attention (escalated, failed, etc.)"""
        return self.db.query(VoiceCall).filter(
            or_(
                VoiceCall.status == "escalated",
                VoiceCall.status == "failed",
                and_(
                    VoiceCall.status == "active",
                    VoiceCall.started_at < datetime.utcnow() - timedelta(hours=1)
                )
            )
        ).order_by(desc(VoiceCall.urgency_level), desc(VoiceCall.created_at)).all()

    async def get_daily_call_stats(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get daily statistics for voice calls"""
        target_date = date or datetime.utcnow().date()
        
        calls = self.db.query(VoiceCall).filter(
            VoiceCall.created_at >= target_date,
            VoiceCall.created_at < target_date + timedelta(days=1)
        ).all()
        
        total_calls = len(calls)
        completed_calls = len([c for c in calls if c.status == "completed"])
        escalated_calls = len([c for c in calls if c.status == "escalated"])
        
        total_duration = sum(c.duration_seconds or 0 for c in calls)
        
        legal_areas = {}
        for call in calls:
            area = call.legal_area or "other"
            legal_areas[area] = legal_areas.get(area, 0) + 1
        
        return {
            "date": target_date.isoformat(),
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "escalated_calls": escalated_calls,
            "completion_rate": completed_calls / total_calls if total_calls > 0 else 0,
            "total_duration_minutes": total_duration // 60,
            "average_duration_minutes": (total_duration // 60) // total_calls if total_calls > 0 else 0,
            "legal_areas": legal_areas
        }

    # Helper Methods
    
    def _format_sa_phone_number(self, phone_number: str) -> str:
        """Format phone number for SA standards"""
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        if cleaned.startswith('27'):
            return f"+{cleaned}"
        elif cleaned.startswith('0'):
            return f"+27{cleaned[1:]}"
        elif len(cleaned) == 9:
            return f"+27{cleaned}"
        else:
            return phone_number

    def _detect_legal_terms(self, text: str) -> bool:
        """Detect if text contains legal terminology"""
        legal_terms = [
            "court", "judge", "attorney", "lawyer", "legal", "law", "statute", 
            "constitution", "contract", "agreement", "liability", "damages",
            "criminal", "civil", "commercial", "family", "property"
        ]
        
        text_lower = text.lower()
        return any(term in text_lower for term in legal_terms)

    def _extract_legal_terms(self, text: str) -> List[str]:
        """Extract legal terms found in text"""
        legal_terms = [
            "constitutional court", "supreme court of appeal", "high court",
            "criminal law", "civil law", "commercial law", "family law",
            "contract", "agreement", "liability", "damages", "negligence",
            "constitutional", "statute", "act", "regulation"
        ]
        
        text_lower = text.lower()
        found_terms = [term for term in legal_terms if term in text_lower]
        return found_terms

    def _extract_urgency_indicators(self, text: str) -> List[str]:
        """Extract urgency indicators from text"""
        urgency_words = [
            "urgent", "emergency", "immediately", "asap", "today", 
            "tomorrow", "deadline", "court date", "arrest"
        ]
        
        text_lower = text.lower()
        found_indicators = [word for word in urgency_words if word in text_lower]
        return found_indicators

    def _extract_escalation_triggers(self, text: str) -> List[str]:
        """Extract escalation trigger phrases"""
        triggers = [
            "emergency", "arrest", "police", "court tomorrow", 
            "criminal charge", "urgent legal matter", "immediate help"
        ]
        
        text_lower = text.lower()
        found_triggers = [trigger for trigger in triggers if trigger in text_lower]
        return found_triggers

    def _classify_legal_area(self, text: str) -> str:
        """Classify legal area from text"""
        text_lower = text.lower()
        
        area_keywords = {
            "criminal": ["police", "arrest", "charge", "crime", "theft", "assault", "criminal"],
            "family": ["divorce", "custody", "child", "marriage", "maintenance", "family"],
            "commercial": ["business", "contract", "company", "partnership", "trade", "commercial"],
            "property": ["property", "transfer", "deed", "bond", "mortgage", "real estate"],
            "civil": ["damages", "dispute", "claim", "liability", "negligence", "civil"],
            "employment": ["workplace", "dismissal", "employment", "salary", "unfair", "labor"]
        }
        
        for area, keywords in area_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return area
        
        return "general"

    def _calculate_urgency_score(self, text: str) -> float:
        """Calculate urgency score from 0.0 to 1.0"""
        text_lower = text.lower()
        
        critical_words = ["emergency", "arrest", "court tomorrow", "today"]
        high_words = ["urgent", "deadline", "court date", "police", "immediately"]
        medium_words = ["soon", "quick", "asap", "important"]
        
        score = 0.0
        
        # Critical indicators
        for word in critical_words:
            if word in text_lower:
                score += 0.3
        
        # High priority indicators
        for word in high_words:
            if word in text_lower:
                score += 0.2
        
        # Medium priority indicators
        for word in medium_words:
            if word in text_lower:
                score += 0.1
        
        return min(score, 1.0)

    def _detect_consultation_booking(self, text: str) -> bool:
        """Detect if consultation was booked during call"""
        booking_indicators = [
            "book", "schedule", "appointment", "meeting", "consultation",
            "calendar", "available", "time slot"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in booking_indicators)

    def _detect_follow_up_needed(self, text: str) -> bool:
        """Detect if follow-up is needed"""
        follow_up_indicators = [
            "follow up", "call back", "more information", "documents",
            "review", "next steps", "additional", "further"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in follow_up_indicators)
"""
Conversation Service for Legal Chat Management
Handles chat sessions, messages, and legal context integration
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.models.chat_schemas import ConversationSummary, MessageResponse
from app.services.legal_quality_assurance import qa_service
from app.utils.south_african_legal import extract_legal_terms, extract_legal_citations

logger = logging.getLogger(__name__)

class Conversation:
    """Conversation model for in-memory representation"""
    def __init__(self, id: str, session_id: str, user_id: str, 
                 title: str = None, legal_matter_context: Dict = None,
                 created_at: datetime = None):
        self.id = id
        self.session_id = session_id
        self.user_id = user_id
        self.title = title
        self.legal_matter_context = legal_matter_context or {}
        self.message_count = 0
        self.last_message_content = ""
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.status = "active"
        
    def get_recent_context(self, limit: int = 5) -> str:
        """Get recent conversation context for AI model"""
        # This would fetch from database in a real implementation
        # For now, return a placeholder context
        return f"Recent context from conversation {self.session_id} with {self.message_count} messages"

class Message:
    """Message model for in-memory representation"""
    def __init__(self, id: str, conversation_id: str, content: str,
                 message_type: str, metadata: Dict = None, created_at: datetime = None):
        self.id = id
        self.conversation_id = conversation_id
        self.content = content
        self.message_type = message_type  # 'user' or 'assistant'
        self.metadata = metadata or {}
        self.qa_score = 0.0
        self.qa_metadata = {}
        self.created_at = created_at or datetime.utcnow()

class ConversationService:
    """Service for managing legal conversations and messages"""
    
    def __init__(self):
        # In a real implementation, these would be database operations
        self._conversations = {}  # session_id -> Conversation
        self._messages = {}       # conversation_id -> List[Message]
        
    async def get_or_create_conversation(
        self, 
        session_id: str, 
        user_id: str, 
        legal_matter_context: Optional[Dict] = None
    ) -> Conversation:
        """Get existing conversation or create new one"""
        try:
            if session_id in self._conversations:
                conversation = self._conversations[session_id]
                conversation.updated_at = datetime.utcnow()
                return conversation
            
            # Create new conversation
            conversation_id = str(uuid.uuid4())
            conversation = Conversation(
                id=conversation_id,
                session_id=session_id,
                user_id=user_id,
                title=self._generate_conversation_title(legal_matter_context),
                legal_matter_context=legal_matter_context
            )
            
            self._conversations[session_id] = conversation
            self._messages[conversation_id] = []
            
            logger.info(f"Created new conversation {conversation_id} for session {session_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to get/create conversation: {str(e)}")
            raise

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        for conversation in self._conversations.values():
            if conversation.id == conversation_id:
                return conversation
        return None

    async def get_conversation_by_session(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID"""
        return self._conversations.get(session_id)

    async def save_message(
        self,
        conversation_id: str,
        content: str,
        message_type: str,
        metadata: Dict = None
    ) -> Message:
        """Save a message to conversation"""
        try:
            message_id = str(uuid.uuid4())
            message = Message(
                id=message_id,
                conversation_id=conversation_id,
                content=content,
                message_type=message_type,
                metadata=metadata or {}
            )
            
            # Add to messages list
            if conversation_id not in self._messages:
                self._messages[conversation_id] = []
            
            self._messages[conversation_id].append(message)
            
            # Update conversation metadata
            await self._update_conversation_after_message(conversation_id, content, message_type)
            
            # Extract legal context if assistant message
            if message_type == "assistant":
                await self._extract_legal_context(message)
            
            logger.info(f"Saved message {message_id} to conversation {conversation_id}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}")
            raise

    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for a conversation"""
        try:
            messages = self._messages.get(conversation_id, [])
            
            # Sort by creation time and apply pagination
            sorted_messages = sorted(messages, key=lambda m: m.created_at)
            return sorted_messages[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Failed to get conversation messages: {str(e)}")
            return []

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """Get all conversations for a user"""
        try:
            user_conversations = [
                conv for conv in self._conversations.values()
                if conv.user_id == user_id
            ]
            
            # Sort by update time (most recent first)
            sorted_conversations = sorted(
                user_conversations, 
                key=lambda c: c.updated_at, 
                reverse=True
            )
            
            return sorted_conversations[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Failed to get user conversations: {str(e)}")
            return []

    async def update_conversation_status(
        self,
        conversation_id: str,
        status: str,
        escalation_reason: Optional[str] = None
    ):
        """Update conversation status (e.g., escalated)"""
        try:
            for conversation in self._conversations.values():
                if conversation.id == conversation_id:
                    conversation.status = status
                    conversation.updated_at = datetime.utcnow()
                    
                    if escalation_reason:
                        conversation.escalation_reason = escalation_reason
                        conversation.escalated_at = datetime.utcnow()
                    
                    logger.info(f"Updated conversation {conversation_id} status to {status}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update conversation status: {str(e)}")
            return False

    async def update_message_qa_score(
        self,
        message_id: str,
        qa_score: float,
        qa_metadata: Dict = None
    ):
        """Update message quality assurance score"""
        try:
            # Find message in all conversations
            for messages_list in self._messages.values():
                for message in messages_list:
                    if message.id == message_id:
                        message.qa_score = qa_score
                        message.qa_metadata = qa_metadata or {}
                        
                        logger.info(f"Updated QA score for message {message_id}: {qa_score}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update message QA score: {str(e)}")
            return False

    async def create_from_voice_call(
        self,
        call_session_id: str,
        legal_summary: Dict
    ) -> Conversation:
        """Create chat conversation from voice call session"""
        try:
            session_id = f"voice_{call_session_id}"
            user_id = legal_summary.get("client_id", "unknown")
            
            # Create conversation with voice call context
            legal_context = {
                "source": "voice_call",
                "call_session_id": call_session_id,
                "legal_area": legal_summary.get("legal_area"),
                "matter_summary": legal_summary.get("summary", ""),
                "follow_up_required": legal_summary.get("follow_up_required", False)
            }
            
            conversation = await self.get_or_create_conversation(
                session_id=session_id,
                user_id=user_id,
                legal_matter_context=legal_context
            )
            
            # Add voice call summary as first message
            await self.save_message(
                conversation_id=conversation.id,
                content=f"Voice consultation summary: {legal_summary.get('summary', '')}",
                message_type="assistant",
                metadata={
                    "source": "voice_call_summary",
                    "call_session_id": call_session_id
                }
            )
            
            logger.info(f"Created chat conversation from voice call {call_session_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create conversation from voice call: {str(e)}")
            raise

    # Helper methods

    def _generate_conversation_title(self, legal_context: Optional[Dict]) -> str:
        """Generate a descriptive title for the conversation"""
        if not legal_context:
            return "Legal Consultation"
        
        legal_area = legal_context.get("legal_area", "general")
        
        title_map = {
            "criminal": "Criminal Law Consultation",
            "civil": "Civil Law Matter",
            "commercial": "Commercial Law Consultation",
            "family": "Family Law Matter",
            "property": "Property Law Consultation",
            "constitutional": "Constitutional Law Matter",
            "employment": "Employment Law Consultation"
        }
        
        return title_map.get(legal_area, "Legal Consultation")

    async def _update_conversation_after_message(
        self,
        conversation_id: str,
        content: str,
        message_type: str
    ):
        """Update conversation metadata after new message"""
        try:
            for conversation in self._conversations.values():
                if conversation.id == conversation_id:
                    conversation.message_count += 1
                    conversation.last_message_content = content[:200] + "..." if len(content) > 200 else content
                    conversation.updated_at = datetime.utcnow()
                    break
                    
        except Exception as e:
            logger.error(f"Failed to update conversation after message: {str(e)}")

    async def _extract_legal_context(self, message: Message):
        """Extract legal citations and terms from assistant messages"""
        try:
            if message.message_type != "assistant":
                return
            
            # Extract legal citations
            citations = extract_legal_citations(message.content)
            if citations:
                message.metadata["legal_citations"] = citations
            
            # Extract legal terms
            legal_terms = extract_legal_terms(message.content)
            if legal_terms:
                message.metadata["legal_terms"] = legal_terms
            
            # Update metadata with legal analysis
            message.metadata.update({
                "legal_analysis_completed": True,
                "analysis_timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to extract legal context from message: {str(e)}")

# Global service instance
conversation_service = ConversationService()
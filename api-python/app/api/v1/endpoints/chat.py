"""
Legal Chat Endpoints - Core Conversation Management
Provides real-time legal assistance with SA legal context integration
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
import logging
import uuid
from datetime import datetime
import asyncio
import json

from app.models.schemas import (
    ChatRequest, ChatResponse, ConversationHistoryRequest, 
    ConversationSummary, MessageResponse
)
from app.services.conversation_service import ConversationService
from app.services.vector_store import VectorStoreService
from app.services.legal_quality_assurance import qa_service
from app.utils.south_african_legal import (
    extract_legal_citations,
    extract_legal_terms,
    format_legal_response,
    sa_legal_parser
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize conversation service
conversation_service = ConversationService()

# Global vector store instance (will be set from main.py)
vector_store_instance = None

def set_vector_store(vector_store):
    """Set the global vector store instance"""
    global vector_store_instance
    vector_store_instance = vector_store

@router.post("/", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks
):
    """
    Send a message to the legal AI assistant and receive a response.
    Integrates with SA legal context and quality assurance.
    """
    try:
        logger.info(f"Processing chat message for session: {request.session_id}")
        
        # Create or retrieve conversation
        conversation = await conversation_service.get_or_create_conversation(
            session_id=request.session_id,
            user_id=request.user_id,
            legal_matter_context=request.legal_context
        )
        
        # Save user message
        user_message = await conversation_service.save_message(
            conversation_id=conversation.id,
            content=request.message,
            message_type="user",
            metadata={
                "client_ip": request.client_metadata.get("ip_address", "unknown"),
                "user_agent": request.client_metadata.get("user_agent", "unknown")
            }
        )
        
        # Generate AI response with legal context
        ai_response = await _generate_legal_response(
            message=request.message,
            conversation=conversation,
            include_sources=request.include_sources,
            vector_store=vector_store_instance
        )
        
        # Save AI response
        ai_message = await conversation_service.save_message(
            conversation_id=conversation.id,
            content=ai_response["content"],
            message_type="assistant",
            metadata={
                "sources": ai_response.get("sources", []),
                "legal_citations": ai_response.get("legal_citations", []),
                "confidence_score": ai_response.get("confidence", 0.0),
                "qa_score": ai_response.get("qa_score", 0.0)
            }
        )
        
        # Background quality assurance
        background_tasks.add_task(
            _run_quality_assurance,
            ai_message.id,
            ai_response["content"],
            request.message
        )
        
        # Check for escalation triggers
        escalation_needed = await _check_escalation_triggers(
            ai_response["content"],
            ai_response.get("confidence", 0.0)
        )
        
        return ChatResponse(
            message_id=ai_message.id,
            content=ai_response["content"],
            sources=ai_response.get("sources", []),
            legal_citations=ai_response.get("legal_citations", []),
            confidence_score=ai_response.get("confidence", 0.0),
            escalation_recommended=escalation_needed,
            conversation_id=conversation.id,
            timestamp=ai_message.created_at
        )
        
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process legal query. Please try again."
        )

@router.get("/history/{session_id}", response_model=List[MessageResponse])
async def get_conversation_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0
):
    """
    Retrieve conversation history for a given session.
    """
    try:
        conversation = await conversation_service.get_conversation_by_session(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await conversation_service.get_conversation_messages(
            conversation_id=conversation.id,
            limit=limit,
            offset=offset
        )
        
        return [
            MessageResponse(
                id=msg.id,
                content=msg.content,
                message_type=msg.message_type,
                timestamp=msg.created_at,
                metadata=msg.metadata
            )
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversation history"
        )

@router.get("/conversations/{user_id}", response_model=List[ConversationSummary])
async def get_user_conversations(
    user_id: str,
    limit: int = 20,
    offset: int = 0
):
    """
    Get all conversations for a user with summary information.
    """
    try:
        conversations = await conversation_service.get_user_conversations(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return [
            ConversationSummary(
                id=conv.id,
                session_id=conv.session_id,
                title=conv.title or "Legal Consultation",
                last_message=conv.last_message_content,
                message_count=conv.message_count,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                legal_context=conv.legal_matter_context
            )
            for conv in conversations
        ]
        
    except Exception as e:
        logger.error(f"User conversations error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve user conversations"
        )

@router.post("/stream")
async def stream_chat_response(request: ChatRequest):
    """
    Stream a real-time legal chat response for immediate user feedback.
    """
    async def generate_stream():
        try:
            # Initialize streaming response
            yield f"data: {json.dumps({'type': 'start', 'session_id': request.session_id})}\n\n"
            
            # Generate response in chunks
            async for chunk in _generate_streaming_response(request):
                yield f"data: {json.dumps(chunk)}\n\n"
                
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

# Helper functions

async def _generate_legal_response(
    message: str,
    conversation,
    include_sources: bool = True,
    vector_store = None
) -> Dict[str, Any]:
    """Generate AI response with SA legal context integration."""
    
    # Search relevant legal documents
    legal_context = []
    if vector_store and include_sources:
        try:
            search_results = await vector_store.search_similar_documents(
                query=message,
                limit=5,
                filter_metadata={
                    "jurisdiction": "South Africa",
                    "document_type": "legal"
                }
            )
            legal_context = [
                {
                    "id": result.id,
                    "title": result.metadata.get("title", "Legal Document"),
                    "excerpt": result.content[:200] + "...",
                    "citation": result.metadata.get("citation", ""),
                    "relevance_score": result.distance
                }
                for result in search_results
            ]
        except Exception as e:
            logger.warning(f"Vector search failed: {str(e)}")
    
    # Extract legal citations and terms
    legal_citations = extract_legal_citations(message)
    legal_terms = extract_legal_terms(message)
    
    # Generate AI response using demo AI service
    ai_response_data = await _call_legal_ai_model(
        message=message,
        context=legal_context,
        conversation_history=conversation.get_recent_context(),
        legal_matter=conversation.legal_matter_context
    )
    
    # Merge legal context with AI sources
    all_sources = legal_context + ai_response_data.get('sources', [])
    all_citations = list(set(legal_citations + ai_response_data.get('legal_citations', [])))
    
    return {
        "content": ai_response_data.get('content', 'Unable to generate response'),
        "sources": all_sources,
        "legal_citations": all_citations,
        "confidence": ai_response_data.get('confidence', 0.0),
        "legal_area": ai_response_data.get('legal_area', 'General'),
        "urgency": ai_response_data.get('urgency', 'Normal'),
        "qa_score": 0.0  # Will be calculated in background
    }

async def _call_legal_ai_model(
    message: str,
    context: List[Dict],
    conversation_history: str,
    legal_matter: Optional[str]
) -> Dict[str, Any]:
    """
    Generate legal AI response using demo service.
    For production, replace with your preferred AI service (OpenAI, Anthropic, etc.)
    """
    from app.services.demo_ai_service import demo_ai_service
    
    try:
        # Use demo AI service for realistic responses
        response_data = await demo_ai_service.generate_response(
            message=message,
            context=context,
            conversation_history=conversation_history,
            legal_matter=legal_matter
        )
        
        return response_data
        
    except Exception as e:
        logger.error(f"AI service error: {str(e)}")
        # Fallback response
        return {
            'content': f"""I apologise, but I'm experiencing technical difficulties processing your legal enquiry about "{message[:100]}...".

**However, our expert attorneys are immediately available to help you!**

Don't let a technical issue delay getting the legal assistance you need. Our qualified legal team can provide personalised guidance for your specific situation.

**For urgent legal matters:** Contact Legal Aid South Africa at 0800 110 110

---

**Get direct access to our legal experts:**

Our experienced attorneys specialise in South African law and are ready to review your case personally. Don't wait - schedule your consultation now.

[SCHEDULE_CONSULTATION] [CONTACT_FIRM]""",
            'legal_area': 'Technical Error',
            'urgency': 'Normal',
            'confidence': 0.0,
            'sources': [],
            'legal_citations': []
        }

async def _generate_streaming_response(request: ChatRequest):
    """Generate streaming response chunks for real-time chat."""
    chunks = [
        {"type": "typing", "message": "Analyzing your legal question..."},
        {"type": "searching", "message": "Searching SA legal database..."},
        {"type": "processing", "message": "Generating response..."},
        {"type": "content", "content": "Based on South African law..."},
        {"type": "content", "content": " your question relates to..."},
        {"type": "content", "content": " [Complete response here]"}
    ]
    
    for chunk in chunks:
        await asyncio.sleep(0.5)  # Simulate processing time
        yield chunk

async def _run_quality_assurance(message_id: str, content: str, user_query: str):
    """Run quality assurance on AI response in background."""
    try:
        qa_result = await qa_service.assess_response_quality(
            response=content,
            query=user_query,
            context="legal_chat"
        )
        
        # Update message with QA score
        await conversation_service.update_message_qa_score(
            message_id=message_id,
            qa_score=qa_result.overall_score,
            qa_metadata={
                "citation_accuracy": qa_result.citation_accuracy,
                "legal_terminology_score": qa_result.legal_terminology_score,
                "sa_legal_context_score": qa_result.sa_legal_context_score
            }
        )
        
        logger.info(f"QA completed for message {message_id}: {qa_result.overall_score}")
        
    except Exception as e:
        logger.error(f"QA processing failed for message {message_id}: {str(e)}")

async def _check_escalation_triggers(content: str, confidence: float) -> bool:
    """Check if conversation should be escalated to human lawyer."""
    
    escalation_triggers = [
        confidence < 0.7,  # Low confidence
        "urgent" in content.lower(),
        "emergency" in content.lower(),
        "court date" in content.lower(),
        "deadline" in content.lower(),
        "criminal charge" in content.lower()
    ]
    
    return any(escalation_triggers)
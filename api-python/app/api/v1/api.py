"""
API Router for Verdict360 Legal Intelligence Platform
Combines all API endpoints for legal document processing, chat, and consultation management
"""

from fastapi import APIRouter
from app.api.v1.endpoints import search, documents, chat, consultation, voice, webhooks, analytics, calendar, simple_chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(search.router, prefix="/search", tags=["Legal Search & Chat"])
api_router.include_router(documents.router, prefix="/documents", tags=["Document Management"])
api_router.include_router(chat.router, prefix="/chat", tags=["Legal AI Chat"])
api_router.include_router(simple_chat.router, prefix="/simple-chat", tags=["Demo Chat API"])
api_router.include_router(consultation.router, prefix="/consultations", tags=["Consultation Booking"])
api_router.include_router(voice.router, prefix="/voice", tags=["Voice Integration"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Dashboard"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar & Scheduling"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["N8N Workflow Webhooks"])

# Health check for API v1
@api_router.get("/health")
async def api_health():
    """Health check for API v1"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "capabilities": [
            "Legal AI Chat",
            "Consultation Booking",
            "Voice Integration", 
            "Document Processing",
            "SA Legal Search",
            "Analytics & Dashboard",
            "Real-time Calendar Scheduling",
            "N8N Workflow Integration"
        ],
        "endpoints": [
            "/chat/",
            "/consultations/",
            "/voice/initiate-call",
            "/search/legal-query",
            "/documents/upload",
            "/analytics/dashboard/summary",
            "/calendar/availability/check",
            "/webhooks/*"
        ],
        "market": "South African Legal Professionals",
        "features": {
            "ai_legal_chat": True,
            "consultation_booking": True,
            "voice_calls": True,
            "sa_legal_citations": True,
            "analytics_dashboard": True,
            "real_time_calendar": True,
            "conflict_detection": True,
            "workflow_automation": True,
            "crm_integration": True
        }
    }
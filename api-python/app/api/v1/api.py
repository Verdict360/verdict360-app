"""
API Router for Verdict360 Legal Intelligence Platform
Combines all API endpoints for legal document processing and search
"""

from fastapi import APIRouter
from app.api.v1.endpoints import search, documents

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(search.router, prefix="/search", tags=["Legal Search & Chat"])
api_router.include_router(documents.router, prefix="/documents", tags=["Document Management"])

# Health check for API v1
@api_router.get("/health")
async def api_health():
    """Health check for API v1"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "endpoints": [
            "/search/legal-query",
            "/search/documents/search", 
            "/documents/upload",
            "/documents/process"
        ]
    }
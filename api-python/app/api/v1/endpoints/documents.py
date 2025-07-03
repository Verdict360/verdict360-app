"""
Document Management Endpoints
Basic document endpoints to support the legal chat functionality
"""

from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/")
async def list_documents():
    """List available documents"""
    return {
        "message": "Document listing endpoint",
        "available": True
    }

@router.post("/upload")
async def upload_document():
    """Upload document endpoint placeholder"""
    return {
        "message": "Document upload endpoint",
        "status": "placeholder"
    }
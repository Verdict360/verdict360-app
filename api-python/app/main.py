from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from typing import List, Optional
import asyncio

from app.dependencies import get_current_user
from app.services.document_processor import DocumentProcessor
from app.services.minio_service import minio_service
from app.services.whisper_service import whisper_service
from app.models.schemas import DocumentCreate, RecordingCreate, LegalQuery, UserResponse
from app.routers import recordings

# Initialize services
document_processor = DocumentProcessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Verdict360 Legal API...")
    try:
        await minio_service.ensure_buckets_exist()
        print("✅ MinIO storage initialized")
        print("✅ Document processor initialized")
        print("✅ Whisper transcription service ready")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("⚠️  Continuing without MinIO (check your MinIO configuration)")
    yield
    # Shutdown
    print("🛑 Shutting down Verdict360 Legal API...")

app = FastAPI(
    title="Verdict360 Legal API",
    description="AI-powered legal intelligence platform for South African professionals",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://10.0.2.2:3000"],  # Web and mobile
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recordings.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Verdict360 Legal API",
        "version": "1.0.0",
        "python_version": "3.11",
        "features": [
            "document_processing", 
            "sa_citation_detection", 
            "text_extraction",
            "minio_storage",
            "whisper_transcription",
            "audio_processing"
        ]
    }

# Enhanced document upload endpoint with storage
@app.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    jurisdiction: str = Form("South Africa"),
    matter_id: Optional[str] = Form(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload, process and store a legal document with South African legal context"""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, DOCX, and TXT files are allowed.")
        
        # Process and store document
        metadata = {
            "title": title,
            "document_type": document_type,
            "jurisdiction": jurisdiction,
            "matter_id": matter_id,
            "created_by": current_user.id
        }
        
        processing_result = await document_processor.process_and_store_document(file, metadata, current_user.id)
        
        if processing_result["status"] == "failed":
            raise HTTPException(status_code=500, detail=f"Document processing failed: {processing_result.get('error', 'Unknown error')}")
        
        return {
            "success": True,
            "document_id": processing_result["document_id"],
            "status": "processed_and_stored",
            "message": "Document uploaded, processed and stored successfully",
            "storage_info": {
                "file_path": processing_result["file_info"]["storage_path"],
                "results_path": processing_result["results_storage_path"]
            },
            "processing_summary": {
                "text_length": processing_result["text_length"],
                "citations_found": processing_result["citations_found"],
                "document_analysis": processing_result["analysis"],
                "top_citations": processing_result["citations"][:5]  # Show top 5 citations
            },
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

# Get document processing result
@app.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get document processing results"""
    # For now, return mock data - we'll add database integration later
    return {
        "document_id": document_id,
        "status": "processed",
        "message": "Document processing completed",
        "created_by": current_user.id
    }

# Test endpoint for development
@app.get("/test")
async def test_endpoint():
    return {
        "message": "Verdict360 Legal API is working!",
        "features": [
            "FastAPI", 
            "Document Processing", 
            "SA Citation Detection",
            "MinIO Storage Integration",
            "Whisper Audio Transcription",
            "Legal Audio Processing"
        ],
        "next_steps": ["Vector search", "Database integration", "Legal chat with LLMs"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

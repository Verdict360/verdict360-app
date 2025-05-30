from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from typing import List, Optional
import asyncio

from app.dependencies import get_current_user
# from app.services.document_processor import DocumentProcessor  # We'll create this next
# from app.services.audio_processor import AudioProcessor      # We'll add this later
# from app.services.vector_store import VectorStore           # We'll create this next
from app.models.schemas import DocumentCreate, RecordingCreate, LegalQuery, UserResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Verdict360 Legal API...")
    # await vector_store.initialize()        # We'll enable this later
    # await audio_processor.initialize()     # We'll add this later
    print("✅ Basic API initialized")
    yield
    # Shutdown
    print("👋 Shutting down Verdict360 Legal API...")

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

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Verdict360 Legal API",
        "version": "1.0.0",
        "python_version": "3.13",
        "features": ["document_processing", "basic_endpoints"]
    }

# Basic document upload endpoint (we'll enhance this)
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
    """Upload a legal document - basic version"""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, DOCX, and TXT files are allowed.")
        
        # For now, just return basic info - we'll add processing in next steps
        document_id = f"doc_{hash(file.filename)}_{int(__import__('time').time())}"
        
        return {
            "document_id": document_id,
            "status": "received",
            "message": "Document uploaded successfully",
            "file_info": {
                "name": file.filename,
                "size": file.size,
                "type": file.content_type
            },
            "metadata": {
                "title": title,
                "document_type": document_type,
                "jurisdiction": jurisdiction,
                "matter_id": matter_id,
                "created_by": current_user.id
            }
        }
        
    except Exception as e:
        print(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

# Test endpoint for development
@app.get("/test")
async def test_endpoint():
    return {
        "message": "Verdict360 Legal API is working!",
        "features": ["FastAPI", "Pydantic", "CORS enabled"],
        "next_steps": ["Document processing", "Audio transcription", "Vector search"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

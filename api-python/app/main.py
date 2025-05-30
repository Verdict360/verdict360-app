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
from app.services.vector_store import vector_store
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
        
        await vector_store.initialize()
        print("✅ Vector store initialized")
        
        print("✅ Document processor initialized")
        print("✅ Whisper transcription service ready")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("⚠️  Continuing without some services (check your configuration)")
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
            "audio_processing",
            "vector_search",
            "semantic_similarity"
        ]
    }

# Enhanced document upload endpoint with vector storage
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
    """Upload, process and store a legal document with vector embeddings"""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, DOCX, and TXT files are allowed.")
        
        # Process and store document (now includes vector storage)
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
            "message": "Document uploaded, processed and stored with vector embeddings",
            "storage_info": {
                "file_path": processing_result["file_info"]["storage_path"],
                "results_path": processing_result["results_storage_path"]
            },
            "processing_summary": {
                "text_length": processing_result["text_length"],
                "chunks_created": processing_result["chunk_count"],
                "citations_found": processing_result["citations_found"],
                "document_analysis": processing_result["analysis"],
                "top_citations": processing_result["citations"][:5],
                "vector_storage": processing_result["vector_storage"]
            },
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

# NEW: Vector search endpoint for legal documents
@app.post("/documents/search")
async def search_documents(
    query: str = Form(...),
    limit: int = Form(5),
    jurisdiction: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Search for similar legal documents using vector similarity
    
    This endpoint performs semantic search across all uploaded documents
    to find content similar to your query.
    """
    try:
        # Perform vector search
        search_results = await vector_store.search_similar_documents(
            query=query,
            limit=limit,
            jurisdiction_filter=jurisdiction,
            document_type_filter=document_type,
            include_metadata=True
        )
        
        # Format results for response
        formatted_results = []
        for result in search_results:
            formatted_result = {
                "content_preview": result["content"][:300] + "..." if len(result["content"]) > 300 else result["content"],
                "similarity_score": result["similarity_score"],
                "document_id": result.get("metadata", {}).get("document_id", "unknown"),
                "document_title": result.get("metadata", {}).get("title", "Untitled"),
                "document_type": result.get("metadata", {}).get("document_type", "unknown"),
                "jurisdiction": result.get("metadata", {}).get("jurisdiction", "unknown"),
                "chunk_index": result["chunk_index"],
                "citations_in_chunk": result.get("metadata", {}).get("citations", []),
                "legal_terms_in_chunk": result.get("metadata", {}).get("legal_terms", []),
                "word_count": result.get("metadata", {}).get("word_count", 0)
            }
            formatted_results.append(formatted_result)
        
        return {
            "success": True,
            "query": query,
            "results_count": len(formatted_results),
            "search_results": formatted_results,
            "search_metadata": {
                "jurisdiction_filter": jurisdiction,
                "document_type_filter": document_type,
                "max_results": limit,
                "embedding_model": "all-MiniLM-L6-v2"
            }
        }
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# NEW: Get vector store statistics
@app.get("/documents/vector-stats")
async def get_vector_stats(current_user: UserResponse = Depends(get_current_user)):
    """Get statistics about the vector database"""
    try:
        stats = await vector_store.get_collection_stats()
        return {
            "success": True,
            "vector_database_stats": stats
        }
    except Exception as e:
        print(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

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

# NEW: Find similar documents to a specific document
@app.get("/documents/{document_id}/similar")
async def find_similar_documents(
    document_id: str,
    limit: int = 5,
    current_user: UserResponse = Depends(get_current_user)
):
    """Find documents similar to a specific document"""
    try:
        # Get the first chunk of the document to use as query
        search_results = await vector_store.search_similar_documents(
            query=document_id,  # This is a simplified approach
            limit=limit + 1,  # +1 to exclude the original document
            include_metadata=True
        )
        
        # Filter out the original document
        similar_docs = [result for result in search_results 
                       if result.get("metadata", {}).get("document_id") != document_id][:limit]
        
        return {
            "success": True,
            "document_id": document_id,
            "similar_documents": similar_docs
        }
        
    except Exception as e:
        print(f"Similar documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar documents: {str(e)}")

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
            "Legal Audio Processing",
            "ChromaDB Vector Storage",
            "Semantic Document Search",
            "Legal Text Similarity"
        ],
        "next_steps": ["Database integration", "Legal chat with LLMs", "Advanced search filters"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

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

# NEW: Legal Query with Ollama LLM Integration
@app.post("/legal-chat")
async def legal_chat_with_ollama(
    query: str = Form(...),
    context_limit: int = Form(3),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Process legal query using RAG (Retrieval-Augmented Generation) with Ollama
    
    This endpoint:
    1. Searches for relevant documents in your vector store
    2. Uses those documents as context for Ollama
    3. Returns a legal response with citations
    """
    try:
        import httpx
        
        # Step 1: Retrieve relevant documents from vector store
        relevant_docs = await vector_store.search_similar_documents(
            query=query,
            limit=context_limit,
            include_metadata=True
        )
        
        # Step 2: Format context from retrieved documents
        context_parts = []
        sources = []
        
        for i, doc in enumerate(relevant_docs, 1):
            context_parts.append(f"Document {i}: {doc['content'][:500]}...")
            sources.append({
                "document_id": doc.get("metadata", {}).get("document_id", "unknown"),
                "title": doc.get("metadata", {}).get("title", "Untitled"),
                "similarity_score": doc["similarity_score"],
                "citations": doc.get("metadata", {}).get("citations", [])
            })
        
        context = "\n\n".join(context_parts)
        
        # Step 3: Create legal prompt for Ollama
        legal_prompt = f"""You are Verdict360, a specialized South African legal assistant with expertise in South African law.

SOUTH AFRICAN LEGAL CONTEXT:
- South Africa has a mixed legal system (Roman-Dutch civil law and English common law)
- The Constitution of the Republic of South Africa (1996) is the supreme law
- Court hierarchy: Constitutional Court > Supreme Court of Appeal > High Courts > Magistrates' Courts
- Key legal principles include Ubuntu, constitutional supremacy, and the rule of law

RELEVANT DOCUMENTS FROM DATABASE:
{context}

QUESTION: {query}

Please provide a comprehensive legal analysis based on the provided context. If the documents contain relevant South African case law or statutes, reference them appropriately. If you cannot answer based on the provided context, clearly state so and suggest what additional information might be needed.

Focus on South African legal principles and cite any case law or statutes mentioned in the context."""

        # Step 4: Query Ollama
        async with httpx.AsyncClient(timeout=60.0) as client:
            ollama_response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": legal_prompt,
                    "system": "You are a helpful South African legal assistant. Always provide accurate, well-reasoned legal analysis based on South African law.",
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower temperature for more consistent legal advice
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                }
            )
            
            if ollama_response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Ollama service error: {ollama_response.status_code}")
            
            ollama_result = ollama_response.json()
        
        # Step 5: Format response
        return {
            "success": True,
            "query": query,
            "response": ollama_result.get("response", "No response generated"),
            "context_used": {
                "documents_found": len(relevant_docs),
                "sources": sources
            },
            "model_info": {
                "model": "llama3.2",
                "local": True,
                "temperature": 0.3
            },
            "legal_disclaimer": "This is AI-generated legal information for research purposes only. Always consult with a qualified South African attorney for specific legal advice."
        }
        
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama service timeout. Please try again.")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama service. Please ensure Ollama is running.")
    except Exception as e:
        print(f"Legal chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Legal chat failed: {str(e)}")

# Health check for Ollama integration
@app.get("/ollama/health")
async def ollama_health_check():
    """Check if Ollama service is available and responsive"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                llama_available = any("llama3.2" in model.get("name", "") for model in models)
                
                return {
                    "status": "healthy",
                    "ollama_running": True,
                    "llama3.2_available": llama_available,
                    "total_models": len(models)
                }
            else:
                return {"status": "unhealthy", "error": f"Ollama responded with {response.status_code}"}
                
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

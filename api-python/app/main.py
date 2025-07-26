"""
Verdict360 Legal Intelligence Platform - FastAPI Backend
AI-powered legal document processing and search for South African legal professionals
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

from app.api.v1.api import api_router
from app.core.config import settings
from app.services.vector_store import VectorStoreService
from app.api.v1.endpoints.search import set_vector_store
from app.api.v1.endpoints.chat import set_vector_store as set_chat_vector_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Global vector store instance
vector_store = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    global vector_store
    
    # Startup
    logger.info("🚀 Starting Verdict360 Legal Intelligence API")
    logger.info("🇿🇦 Configured for South African legal context")
    
    try:
        # Initialize vector store (optional for basic API functionality)
        vector_store = VectorStoreService()
        await vector_store.initialize()
        
        # Store in app state for access in endpoints
        app.state.vector_store = vector_store
        
        # Set global vector store for search and chat endpoints
        set_vector_store(vector_store)
        set_chat_vector_store(vector_store)
        
        logger.info("✅ Vector database initialized successfully")
        logger.info(f"📊 Collection: {settings.CHROMA_COLLECTION_NAME}")
        
    except Exception as e:
        logger.warning(f"⚠️ Vector store initialization failed: {e}")
        logger.info("🔄 Starting API without vector store (simple chat will still work)")
        
        # Set None for vector store to allow basic functionality
        app.state.vector_store = None
        set_vector_store(None)
        set_chat_vector_store(None)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Verdict360 API")
    if vector_store:
        await vector_store.close()

# Create FastAPI application
app = FastAPI(
    title="Verdict360 Legal Intelligence API",
    description="AI-powered legal document processing and search for South African legal professionals",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Alternative ports
        "http://localhost:5173",  # SvelteKit dev server
        "http://127.0.0.1:5173",
        "http://localhost:4173",  # SvelteKit preview
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "Verdict360 Legal Intelligence API",
        "version": "1.0.0",
        "jurisdiction": "South Africa",
        "vector_store": "initialized" if hasattr(app.state, 'vector_store') else "not_initialized"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Verdict360 Legal Intelligence Platform API",
        "description": "AI-powered legal document processing for South African legal professionals",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_RELOAD", "true").lower() == "true",
        log_level="info"
    )

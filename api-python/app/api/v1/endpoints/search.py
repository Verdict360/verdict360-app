"""
Enhanced Legal Search and Chat Endpoints
Provides legal query processing with RAG, citation detection, and South African legal context
"""

from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
import re
from app.models.schemas import LegalQueryRequest, LegalQueryResponse, DocumentSearchRequest
from app.services.vector_store import VectorStoreService
from app.services.legal_quality_assurance import qa_service
from app.services.cache_service import cache_service
from app.utils.south_african_legal import (
    extract_legal_citations, 
    extract_legal_terms,
    format_legal_response,
    SA_LEGAL_SYSTEM_PROMPT
)

router = APIRouter()
logger = logging.getLogger(__name__)

# South African legal citation patterns
SA_CITATION_PATTERNS = [
    r'\d{4}\s+\(\d+\)\s+SA\s+\d+\s+\([A-Z]+\)',  # 2019 (2) SA 343 (SCA)
    r'\[\d{4}\]\s+ZACC\s+\d+',                   # [2021] ZACC 13
    r'\[\d{4}\]\s+ZASCA\s+\d+',                  # [2020] ZASCA 99
    r'\d{4}\s+\(\d+\)\s+BCLR\s+\d+',             # 2018 (7) BCLR 844
    r'Act\s+No\.\s+\d+\s+of\s+\d{4}',            # Act No. 71 of 2008
    r'Act\s+\d+\s+of\s+\d{4}',                   # Act 71 of 2008
    r'Constitution\s+of\s+the\s+Republic\s+of\s+South\s+Africa,?\s+1996',
]

@router.post("/legal-query")
async def process_legal_query(
    query: str = Form(...),
    jurisdiction: str = Form("South Africa"),
    matter_id: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None),
    vector_store: VectorStoreService = Depends(lambda: vector_store_instance)
):
    """
    Process a legal query with RAG-enhanced responses, citation detection,
    and South African legal context integration.
    """
    try:
        logger.info(f"Processing legal query: {query[:100]}...")
        
        # Check cache first
        cached_response = await cache_service.get_legal_query(query, jurisdiction)
        if cached_response:
            logger.info("Returning cached legal query response")
            return LegalQueryResponse(**cached_response)
        
        # Search for relevant documents using vector similarity
        search_results = await vector_store.search_documents(
            query=query,
            limit=5,
            filters={
                "jurisdiction": jurisdiction
            } if jurisdiction else None
        )
        
        # Generate legal response using retrieved context
        legal_response = await generate_legal_response(
            query=query,
            search_results=search_results,
            jurisdiction=jurisdiction
        )
        
        # Extract citations and legal terms from response
        citations = extract_legal_citations(legal_response)
        legal_terms = extract_legal_terms(legal_response)
        
        # Format sources from search results
        sources = []
        for result in search_results:
            source = {
                "id": result.get("document_id", ""),
                "title": result.get("document_title", "Unknown Document"),
                "citation": result.get("citation", ""),
                "document_type": result.get("document_type", ""),
                "jurisdiction": result.get("jurisdiction", jurisdiction),
                "chunk_index": result.get("chunk_index", 0),
                "similarity_score": result.get("similarity_score", 0.0)
            }
            sources.append(source)
        
        # Calculate confidence score based on similarity and citations
        confidence_score = calculate_response_confidence(search_results, citations)
        
        # Perform quality assurance check
        quality_assessment = await qa_service.assess_legal_response(
            query=query,
            response=legal_response,
            sources=search_results,
            context_documents=[]
        )
        
        # Add quality metrics to response
        response_data = LegalQueryResponse(
            success=True,
            response=legal_response,
            sources=sources,
            query=query,
            legal_citations=citations,
            legal_terms=legal_terms[:10],  # Limit to top 10 terms
            confidence_score=max(confidence_score, quality_assessment.overall_score),  # Use higher score
            jurisdiction=jurisdiction
        )
        
        # Add quality assessment metadata if it reveals issues
        if quality_assessment.overall_score < 0.7:
            logger.warning(f"Low quality response detected: {quality_assessment.overall_score}")
            # In production, you might want to regenerate the response or add warnings
        
        # Cache the response for future use
        response_dict = {
            "success": True,
            "response": legal_response,
            "sources": sources,
            "query": query,
            "legal_citations": citations,
            "legal_terms": legal_terms[:10],
            "confidence_score": max(confidence_score, quality_assessment.overall_score),
            "jurisdiction": jurisdiction
        }
        
        # Cache only high-quality responses
        if quality_assessment.overall_score >= 0.7:
            await cache_service.set_legal_query(query, response_dict, jurisdiction)
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing legal query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process legal query: {str(e)}"
        )

@router.post("/documents/search")
async def search_documents(
    query: str = Form(...),
    document_type: Optional[str] = Form(None),
    jurisdiction: Optional[str] = Form(None),
    limit: int = Form(5),
    vector_store: VectorStoreService = Depends(lambda: vector_store_instance)
):
    """
    Enhanced document search with legal context and metadata filtering.
    """
    try:
        logger.info(f"Searching documents for: {query[:50]}...")
        
        # Build filters
        filters = {}
        if document_type:
            filters["document_type"] = document_type
        if jurisdiction:
            filters["jurisdiction"] = jurisdiction
        
        # Perform vector search
        search_results = await vector_store.search_documents(
            query=query,
            limit=limit,
            filters=filters if filters else None
        )
        
        # Process and enhance results
        enhanced_results = []
        for result in search_results:
            # Extract citations and legal terms from content
            content = result.get("content", "")
            citations = extract_legal_citations(content)
            legal_terms = extract_legal_terms(content)
            
            enhanced_result = {
                "content_preview": content[:500] + "..." if len(content) > 500 else content,
                "similarity_score": result.get("similarity_score", 0.0),
                "document_id": result.get("document_id", ""),
                "document_title": result.get("document_title", "Unknown Document"),
                "document_type": result.get("document_type", "unknown"),
                "jurisdiction": result.get("jurisdiction", "Unknown"),
                "chunk_index": result.get("chunk_index", 0),
                "citations_in_chunk": citations[:5],  # Limit to 5 citations
                "legal_terms_in_chunk": legal_terms[:8],  # Limit to 8 terms
                "word_count": len(content.split())
            }
            enhanced_results.append(enhanced_result)
        
        return {
            "success": True,
            "query": query,
            "results_count": len(enhanced_results),
            "search_results": enhanced_results,
            "search_metadata": {
                "filters_applied": filters,
                "total_documents_searched": "vector_database",
                "search_type": "semantic_similarity"
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Document search failed: {str(e)}"
        )

async def generate_legal_response(
    query: str, 
    search_results: List[Dict[str, Any]], 
    jurisdiction: str = "South Africa"
) -> str:
    """
    Generate a legal response using retrieved context and SA legal prompts.
    This is a simplified implementation - in production you'd use Ollama/LLM here.
    """
    try:
        # Extract context from search results
        context_chunks = []
        for result in search_results[:3]:  # Use top 3 results
            content = result.get("content", "")
            title = result.get("document_title", "")
            context_chunks.append(f"From '{title}':\n{content[:800]}")
        
        context = "\n\n".join(context_chunks)
        
        # Create enhanced prompt for South African legal context
        prompt = f"""
{SA_LEGAL_SYSTEM_PROMPT}

Based on the following South African legal context, please answer the question:

CONTEXT:
{context}

QUESTION: {query}

Please provide a comprehensive answer that:
1. Directly addresses the question
2. References relevant South African case law or statutes if available in the context
3. Uses proper legal citation format
4. Considers the South African legal framework
5. Is practical and actionable for legal practitioners

ANSWER:
"""
        
        # This would normally call Ollama or another LLM
        # For now, return a formatted response based on context
        if context:
            response = f"""Based on South African legal principles and the relevant context:

The query regarding "{query}" relates to important aspects of South African law.

{context[:1000]}

This analysis is based on the retrieved legal documents and should be verified against current South African legislation and case law. For specific legal advice, please consult with a qualified South African attorney.

Key legal considerations include:
- Compliance with South African statutory requirements
- Adherence to constitutional principles
- Consideration of relevant case precedents
- Jurisdictional limitations and procedures"""
        else:
            response = f"""I understand you're asking about: {query}

While I don't have specific context available for this query in the current document database, I can provide general guidance that this matter should be approached considering:

- The Constitution of the Republic of South Africa, 1996 as the supreme law
- Relevant South African legislation and regulations
- Applicable case law from South African courts
- Professional legal advice for specific circumstances

For comprehensive legal advice on this matter, please consult with a qualified South African legal professional who can provide guidance specific to your circumstances and current legal developments."""
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating legal response: {str(e)}")
        return f"I apologize, but I encountered an error processing your legal query about: {query}. Please try again or consult with a qualified legal professional."

def calculate_response_confidence(search_results: List[Dict[str, Any]], citations: List[str]) -> float:
    """Calculate confidence score for the legal response"""
    if not search_results:
        return 0.1
    
    # Base confidence on similarity scores
    avg_similarity = sum(result.get("similarity_score", 0) for result in search_results) / len(search_results)
    
    # Boost for legal citations found
    citation_boost = min(len(citations) * 0.1, 0.3)
    
    # Boost for South African jurisdiction
    sa_boost = 0.1 if any(result.get("jurisdiction") == "South Africa" for result in search_results) else 0
    
    confidence = min(avg_similarity + citation_boost + sa_boost, 1.0)
    return round(confidence, 2)

# Global vector store instance (initialized in main.py)
vector_store_instance = None

@router.post("/quality-assessment")
async def assess_response_quality(
    query: str = Form(...),
    response: str = Form(...),
    sources: Optional[str] = Form(None)  # JSON string of sources
):
    """
    Endpoint for assessing the quality of a legal response
    Used by admin dashboard and quality monitoring
    """
    try:
        import json
        
        # Parse sources if provided
        source_list = []
        if sources:
            try:
                source_list = json.loads(sources)
            except json.JSONDecodeError:
                logger.warning("Invalid sources JSON provided")
        
        # Perform quality assessment
        assessment = await qa_service.assess_legal_response(
            query=query,
            response=response,
            sources=source_list
        )
        
        return {
            "success": True,
            "assessment": {
                "overall_score": assessment.overall_score,
                "citation_accuracy": assessment.citation_accuracy,
                "legal_terminology_score": assessment.legal_terminology_score,
                "relevance_score": assessment.relevance_score,
                "confidence_score": assessment.confidence_score,
                "sa_legal_context_score": assessment.sa_legal_context_score,
                "quality_level": get_quality_level(assessment.overall_score),
                "issues": assessment.issues,
                "recommendations": assessment.recommendations,
                "validated_citations": assessment.validated_citations,
                "legal_terms_found": assessment.legal_terms_found
            }
        }
        
    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quality assessment failed: {str(e)}"
        )

def get_quality_level(score: float) -> str:
    """Get quality level description from score"""
    if score >= 0.9:
        return "Excellent"
    elif score >= 0.8:
        return "Very Good"
    elif score >= 0.7:
        return "Good"
    elif score >= 0.6:
        return "Satisfactory"
    elif score >= 0.5:
        return "Needs Improvement"
    else:
        return "Poor"

@router.get("/cache-stats")
async def get_cache_statistics():
    """Get cache performance statistics for admin dashboard"""
    try:
        stats = cache_service.get_cache_stats()
        return {
            "success": True,
            "cache_stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache-optimize")
async def optimize_cache():
    """Optimize cache by removing expired entries"""
    try:
        optimization_result = await cache_service.optimize_cache()
        return {
            "success": True,
            "optimization_result": optimization_result
        }
    except Exception as e:
        logger.error(f"Cache optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache-clear")
async def clear_cache(cache_type: Optional[str] = None):
    """Clear cache entries (optionally by type)"""
    try:
        clear_result = await cache_service.clear_cache(cache_type)
        return {
            "success": True,
            "clear_result": clear_result
        }
    except Exception as e:
        logger.error(f"Cache clearing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def set_vector_store(store: VectorStoreService):
    global vector_store_instance
    vector_store_instance = store
"""
Vector store service using ChromaDB for legal document embeddings
Optimized for South African legal content
"""

import chromadb
from chromadb.utils import embedding_functions
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import uuid
from datetime import datetime

from app.core.config import settings
from app.models.document import DocumentChunk, SearchResult, DocumentType, Jurisdiction

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    ChromaDB-based vector store for legal documents
    Handles embeddings, storage, and similarity search for SA legal content
    """
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_function = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            logger.info("🔄 Initializing vector store for legal documents...")
            
            # Create ChromaDB client with persistence
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
            
            # Initialize embedding function
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL,
                device=settings.EMBEDDING_DEVICE
            )
            
            # Create or get collection for legal documents
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={
                    "hnsw:space": "cosine",  # Good for semantic similarity
                    "description": "South African legal documents for Verdict360",
                    "created_at": datetime.now().isoformat(),
                    "jurisdiction": settings.DEFAULT_JURISDICTION
                }
            )
            
            # Get collection stats
            doc_count = self.collection.count()
            logger.info(f"✅ Vector store initialized successfully")
            logger.info(f"📊 Collection: {settings.CHROMA_COLLECTION_NAME}")
            logger.info(f"📄 Documents: {doc_count}")
            logger.info(f"🤖 Embedding model: {settings.EMBEDDING_MODEL}")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize vector store: {e}")
            raise Exception(f"Vector store initialization failed: {str(e)}")
    
    async def add_document_chunks(
        self, 
        document_id: str, 
        chunks: List[DocumentChunk],
        document_metadata: Dict[str, Any]
    ) -> List[str]:
        """
        Add document chunks to the vector store
        
        Args:
            document_id: Unique document identifier
            chunks: List of document chunks with content and metadata
            document_metadata: Document-level metadata
            
        Returns:
            List of chunk IDs that were added
        """
        if not self._initialized:
            raise Exception("Vector store not initialized")
            
        try:
            logger.info(f"📥 Adding {len(chunks)} chunks for document {document_id}")
            
            chunk_ids = []
            documents = []
            metadatas = []
            
            for chunk in chunks:
                # Create unique chunk ID
                chunk_id = f"{document_id}_chunk_{chunk.chunk_index}"
                chunk_ids.append(chunk_id)
                documents.append(chunk.content)
                
                # Prepare metadata for storage (ensure all values are strings/numbers/bools)
                chunk_metadata = {
                    "document_id": str(document_id),
                    "chunk_index": int(chunk.chunk_index),
                    "document_title": str(document_metadata.get("title", "")),
                    "document_type": str(document_metadata.get("document_type", "other")),
                    "jurisdiction": str(document_metadata.get("jurisdiction", "South Africa")),
                    "word_count": int(chunk.word_count),
                    "citations": "|".join(chunk.citations) if chunk.citations else "",
                    "legal_terms": "|".join(chunk.legal_terms) if chunk.legal_terms else "",
                    "created_at": datetime.now().isoformat(),
                    "matter_id": str(document_metadata.get("matter_id") or ""),
                    "file_type": str(document_metadata.get("file_type", ""))
                }
                
                metadatas.append(chunk_metadata)
            
            # Add to ChromaDB collection
            self.collection.add(
                ids=chunk_ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"✅ Successfully added {len(chunk_ids)} chunks to vector store")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"❌ Failed to add document chunks: {e}")
            raise Exception(f"Failed to add chunks to vector store: {str(e)}")
    
    async def search_similar_documents(
        self,
        query: str,
        limit: int = 5,
        document_type_filter: Optional[str] = None,
        jurisdiction_filter: Optional[str] = None,
        min_similarity: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for documents similar to the query using semantic similarity
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            document_type_filter: Filter by document type
            jurisdiction_filter: Filter by jurisdiction
            min_similarity: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of search results with similarity scores
        """
        if not self._initialized:
            raise Exception("Vector store not initialized")
            
        try:
            logger.info(f"🔍 Searching for: '{query[:50]}{'...' if len(query) > 50 else ''}'")
            
            # Build filter conditions
            where_conditions = {}
            if document_type_filter:
                where_conditions["document_type"] = document_type_filter
            if jurisdiction_filter:
                where_conditions["jurisdiction"] = jurisdiction_filter
            
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_conditions if where_conditions else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            search_results = []
            
            if results["documents"] and len(results["documents"]) > 0:
                documents = results["documents"][0]
                metadatas = results["metadatas"][0] if results["metadatas"] else []
                distances = results["distances"][0] if results["distances"] else []
                
                for i, (document, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity_score = 1.0 - distance
                    
                    # Apply minimum similarity filter
                    if similarity_score < min_similarity:
                        continue
                    
                    # Parse stored citations and legal terms
                    citations = metadata.get("citations", "").split("|") if metadata.get("citations") else []
                    legal_terms = metadata.get("legal_terms", "").split("|") if metadata.get("legal_terms") else []
                    
                    # Create search result
                    result = SearchResult(
                        document_id=metadata.get("document_id", "unknown"),
                        document_title=metadata.get("document_title", "Untitled"),
                        document_type=DocumentType(metadata.get("document_type", "other")),
                        jurisdiction=Jurisdiction(metadata.get("jurisdiction", "South Africa")),
                        content_preview=document[:300] + "..." if len(document) > 300 else document,
                        similarity_score=round(similarity_score, 4),
                        chunk_index=metadata.get("chunk_index", 0),
                        citations_in_chunk=[c for c in citations if c],  # Remove empty strings
                        legal_terms_in_chunk=[t for t in legal_terms if t],  # Remove empty strings
                        word_count=metadata.get("word_count", 0)
                    )
                    
                    search_results.append(result)
            
            logger.info(f"✅ Found {len(search_results)} matching documents")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise Exception(f"Vector search failed: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a specific document"""
        if not self._initialized:
            raise Exception("Vector store not initialized")
            
        try:
            self.collection.delete(
                where={"document_id": document_id}
            )
            logger.info(f"🗑️ Deleted document {document_id} from vector store")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete document: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        if not self._initialized:
            return {"error": "Vector store not initialized"}
            
        try:
            total_count = self.collection.count()
            
            # Get sample of metadata to analyze collection
            if total_count > 0:
                sample_results = self.collection.get(
                    limit=min(100, total_count),
                    include=["metadatas"]
                )
                
                # Analyze metadata
                document_types = set()
                jurisdictions = set()
                unique_documents = set()
                
                if sample_results.get("metadatas"):
                    for metadata in sample_results["metadatas"]:
                        if "document_type" in metadata:
                            document_types.add(metadata["document_type"])
                        if "jurisdiction" in metadata:
                            jurisdictions.add(metadata["jurisdiction"])
                        if "document_id" in metadata:
                            unique_documents.add(metadata["document_id"])
                
                return {
                    "total_chunks": total_count,
                    "unique_documents": len(unique_documents),
                    "document_types": list(document_types),
                    "jurisdictions": list(jurisdictions),
                    "collection_name": settings.CHROMA_COLLECTION_NAME,
                    "embedding_model": settings.EMBEDDING_MODEL
                }
            else:
                return {
                    "total_chunks": 0,
                    "unique_documents": 0,
                    "document_types": [],
                    "jurisdictions": [],
                    "collection_name": settings.CHROMA_COLLECTION_NAME,
                    "embedding_model": settings.EMBEDDING_MODEL
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    async def search_documents(self, query: str, limit: int = 5, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Alias for search_similar_documents with different return format for API compatibility
        """
        # Map filters to individual parameters
        document_type_filter = filters.get("document_type") if filters else None
        jurisdiction_filter = filters.get("jurisdiction") if filters else None
        
        # Call the main search method
        search_results = await self.search_similar_documents(
            query=query,
            limit=limit,
            document_type_filter=document_type_filter,
            jurisdiction_filter=jurisdiction_filter
        )
        
        # Convert SearchResult objects to dictionaries for API compatibility
        return [
            {
                "document_id": result.document_id,
                "document_title": result.document_title,
                "document_type": result.document_type.value if hasattr(result.document_type, 'value') else str(result.document_type),
                "jurisdiction": result.jurisdiction.value if hasattr(result.jurisdiction, 'value') else str(result.jurisdiction),
                "content": result.content_preview,
                "similarity_score": result.similarity_score,
                "chunk_index": result.chunk_index,
                "citations": result.citations_in_chunk,
                "legal_terms": result.legal_terms_in_chunk,
                "word_count": result.word_count
            }
            for result in search_results
        ]

    async def close(self):
        """Clean up resources"""
        if self.client:
            self._initialized = False
            logger.info("🔄 Vector store connection closed")

import chromadb
from chromadb.utils import embedding_functions
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class LegalVectorStore:
    """
    ChromaDB-based vector store for legal documents
    Optimised for South African legal content with proper metadata handling
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB with sentence transformers"""
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
        # Use sentence-transformers for embeddings (good for legal text)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # Fast and effective for legal documents
        )
        
    async def initialize(self):
        """Initialize the vector database"""
        try:
            # Create ChromaDB client with persistence
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Create or get the legal documents collection
            self.collection = self.client.get_or_create_collection(
                name="legal_documents",
                embedding_function=self.embedding_function,
                metadata={
                    "hnsw:space": "cosine",  # Good for semantic similarity
                    "description": "Legal documents for Verdict360 platform"
                }
            )
            
            doc_count = self.collection.count()
            logger.info(f"✅ Vector store initialized with {doc_count} documents")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize vector store: {e}")
            raise Exception(f"Vector store initialization failed: {str(e)}")
    
    async def add_document_chunks(
        self, 
        document_id: str, 
        chunks: List[Dict[str, Any]],
        document_metadata: Dict[str, Any] = None
    ) -> List[str]:
        """
        Add document chunks to vector store with legal metadata
        
        Args:
            document_id: Unique document identifier
            chunks: List of text chunks with metadata
            document_metadata: Document-level metadata
            
        Returns:
            List of chunk IDs that were added
        """
        try:
            if not self.collection:
                raise Exception("Vector store not initialized")
            
            # Prepare data for ChromaDB
            chunk_ids = []
            texts = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                texts.append(chunk["content"])
                
                # Combine document and chunk metadata
                chunk_metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "document_type": document_metadata.get("document_type", "unknown") if document_metadata else "unknown",
                    "jurisdiction": document_metadata.get("jurisdiction", "South Africa") if document_metadata else "South Africa",
                    "title": document_metadata.get("title", "") if document_metadata else "",
                    "created_at": datetime.now().isoformat(),
                    "word_count": len(chunk["content"].split()),
                    # Store citations as string (ChromaDB doesn't handle lists well in metadata)
                    "citations": "|".join(chunk.get("citations", [])) if chunk.get("citations") else "",
                    "legal_terms": "|".join(chunk.get("legal_terms", [])) if chunk.get("legal_terms") else "",
                }
                
                # Add any additional chunk-specific metadata
                if "metadata" in chunk:
                    chunk_metadata.update(chunk["metadata"])
                
                metadatas.append(chunk_metadata)
            
            # Add to ChromaDB
            self.collection.add(
                ids=chunk_ids,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"✅ Added {len(chunk_ids)} chunks for document {document_id}")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"❌ Failed to add document chunks: {e}")
            raise Exception(f"Failed to add document to vector store: {str(e)}")
    
    async def search_similar_documents(
        self,
        query: str,
        limit: int = 5,
        jurisdiction_filter: Optional[str] = None,
        document_type_filter: Optional[str] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query
        
        Args:
            query: Search query text
            limit: Maximum number of results
            jurisdiction_filter: Filter by jurisdiction (e.g., "South Africa")
            document_type_filter: Filter by document type
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of similar document chunks with scores and metadata
        """
        try:
            if not self.collection:
                raise Exception("Vector store not initialized")
            
            # Build filter conditions
            where_filter = {}
            if jurisdiction_filter:
                where_filter["jurisdiction"] = jurisdiction_filter
            if document_type_filter:
                where_filter["document_type"] = document_type_filter
            
            # Search in ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"] if include_metadata else ["documents", "distances"]
            )
            
            # Format results
            formatted_results = []
            
            if results["documents"] and len(results["documents"]) > 0:
                documents = results["documents"][0]
                distances = results["distances"][0] if results["distances"] else []
                metadatas = results["metadatas"][0] if results.get("metadatas") else []
                
                for i, document in enumerate(documents):
                    similarity_score = 1 - distances[i] if distances else 0  # Convert distance to similarity
                    
                    result = {
                        "content": document,
                        "similarity_score": round(similarity_score, 4),
                        "chunk_index": i
                    }
                    
                    if include_metadata and metadatas and i < len(metadatas):
                        metadata = metadatas[i].copy()
                        # Convert pipe-separated strings back to lists
                        if "citations" in metadata and metadata["citations"]:
                            metadata["citations"] = metadata["citations"].split("|")
                        if "legal_terms" in metadata and metadata["legal_terms"]:
                            metadata["legal_terms"] = metadata["legal_terms"].split("|")
                        
                        result["metadata"] = metadata
                    
                    formatted_results.append(result)
            
            logger.info(f"🔍 Found {len(formatted_results)} similar documents for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise Exception(f"Vector search failed: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a document"""
        try:
            if not self.collection:
                raise Exception("Vector store not initialized")
            
            # Delete all chunks for this document
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
        try:
            if not self.collection:
                return {"error": "Vector store not initialized"}
            
            total_docs = self.collection.count()
            
            # Get some sample metadata to understand the collection
            sample_results = self.collection.get(limit=10, include=["metadatas"])
            
            jurisdictions = set()
            document_types = set()
            
            if sample_results.get("metadatas"):
                for metadata in sample_results["metadatas"]:
                    if "jurisdiction" in metadata:
                        jurisdictions.add(metadata["jurisdiction"])
                    if "document_type" in metadata:
                        document_types.add(metadata["document_type"])
            
            return {
                "total_chunks": total_docs,
                "jurisdictions": list(jurisdictions),
                "document_types": list(document_types),
                "collection_name": self.collection.name,
                "embedding_model": "all-MiniLM-L6-v2"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            return {"error": str(e)}

# Global vector store instance
vector_store = LegalVectorStore()

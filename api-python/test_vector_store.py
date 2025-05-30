#!/usr/bin/env python3
"""
Test script for Verdict360 vector store functionality
"""
import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.vector_store import vector_store

async def test_vector_store():
    """Test the vector store initialization and basic functionality"""
    
    print("🧪 Testing Verdict360 Vector Store")
    print("=" * 50)
    
    try:
        # Test 1: Initialize vector store
        print("1. Initializing vector store...")
        await vector_store.initialize()
        print("   ✅ Vector store initialized successfully")
        
        # Test 2: Add some sample legal documents
        print("\n2. Adding sample legal documents...")
        
        sample_chunks = [
            {
                "content": "The Constitutional Court of South Africa held in 2019 (2) SA 343 (SCA) that the fundamental rights enshrined in the Constitution must be balanced against competing interests.",
                "citations": ["2019 (2) SA 343 (SCA)"],
                "legal_terms": ["constitutional", "fundamental rights", "constitution"]
            },
            {
                "content": "In terms of section 25 of the Constitution, property rights are protected but may be limited in certain circumstances for land reform purposes.",
                "citations": [],
                "legal_terms": ["section 25", "constitution", "property rights", "land reform"]
            },
            {
                "content": "The plaintiff filed pleadings in the High Court seeking damages for breach of contract. The defendant raised an exception to the particulars of claim.",
                "citations": [],
                "legal_terms": ["plaintiff", "pleadings", "high court", "damages", "breach of contract", "defendant"]
            }
        ]
        
        sample_metadata = {
            "title": "Test Legal Document",
            "document_type": "judgment",
            "jurisdiction": "South Africa"
        }
        
        chunk_ids = await vector_store.add_document_chunks(
            document_id="test_doc_001",
            chunks=sample_chunks,
            document_metadata=sample_metadata
        )
        
        print(f"   ✅ Added {len(chunk_ids)} chunks to vector store")
        
        # Test 3: Search functionality
        print("\n3. Testing search functionality...")
        
        search_queries = [
            "constitutional rights",
            "property law",
            "contract disputes"
        ]
        
        for query in search_queries:
            print(f"\n   Searching for: '{query}'")
            results = await vector_store.search_similar_documents(
                query=query,
                limit=2,
                include_metadata=True
            )
            
            for i, result in enumerate(results, 1):
                print(f"   Result {i}: Score {result['similarity_score']:.3f}")
                print(f"   Content: {result['content'][:100]}...")
                if result.get('metadata', {}).get('citations'):
                    print(f"   Citations: {result['metadata']['citations']}")
        
        # Test 4: Get collection statistics
        print("\n4. Getting collection statistics...")
        stats = await vector_store.get_collection_stats()
        print(f"   Total chunks: {stats.get('total_chunks', 0)}")
        print(f"   Document types: {stats.get('document_types', [])}")
        print(f"   Jurisdictions: {stats.get('jurisdictions', [])}")
        
        print("\n🎉 All tests passed successfully!")
        print("\nVector store is ready for legal document search!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_vector_store())
    sys.exit(0 if success else 1)

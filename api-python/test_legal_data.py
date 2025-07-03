#!/usr/bin/env python3
"""
Script to populate the vector database with sample South African legal content
for testing the enhanced legal chat interface
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.vector_store import VectorStoreService
from app.models.document import DocumentChunk
from app.utils.south_african_legal import sa_legal_parser

async def populate_test_data():
    """Add sample South African legal content to the vector database"""
    
    # Sample South African legal documents
    sample_documents = [
        {
            "id": "contract_law_sa_001",
            "title": "South African Contract Law - Requirements for Valid Contracts",
            "content": """
Requirements for a Valid Contract in South Africa

Under South African law, which follows the Roman-Dutch legal system, a valid contract requires the following essential elements:

1. **Consensus (Agreement)**: There must be a meeting of minds between the parties. This includes:
   - Offer: A clear proposal by one party
   - Acceptance: Unconditional agreement to the terms by the other party
   - The offer and acceptance must correspond exactly (mirror image rule)

2. **Contractual Capacity**: Both parties must have the legal capacity to enter into contracts:
   - Natural persons must be of sound mind and not under the influence of substances
   - Minors have limited contractual capacity
   - Juristic persons must act through authorized representatives

3. **Legality**: The contract must not be contrary to law, good morals (boni mores), or public policy:
   - The subject matter must be legal
   - The purpose must not violate constitutional rights
   - Cannot contravene statutory provisions

4. **Possibility of Performance**: Performance must be possible:
   - Physical possibility
   - Legal possibility
   - The impossibility must exist at the time of contracting

5. **Formalities**: Some contracts require specific formalities:
   - Sale of immovable property must be in writing (Alienation of Land Act 68 of 1981)
   - Suretyship agreements must be in writing
   - Certain consumer contracts require specific disclosures

The Constitution of the Republic of South Africa, 1996, also impacts contract law through the application of constitutional values and the Bill of Rights, particularly in cases involving unfair contract terms.

Case law such as Barkhuizen v Napier 2007 (5) SA 323 (CC) established that contractual terms that are contrary to public policy may be unenforceable.
            """,
            "document_type": "legal_article",
            "jurisdiction": "South Africa",
            "citations": ["Alienation of Land Act 68 of 1981", "Constitution of the Republic of South Africa, 1996", "Barkhuizen v Napier 2007 (5) SA 323 (CC)"]
        },
        {
            "id": "labour_law_sa_001", 
            "title": "South African Labour Relations Act - Dismissal Procedures",
            "content": """
Dismissal Procedures under the Labour Relations Act 66 of 1995

The Labour Relations Act 66 of 1995 (LRA) provides comprehensive procedures for fair dismissal in South Africa:

**Substantive Fairness**:
1. **Misconduct**: Serious misconduct may justify dismissal after proper procedures
2. **Incapacity**: Poor performance or ill-health, after support and accommodation
3. **Operational Requirements**: Retrenchment due to economic, technological, or structural reasons

**Procedural Fairness Requirements**:
- Prior notification of allegations
- Right to be heard and represented
- Proper investigation
- Consistent application of disciplinary measures

**Section 188 of the LRA** states that dismissal is unfair if:
- The reason for dismissal is not a fair reason relating to conduct, capacity, or operational requirements
- The dismissal was not effected in accordance with fair procedure

**Constitutional Considerations**:
The right to fair labour practices is enshrined in section 23 of the Constitution. The Constitutional Court in Sidumo v Rustenburg Platinum Mines Ltd 2007 (12) BLLR 1097 (CC) emphasized the importance of procedural fairness.

**CCMA and Labour Courts**:
- Commission for Conciliation, Mediation and Arbitration (CCMA) handles unfair dismissal disputes
- Labour Court has jurisdiction over certain labour matters
- Labour Appeal Court hears appeals from the Labour Court

Recent developments include the amendments addressing labour broking and fixed-term contracts.
            """,
            "document_type": "statute",
            "jurisdiction": "South Africa", 
            "citations": ["Labour Relations Act 66 of 1995", "section 188", "section 23", "Sidumo v Rustenburg Platinum Mines Ltd 2007 (12) BLLR 1097 (CC)"]
        },
        {
            "id": "constitutional_law_sa_001",
            "title": "Constitutional Court Judgment - Freedom of Expression",
            "content": """
IN THE CONSTITUTIONAL COURT OF SOUTH AFRICA

Case CCT 123/2023
[2023] ZACC 15

In the matter between:
MEDIA FREEDOM ORGANIZATION               Applicant
and
MINISTER OF COMMUNICATIONS              First Respondent
BROADCASTING AUTHORITY                  Second Respondent

JUDGMENT

MOGOENG CJ:

Introduction
[1] This matter concerns the interpretation of section 16 of the Constitution, which guarantees freedom of expression. The applicant challenges regulations that impose content restrictions on digital media platforms.

Constitutional Framework
[2] Section 16 of the Constitution provides that everyone has the right to freedom of expression, which includes:
(a) freedom of the press and other media;
(b) freedom to receive or impart information or ideas;
(c) freedom of artistic creativity;
(d) academic freedom and freedom of scientific research.

[3] However, section 16(2) excludes certain expression from constitutional protection, including propaganda for war, incitement of imminent violence, and advocacy of hatred based on race, ethnicity, gender or religion.

Analysis
[4] The Constitutional Court has consistently held that freedom of expression is foundational to democracy. In South African National Defence Union v Minister of Defence 1999 (4) SA 469 (CC), this Court emphasized that democratic government is based on the will of the people, and the will of the people can only be expressed through open debate.

[5] Any limitation of the right to freedom of expression must be justified under section 36 of the Constitution (the limitations clause). The limitation must be reasonable and justifiable in an open and democratic society based on human dignity, equality and freedom.

Conclusion
[6] The impugned regulations fail the proportionality test under section 36. They impose blanket restrictions that go beyond what is necessary to achieve the legitimate government objective of preventing harmful content.

Order
[7] The regulations are declared unconstitutional and invalid.

MOGOENG CJ
For the Constitutional Court
            """,
            "document_type": "judgment",
            "jurisdiction": "South Africa",
            "citations": ["section 16", "section 36", "South African National Defence Union v Minister of Defence 1999 (4) SA 469 (CC)", "[2023] ZACC 15"]
        }
    ]
    
    # Initialize vector store
    vector_store = VectorStoreService()
    await vector_store.initialize()
    
    print("🔄 Adding sample South African legal documents to vector database...")
    
    for doc in sample_documents:
        print(f"📄 Processing: {doc['title']}")
        
        # Parse the document content into chunks
        chunks = []
        content = doc["content"]
        
        # Simple chunking by paragraphs for demo
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 50:  # Skip very short paragraphs
                # Extract citations and legal terms
                citations = sa_legal_parser.extract_citations(paragraph)
                legal_terms = sa_legal_parser.extract_legal_terms(paragraph)
                
                chunk = DocumentChunk(
                    chunk_index=i,
                    content=paragraph,
                    word_count=len(paragraph.split()),
                    citations=[c.text for c in citations] + doc.get("citations", []),
                    legal_terms=legal_terms[:10]  # Limit to 10 terms
                )
                chunks.append(chunk)
        
        # Document metadata
        document_metadata = {
            "title": doc["title"],
            "document_type": doc["document_type"],
            "jurisdiction": doc["jurisdiction"],
            "matter_id": None,
            "file_type": "text"
        }
        
        # Add to vector store
        try:
            chunk_ids = await vector_store.add_document_chunks(
                document_id=doc["id"],
                chunks=chunks,
                document_metadata=document_metadata
            )
            print(f"✅ Added {len(chunk_ids)} chunks for {doc['title']}")
        except Exception as e:
            print(f"❌ Failed to add {doc['title']}: {e}")
    
    # Get collection stats
    stats = await vector_store.get_collection_stats()
    print(f"\n📊 Vector Database Stats:")
    print(f"Total documents: {stats.get('total_documents', 0)}")
    print(f"Total chunks: {stats.get('total_count', 0)}")
    
    await vector_store.close()
    print("\n🎉 Sample legal data added successfully!")

if __name__ == "__main__":
    asyncio.run(populate_test_data())
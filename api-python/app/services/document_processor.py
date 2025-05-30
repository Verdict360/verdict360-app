import PyPDF2
import docx
import re
import io
from typing import List, Dict, Optional, Tuple
from fastapi import UploadFile
import uuid
from datetime import datetime
import aiofiles
import os
from langdetect import detect
from .minio_service import minio_service
from .vector_store import vector_store

class DocumentProcessor:
    """Document processing service for legal documents with South African legal context"""
    
    def __init__(self):
        self.sa_citation_patterns = self._get_sa_citation_patterns()
    
    def _get_sa_citation_patterns(self) -> List[Tuple[str, str]]:
        """
        Get regex patterns for South African legal citations
        Returns list of (pattern, description) tuples
        """
        return [
            # Case law citations
            (r'\d{4}\s+\(\d+\)\s+SA\s+\d+\s+\([A-Z]{2,4}\)', 'SA Law Reports'),
            (r'\[\d{4}\]\s+ZACC\s+\d+', 'Constitutional Court'),
            (r'\[\d{4}\]\s+ZASCA\s+\d+', 'Supreme Court of Appeal'),
            (r'\[\d{4}\]\s+ZAGPPHC\s+\d+', 'Gauteng High Court Pretoria'),
            (r'\[\d{4}\]\s+ZAWCHC\s+\d+', 'Western Cape High Court'),
            (r'\d{4}\s+\(\d+\)\s+BCLR\s+\d+', 'Butterworths Constitutional Law Reports'),
            (r'\d{4}\s+\(\d+\)\s+All\s+SA\s+\d+', 'All South Africa Law Reports'),
            
            # Statute citations
            (r'Act\s+\d+\s+of\s+\d{4}', 'Act of Parliament'),
            (r'Constitution\s+of\s+the\s+Republic\s+of\s+South\s+Africa,?\s+1996', 'Constitution'),
            (r'section\s+\d+(?:\(\d+\))?(?:\([a-z]\))?', 'Section reference'),
            (r'reg(?:ulation)?\s+\d+', 'Regulation reference'),
            
            # Government Gazette
            (r'Government\s+Gazette\s+No\.?\s+\d+', 'Government Gazette'),
            (r'GN\s+\d+', 'Government Notice'),
        ]
    
    async def extract_text_from_file(self, file: UploadFile) -> str:
        """Extract text from uploaded file based on file type"""
        try:
            content = await file.read()
            
            if file.content_type == "application/pdf":
                return self._extract_text_from_pdf(content)
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return self._extract_text_from_docx(content)
            elif file.content_type == "text/plain":
                return content.decode('utf-8')
            else:
                raise ValueError(f"Unsupported file type: {file.content_type}")
                
        except Exception as e:
            raise Exception(f"Failed to extract text: {str(e)}")
    
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract PDF text: {str(e)}")
    
    def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX content"""
        try:
            doc = docx.Document(io.BytesIO(content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
                
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract DOCX text: {str(e)}")
    
    def detect_sa_legal_citations(self, text: str) -> List[Dict[str, str]]:
        """
        Detect South African legal citations in text
        Returns list of citations with their types and positions
        """
        citations = []
        
        for pattern, citation_type in self.sa_citation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                citations.append({
                    "text": match.group(),
                    "type": citation_type,
                    "start": match.start(),
                    "end": match.end(),
                    "context": self._get_citation_context(text, match.start(), match.end())
                })
        
        # Remove duplicates and sort by position
        unique_citations = []
        seen_texts = set()
        
        for citation in sorted(citations, key=lambda x: x["start"]):
            if citation["text"] not in seen_texts:
                unique_citations.append(citation)
                seen_texts.add(citation["text"])
        
        return unique_citations
    
    def _get_citation_context(self, text: str, start: int, end: int, context_length: int = 100) -> str:
        """Get surrounding context for a citation"""
        context_start = max(0, start - context_length)
        context_end = min(len(text), end + context_length)
        
        context = text[context_start:context_end]
        
        # Mark the citation in the context
        citation_in_context = (
            context[:start-context_start] + 
            "**" + text[start:end] + "**" + 
            context[end-context_start:]
        )
        
        return citation_in_context.strip()
    
    def analyze_document_structure(self, text: str) -> Dict[str, any]:
        """Analyze the structure and metadata of the legal document"""
        try:
            language = detect(text)
        except:
            language = "unknown"
        
        word_count = len(text.split())
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # Detect document type indicators
        document_indicators = {
            "judgment": ["plaintiff", "defendant", "judgment", "court", "judge"],
            "contract": ["party", "agreement", "terms", "conditions", "consideration"],
            "statute": ["act", "section", "subsection", "regulation", "minister"],
            "pleading": ["particulars of claim", "statement of case", "prayer", "wherefore"]
        }
        
        detected_types = []
        for doc_type, indicators in document_indicators.items():
            if any(indicator.lower() in text.lower() for indicator in indicators):
                detected_types.append(doc_type)
        
        return {
            "language": language,
            "word_count": word_count,
            "paragraph_count": paragraph_count,
            "estimated_reading_time_minutes": max(1, word_count // 200),
            "detected_document_types": detected_types,
            "has_sa_legal_content": any(
                keyword in text.lower() 
                for keyword in ["south africa", "constitutional court", "high court", "magistrate"]
            )
        }
    
    def chunk_document_for_vectors(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, any]]:
        """
        Split document into chunks for vector storage
        Optimised for legal documents to preserve context
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            # Detect citations and legal terms in this chunk
            chunk_citations = self.detect_sa_legal_citations(chunk_text)
            legal_terms = self._extract_legal_terms(chunk_text)
            
            chunks.append({
                "content": chunk_text,
                "start_word": i,
                "end_word": min(i + chunk_size, len(words)),
                "word_count": len(chunk_words),
                "citations": [c["text"] for c in chunk_citations],
                "legal_terms": legal_terms,
                "metadata": {
                    "has_citations": len(chunk_citations) > 0,
                    "citation_count": len(chunk_citations),
                    "legal_term_count": len(legal_terms)
                }
            })
        
        return chunks
    
    def _extract_legal_terms(self, text: str) -> List[str]:
        """Extract common legal terms from text"""
        legal_terms = [
            "plaintiff", "defendant", "appellant", "respondent", "magistrate",
            "judge", "court", "judgment", "order", "injunction", "damages",
            "contract", "agreement", "breach", "liability", "negligence",
            "constitutional", "statute", "regulation", "section", "subsection",
            "advocate", "attorney", "counsel", "chambers", "affidavit"
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in legal_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    async def process_and_store_document(self, file: UploadFile, metadata: Dict[str, any], user_id: str) -> Dict[str, any]:
        """
        Process a legal document and store both file and results in MinIO + vector store
        """
        document_id = str(uuid.uuid4())
        
        try:
            # Read file content for storage
            await file.seek(0)  # Reset file pointer
            file_content = await file.read()
            
            # Reset file pointer for text extraction
            await file.seek(0)
            
            # Extract text
            text = await self.extract_text_from_file(file)
            
            # Find South African legal citations
            citations = self.detect_sa_legal_citations(text)
            
            # Analyze document structure
            analysis = self.analyze_document_structure(text)
            
            # Create chunks for vector storage
            chunks = self.chunk_document_for_vectors(text)
            
            # Store original file in MinIO
            file_storage_path = minio_service.upload_document(
                user_id=user_id,
                document_id=document_id,
                file_content=file_content,
                filename=file.filename,
                metadata=metadata
            )
            
            # Add chunks to vector store
            await vector_store.add_document_chunks(
                document_id=document_id,
                chunks=chunks,
                document_metadata=metadata
            )
            
            # Generate processing summary
            processing_result = {
                "document_id": document_id,
                "processed_at": datetime.utcnow().isoformat(),
                "file_info": {
                    "name": file.filename,
                    "size": file.size,
                    "type": file.content_type,
                    "storage_path": file_storage_path
                },
                "text_length": len(text),
                "chunk_count": len(chunks),
                "citations_found": len(citations),
                "analysis": analysis,
                "citations": citations,
                "metadata": metadata,
                "vector_storage": {
                    "enabled": True,
                    "chunks_stored": len(chunks),
                    "embedding_model": "all-MiniLM-L6-v2"
                },
                "status": "completed"
            }
            
            # Store processing results in MinIO
            results_storage_path = minio_service.upload_processing_result(
                user_id=user_id,
                document_id=document_id,
                processing_result=processing_result
            )
            
            processing_result["results_storage_path"] = results_storage_path
            
            return processing_result
            
        except Exception as e:
            error_result = {
                "document_id": document_id,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "failed",
                "error": str(e),
                "metadata": metadata
            }
            
            # Try to store error result
            try:
                minio_service.upload_processing_result(user_id, document_id, error_result)
            except:
                pass  # Don't fail completely if we can't store the error
            
            return error_result

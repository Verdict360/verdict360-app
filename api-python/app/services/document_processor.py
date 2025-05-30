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
    
    async def process_and_store_document(self, file: UploadFile, metadata: Dict[str, any], user_id: str) -> Dict[str, any]:
        """
        Process a legal document and store both file and results in MinIO
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
            
            # Store original file in MinIO
            file_storage_path = minio_service.upload_document(
                user_id=user_id,
                document_id=document_id,
                file_content=file_content,
                filename=file.filename,
                metadata=metadata
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
                "citations_found": len(citations),
                "analysis": analysis,
                "citations": citations,
                "metadata": metadata,
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

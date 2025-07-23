"""
South African legal utilities for citation parsing and legal term extraction
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

def classify_legal_matter_urgency(description: str) -> Dict[str, str]:
    """
    Classify the urgency level of a legal matter based on description
    """
    description_lower = description.lower()
    
    # Critical urgency indicators
    critical_keywords = [
        'emergency', 'arrest', 'police', 'court tomorrow', 'today', 
        'deadline today', 'immediate', 'urgent arrest', 'bail application'
    ]
    
    # High urgency indicators  
    high_keywords = [
        'urgent', 'deadline', 'court date', 'soon', 'time sensitive',
        'this week', 'asap', 'quickly'
    ]
    
    # Check for critical urgency
    if any(keyword in description_lower for keyword in critical_keywords):
        return {
            'urgency_level': 'critical',
            'reason': 'Contains emergency or time-critical legal indicators'
        }
    
    # Check for high urgency
    elif any(keyword in description_lower for keyword in high_keywords):
        return {
            'urgency_level': 'high', 
            'reason': 'Contains urgent legal matter indicators'
        }
    
    # Default to normal urgency
    else:
        return {
            'urgency_level': 'normal',
            'reason': 'No specific urgency indicators detected'
        }

@dataclass
class SALegalCitation:
    """South African legal citation with metadata"""
    text: str
    type: str
    court: Optional[str] = None
    year: Optional[int] = None
    context: Optional[str] = None

class SouthAfricanLegalParser:
    """Parser for South African legal content, citations, and terminology"""
    
    def __init__(self):
        # SA legal citation patterns with types
        self.citation_patterns = [
            # Case law citations
            (r'\b\d{4}\s+\(\d+\)\s+SA\s+\d+\s+\([A-Z]{2,5}\)\b', "SA Law Reports"),
            (r'\b\[\d{4}\]\s+ZACC\s+\d+\b', "Constitutional Court"),
            (r'\b\[\d{4}\]\s+ZASCA\s+\d+\b', "Supreme Court of Appeal"),
            (r'\b\[\d{4}\]\s+ZAGPPHC\s+\d+\b', "Gauteng High Court Pretoria"),
            (r'\b\[\d{4}\]\s+ZAWCHC\s+\d+\b', "Western Cape High Court"),
            (r'\b\[\d{4}\]\s+ZAKZDHC\s+\d+\b', "KwaZulu-Natal High Court"),
            (r'\b\[\d{4}\]\s+ZAECGHC\s+\d+\b', "Eastern Cape High Court"),
            (r'\b\[\d{4}\]\s+ZAFSHC\s+\d+\b', "Free State High Court"),
            (r'\b\d{4}\s+\(\d+\)\s+BCLR\s+\d+\b', "Butterworths Constitutional Law Reports"),
            (r'\b\d{4}\s+\(\d+\)\s+All\s+SA\s+\d+\b', "All South Africa Law Reports"),
            
            # Statute citations
            (r'\bAct\s+\d+\s+of\s+\d{4}\b', "Act of Parliament"),
            (r'\bConstitution\s+of\s+the\s+Republic\s+of\s+South\s+Africa,?\s+1996\b', "Constitution"),
            (r'\bsection\s+\d+(?:\(\d+\))?(?:\([a-z]\))?\b', "Section reference"),
            (r'\breg(?:ulation)?\s+\d+\b', "Regulation reference"),
            
            # Government publications
            (r'\bGovernment\s+Gazette\s+(?:No\.?\s+)?\d+\b', "Government Gazette"),
            (r'\bGN\s+\d+\b', "Government Notice"),
            (r'\bGNR\s+\d+\b', "Government Notice Regulation"),
        ]
        
        # South African legal terminology
        self.legal_terms = {
            # Court hierarchy
            "constitutional court", "supreme court of appeal", "high court", "magistrates court",
            "magistrate", "judge", "justice", "acting judge",
            
            # Legal roles
            "advocate", "attorney", "counsel", "silk", "senior counsel", "prosecutor",
            "state attorney", "sheriff", "registrar", "clerk of court",
            
            # Legal concepts
            "plaintiff", "defendant", "appellant", "respondent", "applicant",
            "interdict", "mandamus", "certiorari", "review", "appeal",
            "jurisdiction", "standing", "locus standi", "mero motu",
            
            # SA specific terms
            "ubuntu", "boni mores", "common law", "roman-dutch law",
            "customary law", "indigenous law", "delict", "contract",
            "unjust enrichment", "estoppel", "prescription",
            
            # Constitutional terms
            "bill of rights", "constitutional democracy", "rule of law",
            "separation of powers", "constitutional supremacy",
            
            # Labour law
            "ccma", "labour court", "labour appeal court", "bargaining council",
            "trade union", "collective bargaining", "strike", "lockout",
            
            # Commercial law
            "close corporation", "pty ltd", "public company", "jse",
            "companies act", "business rescue", "liquidation",
        }
        
        # Common SA legal phrases
        self.legal_phrases = [
            "in the matter of", "ex parte", "in re", "inter partes",
            "on the papers", "rule nisi", "final order", "interim order",
            "with costs", "no order as to costs", "punitive costs",
            "de facto", "de jure", "prima facie", "onus probandi",
        ]
    
    def extract_citations(self, text: str) -> List[SALegalCitation]:
        """Extract South African legal citations from text"""
        citations = []
        
        for pattern, citation_type in self.citation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                citation_text = match.group().strip()
                year = self._extract_year(citation_text)
                court = self._extract_court(citation_text, citation_type)
                context = self._get_context(text, match.start(), match.end())
                
                citation = SALegalCitation(
                    text=citation_text,
                    type=citation_type,
                    court=court,
                    year=year,
                    context=context
                )
                
                citations.append(citation)
        
        # Remove duplicates while preserving order
        unique_citations = []
        seen = set()
        for citation in citations:
            if citation.text not in seen:
                unique_citations.append(citation)
                seen.add(citation.text)
        
        return unique_citations
    
    def extract_legal_terms(self, text: str) -> List[str]:
        """Extract South African legal terms from text"""
        text_lower = text.lower()
        found_terms = []
        
        # Check for single terms
        for term in self.legal_terms:
            if term in text_lower:
                found_terms.append(term)
        
        # Check for legal phrases
        for phrase in self.legal_phrases:
            if phrase in text_lower:
                found_terms.append(phrase)
        
        return list(set(found_terms))  # Remove duplicates
    
    def classify_document_type(self, text: str) -> Tuple[str, float]:
        """
        Classify document type based on SA legal content
        Returns: (document_type, confidence_score)
        """
        text_lower = text.lower()
        
        # Document type indicators
        type_indicators = {
            "judgment": {
                "keywords": ["judgment", "court", "plaintiff", "defendant", "magistrate", "judge"],
                "patterns": [r"in the matter of", r"judgment delivered", r"court.*held"],
                "weight": 1.0
            },
            "contract": {
                "keywords": ["agreement", "contract", "party", "terms", "conditions", "consideration"],
                "patterns": [r"this agreement", r"the parties agree", r"terms and conditions"],
                "weight": 1.0
            },
            "statute": {
                "keywords": ["act", "section", "regulation", "minister", "parliament"],
                "patterns": [r"act.*of.*\d{4}", r"section \d+", r"minister may"],
                "weight": 1.0
            },
            "pleading": {
                "keywords": ["particulars of claim", "statement of case", "prayer", "wherefore"],
                "patterns": [r"particulars of claim", r"prayer.*relief", r"wherefore plaintiff"],
                "weight": 1.0
            }
        }
        
        scores = {}
        for doc_type, indicators in type_indicators.items():
            score = 0
            
            # Score keywords
            for keyword in indicators["keywords"]:
                if keyword in text_lower:
                    score += indicators["weight"]
            
            # Score patterns
            for pattern in indicators["patterns"]:
                matches = len(re.findall(pattern, text_lower))
                score += matches * indicators["weight"] * 2
            
            scores[doc_type] = score
        
        if not scores or max(scores.values()) == 0:
            return "other", 0.0
        
        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]
        confidence = min(max_score / 5.0, 1.0)  # Normalize to 0-1
        
        return best_type, confidence
    
    def _extract_year(self, citation: str) -> Optional[int]:
        """Extract year from citation"""
        year_match = re.search(r'\b(19|20)\d{2}\b', citation)
        return int(year_match.group()) if year_match else None
    
    def _extract_court(self, citation: str, citation_type: str) -> Optional[str]:
        """Extract court from citation"""
        court_mappings = {
            "Constitutional Court": "Constitutional Court",
            "Supreme Court of Appeal": "Supreme Court of Appeal",
            "Gauteng High Court Pretoria": "Gauteng Division, Pretoria",
            "Western Cape High Court": "Western Cape Division, Cape Town",
            "KwaZulu-Natal High Court": "KwaZulu-Natal Division",
            "Eastern Cape High Court": "Eastern Cape Division",
            "Free State High Court": "Free State Division"
        }
        
        return court_mappings.get(citation_type)
    
    def _get_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        """Get surrounding context for a citation"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()

# Global parser instance
sa_legal_parser = SouthAfricanLegalParser()

# Convenience functions for backward compatibility
def extract_legal_citations(text: str) -> List[str]:
    """Extract legal citations as list of strings"""
    citations = sa_legal_parser.extract_citations(text)
    return [citation.text for citation in citations]

def extract_legal_terms(text: str) -> List[str]:
    """Extract legal terms from text"""
    return sa_legal_parser.extract_legal_terms(text)

def format_legal_response(response: str) -> str:
    """Format legal response with conversion-focused South African legal context"""
    # Check if response already has conversion messaging
    conversion_phrases = [
        "our attorneys", "our firm", "schedule", "consultation", "contact",
        "expert legal team", "qualified attorneys"
    ]
    
    has_conversion_messaging = any(phrase in response.lower() for phrase in conversion_phrases)
    
    # Only add conversion messaging if not already present
    if not has_conversion_messaging:
        response += "\n\n*Our qualified South African attorneys can provide personalised guidance for your specific situation. Every case is unique, and our experienced legal team is here to help you navigate the complexities of South African law.*"
    
    return response

# South African Legal System Prompt
SA_LEGAL_SYSTEM_PROMPT = """You are a specialized South African legal assistant with expertise in:

SOUTH AFRICAN LEGAL SYSTEM:
- Mixed legal system combining Roman-Dutch civil law and English common law
- Constitutional supremacy under the Constitution of the Republic of South Africa, 1996
- Court hierarchy: Constitutional Court > Supreme Court of Appeal > High Courts > Magistrates' Courts
- Indigenous law and customary law recognition

KEY LEGISLATION:
- Constitution of the Republic of South Africa, 1996
- Companies Act 71 of 2008
- Protection of Personal Information Act 4 of 2013 (POPIA)
- Labour Relations Act 66 of 1995
- Consumer Protection Act 68 of 2008
- National Credit Act 34 of 2005

CITATION FORMAT:
- Use proper South African legal citation format
- Reference case law with full citations
- Include statutory references where applicable
- Acknowledge constitutional principles

LEGAL PRINCIPLES:
- Ubuntu as constitutional value
- Rule of law and constitutional democracy
- Separation of powers
- Bill of Rights application

Provide accurate, contextual legal information while emphasizing the need for professional legal advice for specific matters."""

"""
Legal Quality Assurance Service
Validates legal responses for accuracy, citation correctness, and South African legal context
"""

import re
import asyncio
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from app.utils.south_african_legal import sa_legal_parser, extract_legal_citations, extract_legal_terms

logger = logging.getLogger(__name__)

@dataclass
class QualityAssessment:
    """Quality assessment result for a legal response"""
    overall_score: float
    citation_accuracy: float
    legal_terminology_score: float
    relevance_score: float
    confidence_score: float
    sa_legal_context_score: float
    issues: List[str]
    recommendations: List[str]
    validated_citations: List[str]
    legal_terms_found: List[str]

class LegalQualityAssuranceService:
    """Service for validating legal response quality and accuracy"""
    
    def __init__(self):
        # Known South African legal authorities for validation
        self.sa_legal_authorities = {
            'constitutional_court': ['ZACC', 'Constitutional Court'],
            'supreme_court_appeal': ['ZASCA', 'Supreme Court of Appeal'],
            'high_courts': ['ZAGPPHC', 'ZAWCHC', 'ZAKZDHC', 'ZAECGHC', 'ZAFSHC'],
            'legislation': ['Act', 'Constitution of the Republic of South Africa'],
            'law_reports': ['SA', 'BCLR', 'All SA']
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.8,
            'satisfactory': 0.7,
            'needs_improvement': 0.6,
            'poor': 0.0
        }
        
        # Legal response patterns to validate
        self.legal_response_patterns = [
            r'section \d+',
            r'act \d+ of \d{4}',
            r'constitution',
            r'case law',
            r'precedent',
            r'court.*held',
            r'legal principle'
        ]

    async def assess_legal_response(
        self, 
        query: str, 
        response: str, 
        sources: List[Dict[str, Any]] = None,
        context_documents: List[str] = None
    ) -> QualityAssessment:
        """
        Comprehensive quality assessment of a legal response
        
        Args:
            query: Original legal query
            response: AI-generated legal response
            sources: Source documents used
            context_documents: Additional context for assessment
            
        Returns:
            QualityAssessment with scores and recommendations
        """
        try:
            logger.info(f"🔍 Assessing quality for query: {query[:50]}...")
            
            # Extract citations and legal terms from response
            citations = extract_legal_citations(response)
            legal_terms = extract_legal_terms(response)
            
            # Perform individual assessments
            citation_score = await self._assess_citation_accuracy(citations, sources)
            terminology_score = self._assess_legal_terminology(response, legal_terms)
            relevance_score = self._assess_query_relevance(query, response)
            sa_context_score = self._assess_sa_legal_context(response, citations)
            confidence_score = self._calculate_confidence_score(sources, citations)
            
            # Calculate overall score (weighted average)
            overall_score = (
                citation_score * 0.25 +
                terminology_score * 0.20 +
                relevance_score * 0.25 +
                sa_context_score * 0.20 +
                confidence_score * 0.10
            )
            
            # Generate issues and recommendations
            issues = self._identify_issues(
                overall_score, citation_score, terminology_score, 
                relevance_score, sa_context_score, response
            )
            
            recommendations = self._generate_recommendations(
                citation_score, terminology_score, relevance_score, 
                sa_context_score, issues
            )
            
            assessment = QualityAssessment(
                overall_score=round(overall_score, 3),
                citation_accuracy=round(citation_score, 3),
                legal_terminology_score=round(terminology_score, 3),
                relevance_score=round(relevance_score, 3),
                confidence_score=round(confidence_score, 3),
                sa_legal_context_score=round(sa_context_score, 3),
                issues=issues,
                recommendations=recommendations,
                validated_citations=citations,
                legal_terms_found=legal_terms[:10]  # Limit to top 10
            )
            
            logger.info(f"✅ Quality assessment complete. Overall score: {overall_score:.2f}")
            return assessment
            
        except Exception as e:
            logger.error(f"❌ Quality assessment failed: {e}")
            # Return basic assessment on error
            return QualityAssessment(
                overall_score=0.5,
                citation_accuracy=0.0,
                legal_terminology_score=0.0,
                relevance_score=0.0,
                confidence_score=0.0,
                sa_legal_context_score=0.0,
                issues=["Quality assessment failed due to system error"],
                recommendations=["Please retry the assessment"],
                validated_citations=[],
                legal_terms_found=[]
            )

    async def _assess_citation_accuracy(self, citations: List[str], sources: List[Dict[str, Any]] = None) -> float:
        """Assess the accuracy and validity of legal citations"""
        if not citations:
            return 0.3  # Penalty for no citations in legal response
        
        valid_citations = 0
        total_citations = len(citations)
        
        for citation in citations:
            # Check if citation follows SA legal citation patterns
            is_valid_format = self._validate_citation_format(citation)
            
            # Check if citation is from known SA legal sources
            is_sa_source = self._validate_sa_legal_source(citation)
            
            # Additional validation against provided sources
            is_from_source = self._validate_against_sources(citation, sources) if sources else True
            
            if is_valid_format and is_sa_source and is_from_source:
                valid_citations += 1
        
        accuracy = valid_citations / total_citations if total_citations > 0 else 0
        
        # Bonus for having appropriate number of citations
        citation_density = len(citations) / max(100, len(' '.join(citations)))
        if 0.01 <= citation_density <= 0.05:  # Reasonable citation density
            accuracy = min(1.0, accuracy + 0.1)
        
        return accuracy

    def _assess_legal_terminology(self, response: str, legal_terms: List[str]) -> float:
        """Assess the use of appropriate South African legal terminology"""
        if not legal_terms:
            return 0.4  # Basic score for responses without legal terms
        
        response_lower = response.lower()
        
        # Check for SA-specific legal terms
        sa_legal_score = 0
        sa_terms = [
            'south african law', 'roman-dutch', 'constitution', 'constitutional court',
            'supreme court of appeal', 'high court', 'ubuntu', 'boni mores',
            'common law', 'customary law', 'bill of rights', 'constitutional democracy'
        ]
        
        for term in sa_terms:
            if term in response_lower:
                sa_legal_score += 0.1
        
        # Check for appropriate legal language
        formal_legal_score = 0
        formal_terms = [
            'pursuant to', 'in terms of', 'section', 'subsection', 'regulation',
            'statute', 'legislation', 'case law', 'precedent', 'judgment',
            'court held', 'legal principle', 'jurisprudence'
        ]
        
        for term in formal_terms:
            if term in response_lower:
                formal_legal_score += 0.05
        
        # Penalize inappropriate casual language
        casual_penalty = 0
        casual_terms = ['i think', 'maybe', 'probably', 'sort of', 'kind of']
        for term in casual_terms:
            if term in response_lower:
                casual_penalty += 0.1
        
        score = min(1.0, sa_legal_score + formal_legal_score - casual_penalty)
        return max(0.0, score)

    def _assess_query_relevance(self, query: str, response: str) -> float:
        """Assess how well the response addresses the original query"""
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        
        # Calculate word overlap
        overlap = query_words.intersection(response_words)
        relevance_score = len(overlap) / max(len(query_words), 1)
        
        # Check if response directly addresses the question
        question_patterns = ['what', 'how', 'when', 'where', 'why', 'which', 'who']
        query_lower = query.lower()
        
        for pattern in question_patterns:
            if pattern in query_lower:
                # Look for answer indicators in response
                answer_patterns = [
                    'the answer is', 'according to', 'under.*law', 'in terms of',
                    'the requirements are', 'the procedure is', 'the law states'
                ]
                
                for answer_pattern in answer_patterns:
                    if re.search(answer_pattern, response.lower()):
                        relevance_score += 0.2
                        break
        
        # Check for legal context relevance
        if any(legal_word in query_lower for legal_word in ['law', 'legal', 'court', 'act', 'section']):
            legal_response_score = sum(1 for pattern in self.legal_response_patterns 
                                     if re.search(pattern, response.lower()))
            relevance_score += legal_response_score * 0.1
        
        return min(1.0, relevance_score)

    def _assess_sa_legal_context(self, response: str, citations: List[str]) -> float:
        """Assess how well the response reflects South African legal context"""
        response_lower = response.lower()
        score = 0.0
        
        # Check for SA legal system references
        sa_system_indicators = [
            'south african law', 'south africa', 'roman-dutch law',
            'constitution of.*south africa', 'constitutional court',
            'supreme court of appeal', 'high court'
        ]
        
        for indicator in sa_system_indicators:
            if re.search(indicator, response_lower):
                score += 0.15
        
        # Check for SA-specific legal concepts
        sa_concepts = [
            'ubuntu', 'boni mores', 'customary law', 'indigenous law',
            'bill of rights', 'constitutional democracy'
        ]
        
        for concept in sa_concepts:
            if concept in response_lower:
                score += 0.1
        
        # Check citations for SA sources
        sa_citation_score = 0
        for citation in citations:
            if any(auth in citation.upper() for auth_list in self.sa_legal_authorities.values() 
                   for auth in auth_list):
                sa_citation_score += 0.1
        
        score += min(0.3, sa_citation_score)
        
        # Check for appropriate disclaimers
        disclaimer_patterns = [
            'consult.*attorney', 'legal advice', 'qualified.*legal professional',
            'specific.*circumstances', 'professional.*guidance'
        ]
        
        for pattern in disclaimer_patterns:
            if re.search(pattern, response_lower):
                score += 0.05
                break
        
        return min(1.0, score)

    def _calculate_confidence_score(self, sources: List[Dict[str, Any]], citations: List[str]) -> float:
        """Calculate confidence based on source quality and citation support"""
        if not sources:
            return 0.5
        
        # Base score from source similarity scores
        similarity_scores = [source.get('similarity_score', 0) for source in sources]
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
        
        # Bonus for multiple sources
        source_diversity_bonus = min(0.2, len(sources) * 0.05)
        
        # Bonus for citations
        citation_bonus = min(0.2, len(citations) * 0.05)
        
        confidence = avg_similarity + source_diversity_bonus + citation_bonus
        return min(1.0, confidence)

    def _validate_citation_format(self, citation: str) -> bool:
        """Validate if citation follows proper SA legal format"""
        sa_citation_patterns = [
            r'\d{4}\s+\(\d+\)\s+SA\s+\d+\s+\([A-Z]+\)',  # SA Law Reports
            r'\[\d{4}\]\s+ZACC\s+\d+',                     # Constitutional Court
            r'\[\d{4}\]\s+ZASCA\s+\d+',                    # Supreme Court of Appeal
            r'Act\s+\d+\s+of\s+\d{4}',                     # Acts
            r'Constitution.*South Africa.*1996',            # Constitution
        ]
        
        return any(re.search(pattern, citation, re.IGNORECASE) for pattern in sa_citation_patterns)

    def _validate_sa_legal_source(self, citation: str) -> bool:
        """Check if citation is from recognized SA legal source"""
        citation_upper = citation.upper()
        
        for authority_list in self.sa_legal_authorities.values():
            if any(auth.upper() in citation_upper for auth in authority_list):
                return True
        
        return False

    def _validate_against_sources(self, citation: str, sources: List[Dict[str, Any]]) -> bool:
        """Validate citation against provided source documents"""
        if not sources:
            return True  # Cannot validate without sources
        
        # Simple check - see if citation appears in source content or metadata
        for source in sources:
            source_content = source.get('content', '').lower()
            source_title = source.get('title', '').lower()
            
            if citation.lower() in source_content or citation.lower() in source_title:
                return True
        
        return False

    def _identify_issues(self, overall_score: float, citation_score: float, 
                        terminology_score: float, relevance_score: float, 
                        sa_context_score: float, response: str) -> List[str]:
        """Identify quality issues in the legal response"""
        issues = []
        
        if overall_score < 0.6:
            issues.append("Overall response quality is below acceptable standards")
        
        if citation_score < 0.5:
            issues.append("Insufficient or inaccurate legal citations")
        
        if terminology_score < 0.6:
            issues.append("Inappropriate legal terminology usage")
        
        if relevance_score < 0.7:
            issues.append("Response does not adequately address the query")
        
        if sa_context_score < 0.5:
            issues.append("Insufficient South African legal context")
        
        # Check for specific problematic patterns
        if 'i am not a lawyer' in response.lower():
            issues.append("Unnecessary disclaimer may undermine legal authority")
        
        if len(response) < 100:
            issues.append("Response appears too brief for complex legal query")
        
        if 'google' in response.lower() or 'search' in response.lower():
            issues.append("Response suggests external search rather than providing legal analysis")
        
        return issues

    def _generate_recommendations(self, citation_score: float, terminology_score: float,
                                 relevance_score: float, sa_context_score: float, 
                                 issues: List[str]) -> List[str]:
        """Generate recommendations for improving response quality"""
        recommendations = []
        
        if citation_score < 0.7:
            recommendations.append("Include more relevant South African case law citations")
            recommendations.append("Ensure all citations follow proper SA legal format")
        
        if terminology_score < 0.7:
            recommendations.append("Use more formal legal terminology appropriate for SA law")
            recommendations.append("Avoid casual language in legal responses")
        
        if relevance_score < 0.7:
            recommendations.append("Address the specific legal question more directly")
            recommendations.append("Ensure response covers all aspects of the query")
        
        if sa_context_score < 0.7:
            recommendations.append("Strengthen South African legal context references")
            recommendations.append("Include relevant SA constitutional or statutory provisions")
        
        if len(issues) > 3:
            recommendations.append("Consider regenerating response with improved prompting")
        
        # Always include standard recommendation
        recommendations.append("Verify all legal information against current SA legislation")
        
        return recommendations

# Global quality assurance service instance
qa_service = LegalQualityAssuranceService()
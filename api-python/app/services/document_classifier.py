from typing import Dict, List, Tuple
import re
from collections import Counter

class LegalDocumentClassifier:
    """
    Lightweight document classifier for South African legal documents
    Uses keyword-based classification optimized for legal content
    """
    
    def __init__(self):
        self.classification_rules = {
            "judgment": {
                "keywords": ["judgment", "court", "judge", "plaintiff", "defendant", "appellant", "respondent", "magistrate", "justice"],
                "patterns": [r"\d{4}\s+\(\d+\)\s+SA\s+\d+", r"\[\d{4}\]\s+ZA[A-Z]+\s+\d+"],
                "weight": 1.0
            },
            "contract": {
                "keywords": ["agreement", "contract", "party", "consideration", "terms", "conditions", "breach", "performance"],
                "patterns": [r"party\s+(a|b|1|2)", r"consideration", r"terms\s+and\s+conditions"],
                "weight": 1.0
            },
            "statute": {
                "keywords": ["act", "section", "subsection", "regulation", "minister", "parliament", "gazette"],
                "patterns": [r"Act\s+\d+\s+of\s+\d{4}", r"section\s+\d+", r"regulation\s+\d+"],
                "weight": 1.0
            },
            "pleading": {
                "keywords": ["particulars of claim", "statement of case", "prayer", "wherefore", "pleadings", "affidavit"],
                "patterns": [r"particulars\s+of\s+claim", r"wherefore\s+plaintiff", r"prayer"],
                "weight": 1.0
            },
            "opinion": {
                "keywords": ["opinion", "advice", "counsel", "recommend", "view", "analysis"],
                "patterns": [r"legal\s+opinion", r"in\s+my\s+opinion", r"advised\s+that"],
                "weight": 1.0
            }
        }
    
    def classify_document(self, text: str) -> Dict[str, any]:
        """
        Classify a legal document based on content analysis
        
        Returns:
            Dict with classification results and confidence scores
        """
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Calculate scores for each document type
        type_scores = {}
        
        for doc_type, rules in self.classification_rules.items():
            score = 0
            matches_found = []
            
            # Score based on keywords
            for keyword in rules["keywords"]:
                if keyword in text_lower:
                    score += rules["weight"]
                    matches_found.append(keyword)
            
            # Score based on regex patterns
            for pattern in rules["patterns"]:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    score += len(matches) * rules["weight"] * 2  # Patterns are weighted higher
                    matches_found.extend(matches)
            
            # Normalize score by text length
            normalized_score = score / max(word_count / 100, 1)  # Per 100 words
            
            type_scores[doc_type] = {
                "raw_score": score,
                "normalized_score": normalized_score,
                "matches": matches_found
            }
        
        # Determine primary classification
        best_type = max(type_scores.keys(), key=lambda k: type_scores[k]["normalized_score"])
        confidence = type_scores[best_type]["normalized_score"]
        
        # Classify as "unknown" if confidence is too low
        if confidence < 0.1:
            best_type = "unknown"
            confidence = 0.0
        
        return {
            "primary_type": best_type,
            "confidence": round(confidence, 3),
            "all_scores": {k: round(v["normalized_score"], 3) for k, v in type_scores.items()},
            "matches_found": type_scores.get(best_type, {}).get("matches", []),
            "analysis": {
                "word_count": word_count,
                "has_sa_citations": bool(re.search(r"\d{4}\s+\(\d+\)\s+SA\s+\d+", text)),
                "has_court_references": any(court in text_lower for court in ["constitutional court", "high court", "magistrate"]),
                "language_indicators": self._detect_language_indicators(text_lower)
            }
        }
    
    def _detect_language_indicators(self, text_lower: str) -> Dict[str, bool]:
        """Detect South African language indicators"""
        return {
            "english": any(word in text_lower for word in ["the", "and", "of", "in", "to"]),
            "afrikaans": any(word in text_lower for word in ["die", "en", "van", "in", "tot"]),
            "legal_english": any(phrase in text_lower for phrase in ["plaintiff", "defendant", "whereas", "wherefore"])
        }
    
    def batch_classify(self, documents: List[Dict[str, str]]) -> List[Dict[str, any]]:
        """Classify multiple documents at once"""
        results = []
        
        for doc in documents:
            classification = self.classify_document(doc.get("content", ""))
            classification["document_id"] = doc.get("id", "unknown")
            classification["title"] = doc.get("title", "")
            results.append(classification)
        
        return results

# Global classifier instance
document_classifier = LegalDocumentClassifier()

"""
Test keyword extraction and trending functionality
"""

from app.services.analytics_service import AnalyticsService
from datetime import datetime, date
import asyncio

def test_legal_keyword_extraction():
    """Test keyword extraction from legal text"""
    
    # Create analytics service (without DB for testing)
    analytics_service = AnalyticsService(None)
    
    # Test legal text samples
    test_texts = [
        "I need help with a criminal case involving arrest and police charges",
        "My divorce proceedings require custody arrangements for my children", 
        "The company breach of contract has caused significant damages",
        "I was unfairly dismissed from my employment position",
        "Property transfer documents need review for the deed registration"
    ]
    
    print("🧪 Testing Legal Keyword Extraction")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text[:60]}...")
        
        # Analyze legal content
        analysis = analytics_service._analyze_legal_content([{"content": text}], [])
        
        print(f"   Legal Area: {analysis['legal_area']}")
        print(f"   Complexity: {analysis['complexity']}")
        print(f"   Urgency: {analysis['urgency']}")
        print(f"   Keywords Found: {analysis['keywords']}")
        print(f"   Legal Terms Count: {analysis['terms_count']}")
        print(f"   Follow-up Required: {analysis['follow_up_required']}")

def test_keyword_categorization():
    """Test keyword categorization"""
    
    analytics_service = AnalyticsService(None)
    
    print("\n\n🏷️  Testing Keyword Categorization")
    print("=" * 50)
    
    test_keywords = [
        "constitution", "criminal procedure act", "constitutional court",
        "application", "damages", "negligence", "arrest"
    ]
    
    for keyword in test_keywords:
        category = analytics_service._get_keyword_category(keyword)
        print(f"   '{keyword}' → {category}")

def test_legal_area_classification():
    """Test legal area classification"""
    
    analytics_service = AnalyticsService(None)
    
    print("\n\n⚖️  Testing Legal Area Classification")
    print("=" * 50)
    
    test_cases = [
        ("I was arrested by police for theft charges", "criminal"),
        ("My spouse wants a divorce and child custody", "family"), 
        ("Business partner violated our commercial agreement", "commercial"),
        ("Landlord is evicting me from rental property", "property"),
        ("Employer fired me without proper procedure", "employment"),
        ("Car accident victim wants compensation", "civil")
    ]
    
    for text, expected in test_cases:
        classified = analytics_service._classify_legal_area(text.lower())
        status = "✅" if classified == expected else "❌"
        print(f"   {status} '{text[:40]}...' → {classified} (expected: {expected})")

def test_urgency_assessment():
    """Test urgency level assessment"""
    
    analytics_service = AnalyticsService(None)
    
    print("\n\n🚨 Testing Urgency Assessment")
    print("=" * 50)
    
    test_cases = [
        ("I was just arrested and need help immediately", "critical"),
        ("I have court tomorrow and need urgent help", "critical"),
        ("Police are at my door right now", "critical"),
        ("I need urgent legal advice for my case", "high"),
        ("I have a court date next week", "high"),
        ("I need help with my divorce case", "normal"),
        ("General legal question about contracts", "normal")
    ]
    
    for text, expected in test_cases:
        urgency = analytics_service._assess_urgency(text.lower())
        status = "✅" if urgency == expected else "❌"
        print(f"   {status} '{text[:40]}...' → {urgency} (expected: {expected})")

def test_citation_extraction():
    """Test SA legal citation extraction"""
    
    analytics_service = AnalyticsService(None)
    
    print("\n\n📚 Testing Citation Extraction")
    print("=" * 50)
    
    test_texts = [
        "The case of 2019 ZACC 15 establishes the precedent",
        "According to 2020 ZASCA 89 and 2018 SA 245, the ruling is clear",
        "The Western Cape High Court in 2021 ZAWCHC 67 decided",
        "No legal citations in this general text"
    ]
    
    for text in test_texts:
        citations = analytics_service._extract_citations(text.lower())
        print(f"   '{text[:50]}...'")
        print(f"     Citations found: {citations}")

if __name__ == "__main__":
    print("🚀 Testing Verdict360 Legal Keyword Analysis System")
    print("=" * 60)
    
    test_legal_keyword_extraction()
    test_keyword_categorization()
    test_legal_area_classification()
    test_urgency_assessment()
    test_citation_extraction()
    
    print("\n\n✅ All keyword analysis tests completed!")
    print("\nNext steps:")
    print("1. Connect to live database to test trending keywords")
    print("2. Create sample conversation data")
    print("3. Test analytics dashboard API endpoints")
    print("4. Integrate with frontend dashboard components")
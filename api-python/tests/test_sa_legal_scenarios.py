"""
Comprehensive South African Legal Testing Scenarios
Tests the legal system with real SA legal queries and validates responses
"""

import pytest
import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime

from app.services.legal_quality_assurance import qa_service
from app.services.cache_service import cache_service
from app.api.v1.endpoints.search import process_legal_query, generate_legal_response
from app.services.vector_store import VectorStoreService
from app.utils.south_african_legal import extract_legal_citations, extract_legal_terms

class TestSALegalScenarios:
    """Test suite for South African legal scenarios"""
    
    @pytest.fixture
    def sa_legal_test_cases(self):
        """Real South African legal test scenarios"""
        return [
            {
                "id": "constitutional_rights",
                "category": "Constitutional Law",
                "query": "What are the constitutional rights regarding freedom of expression in South Africa?",
                "expected_citations": ["Constitution of the Republic of South Africa, 1996", "Section 16"],
                "expected_terms": ["freedom of expression", "bill of rights", "constitutional court"],
                "min_quality_score": 0.85,
                "context": "Testing constitutional law knowledge"
            },
            {
                "id": "labour_dispute",
                "category": "Labour Law",
                "query": "What is the process for resolving unfair dismissal disputes under the Labour Relations Act?",
                "expected_citations": ["Labour Relations Act 66 of 1995", "CCMA"],
                "expected_terms": ["unfair dismissal", "CCMA", "labour relations", "arbitration"],
                "min_quality_score": 0.80,
                "context": "Testing labour law procedures"
            },
            {
                "id": "contract_validity",
                "category": "Contract Law",
                "query": "What makes a contract void under South African common law?",
                "expected_citations": ["common law", "roman-dutch law"],
                "expected_terms": ["void contract", "consensus", "capacity", "legality"],
                "min_quality_score": 0.75,
                "context": "Testing contract law principles"
            },
            {
                "id": "criminal_procedure",
                "category": "Criminal Law",
                "query": "What are the bail application procedures under the Criminal Procedure Act?",
                "expected_citations": ["Criminal Procedure Act 51 of 1977", "Section 60"],
                "expected_terms": ["bail application", "detention", "schedule offences"],
                "min_quality_score": 0.80,
                "context": "Testing criminal procedure knowledge"
            },
            {
                "id": "property_transfer",
                "category": "Property Law",
                "query": "What are the requirements for valid property transfer under the Deeds Registries Act?",
                "expected_citations": ["Deeds Registries Act 47 of 1937"],
                "expected_terms": ["property transfer", "deeds office", "registration"],
                "min_quality_score": 0.75,
                "context": "Testing property law procedures"
            },
            {
                "id": "company_directors",
                "category": "Company Law",
                "query": "What are the fiduciary duties of company directors under the Companies Act?",
                "expected_citations": ["Companies Act 71 of 2008"],
                "expected_terms": ["fiduciary duties", "directors", "company law"],
                "min_quality_score": 0.80,
                "context": "Testing corporate law knowledge"
            }
        ]

    @pytest.fixture
    def complex_legal_scenarios(self):
        """Complex multi-jurisdiction scenarios"""
        return [
            {
                "id": "customary_law_marriage",
                "category": "Family Law",
                "query": "How are customary law marriages recognized and what are the property consequences?",
                "expected_citations": ["Recognition of Customary Marriages Act 120 of 1998"],
                "expected_terms": ["customary marriage", "lobola", "community property"],
                "min_quality_score": 0.85,
                "context": "Testing customary law integration"
            },
            {
                "id": "constitutional_court_appeal",
                "category": "Constitutional Law",
                "query": "What is the procedure for direct access to the Constitutional Court?",
                "expected_citations": ["[2019] ZACC", "Constitutional Court Rules"],
                "expected_terms": ["direct access", "constitutional matter", "leave to appeal"],
                "min_quality_score": 0.90,
                "context": "Testing constitutional procedure"
            }
        ]

    async def test_basic_sa_legal_scenarios(self, sa_legal_test_cases):
        """Test basic South African legal scenarios"""
        results = []
        
        for test_case in sa_legal_test_cases:
            print(f"\n🧪 Testing: {test_case['category']} - {test_case['id']}")
            
            # Generate legal response
            mock_sources = [
                {
                    "document_id": f"doc_{test_case['id']}",
                    "document_title": f"SA Legal Document - {test_case['category']}",
                    "content": f"Legal content related to {test_case['query']}",
                    "similarity_score": 0.85,
                    "jurisdiction": "South Africa",
                    "document_type": "legal_article"
                }
            ]
            
            response = await generate_legal_response(
                query=test_case['query'],
                search_results=mock_sources,
                jurisdiction="South Africa"
            )
            
            # Extract citations and terms
            citations = extract_legal_citations(response)
            legal_terms = extract_legal_terms(response)
            
            # Quality assessment
            assessment = await qa_service.assess_legal_response(
                query=test_case['query'],
                response=response,
                sources=mock_sources
            )
            
            # Validate results
            test_result = {
                "test_case_id": test_case['id'],
                "category": test_case['category'],
                "query": test_case['query'],
                "response_length": len(response),
                "citations_found": len(citations),
                "legal_terms_found": len(legal_terms),
                "quality_score": assessment.overall_score,
                "citation_accuracy": assessment.citation_accuracy,
                "sa_context_score": assessment.sa_legal_context_score,
                "passed": assessment.overall_score >= test_case['min_quality_score'],
                "issues": assessment.issues,
                "recommendations": assessment.recommendations
            }
            
            results.append(test_result)
            
            # Assert minimum quality standards
            assert assessment.overall_score >= test_case['min_quality_score'], \
                f"Quality score {assessment.overall_score} below minimum {test_case['min_quality_score']} for {test_case['id']}"
            
            # Assert SA legal context
            assert assessment.sa_legal_context_score >= 0.7, \
                f"SA legal context score too low: {assessment.sa_legal_context_score}"
            
            print(f"✅ Passed: Quality {assessment.overall_score:.2f}, SA Context {assessment.sa_legal_context_score:.2f}")
        
        return results

    async def test_citation_accuracy(self, sa_legal_test_cases):
        """Test citation accuracy and format validation"""
        citation_results = []
        
        for test_case in sa_legal_test_cases:
            print(f"\n📚 Testing citations for: {test_case['id']}")
            
            # Create mock response with expected citations
            mock_response = f"""
            Based on South African law, regarding {test_case['query']}:
            
            The Constitution of the Republic of South Africa, 1996 provides fundamental guidance.
            Section 16 addresses freedom of expression.
            The Labour Relations Act 66 of 1995 governs employment matters.
            See [2019] ZACC 13 for Constitutional Court guidance.
            Act 71 of 2008 (Companies Act) regulates corporate governance.
            """
            
            citations = extract_legal_citations(mock_response)
            
            # Validate citation formats
            valid_citations = 0
            for citation in citations:
                if any(expected in citation for expected in test_case.get('expected_citations', [])):
                    valid_citations += 1
            
            citation_accuracy = valid_citations / max(len(citations), 1)
            
            citation_result = {
                "test_case_id": test_case['id'],
                "total_citations": len(citations),
                "valid_citations": valid_citations,
                "citation_accuracy": citation_accuracy,
                "citations": citations
            }
            
            citation_results.append(citation_result)
            
            # Assert citation quality
            assert citation_accuracy >= 0.6, \
                f"Citation accuracy too low: {citation_accuracy} for {test_case['id']}"
            
            print(f"✅ Citation accuracy: {citation_accuracy:.2f}")
        
        return citation_results

    async def test_legal_terminology_validation(self, sa_legal_test_cases):
        """Test legal terminology usage and accuracy"""
        terminology_results = []
        
        for test_case in sa_legal_test_cases:
            print(f"\n📖 Testing terminology for: {test_case['id']}")
            
            # Generate response with legal terms
            mock_response = f"""
            In South African law, {test_case['query']} involves several key legal principles.
            The constitutional framework provides guidance through the Bill of Rights.
            Common law principles from Roman-Dutch law also apply.
            Legal practitioners must consider precedent from the Constitutional Court.
            """
            
            legal_terms = extract_legal_terms(mock_response)
            
            # Check for expected terms
            expected_terms_found = 0
            for expected_term in test_case.get('expected_terms', []):
                if any(expected_term.lower() in term.lower() for term in legal_terms):
                    expected_terms_found += 1
            
            terminology_score = expected_terms_found / max(len(test_case.get('expected_terms', [])), 1)
            
            terminology_result = {
                "test_case_id": test_case['id'],
                "expected_terms": test_case.get('expected_terms', []),
                "found_terms": legal_terms,
                "expected_terms_found": expected_terms_found,
                "terminology_score": terminology_score
            }
            
            terminology_results.append(terminology_result)
            
            # Assert terminology quality
            assert terminology_score >= 0.4, \
                f"Terminology score too low: {terminology_score} for {test_case['id']}"
            
            print(f"✅ Terminology score: {terminology_score:.2f}")
        
        return terminology_results

    async def test_cache_performance(self):
        """Test caching performance with legal queries"""
        print("\n⚡ Testing cache performance...")
        
        test_query = "What are the constitutional rights in South Africa?"
        
        # Clear cache first
        await cache_service.clear_cache()
        
        # First query (cache miss)
        start_time = datetime.now()
        await cache_service.get_legal_query(test_query)
        cache_miss_time = (datetime.now() - start_time).total_seconds()
        
        # Cache the query
        test_response = {
            "success": True,
            "response": "Constitutional rights are protected...",
            "confidence_score": 0.95
        }
        await cache_service.set_legal_query(test_query, test_response)
        
        # Second query (cache hit)
        start_time = datetime.now()
        cached_result = await cache_service.get_legal_query(test_query)
        cache_hit_time = (datetime.now() - start_time).total_seconds()
        
        # Validate cache performance
        assert cached_result is not None, "Cache should return stored query"
        assert cache_hit_time < cache_miss_time, "Cache hit should be faster than miss"
        
        # Get cache statistics
        stats = cache_service.get_cache_stats()
        
        print(f"✅ Cache performance - Hit: {cache_hit_time:.4f}s, Miss: {cache_miss_time:.4f}s")
        print(f"📊 Cache stats: {stats['hit_rate_percent']:.1f}% hit rate")
        
        return {
            "cache_hit_time": cache_hit_time,
            "cache_miss_time": cache_miss_time,
            "cache_stats": stats
        }

    async def test_quality_assurance_thresholds(self):
        """Test quality assurance scoring thresholds"""
        print("\n🎯 Testing QA thresholds...")
        
        test_scenarios = [
            {
                "query": "Constitutional law in South Africa",
                "response": "The Constitution of the Republic of South Africa, 1996 is the supreme law. Section 16 protects freedom of expression.",
                "expected_score_range": (0.85, 1.0),
                "description": "High quality response"
            },
            {
                "query": "Labour law question",
                "response": "I think maybe the Labour Relations Act might help. You should probably google it.",
                "expected_score_range": (0.0, 0.5),
                "description": "Poor quality response"
            },
            {
                "query": "Property transfer process",
                "response": "Property transfer in South Africa requires registration at the Deeds Office under the Deeds Registries Act 47 of 1937.",
                "expected_score_range": (0.7, 0.9),
                "description": "Good quality response"
            }
        ]
        
        qa_results = []
        
        for scenario in test_scenarios:
            assessment = await qa_service.assess_legal_response(
                query=scenario['query'],
                response=scenario['response']
            )
            
            min_score, max_score = scenario['expected_score_range']
            score_in_range = min_score <= assessment.overall_score <= max_score
            
            qa_result = {
                "description": scenario['description'],
                "score": assessment.overall_score,
                "expected_range": scenario['expected_score_range'],
                "in_range": score_in_range,
                "issues": assessment.issues,
                "recommendations": assessment.recommendations
            }
            
            qa_results.append(qa_result)
            
            assert score_in_range, \
                f"Score {assessment.overall_score} not in expected range {scenario['expected_score_range']}"
            
            print(f"✅ {scenario['description']}: {assessment.overall_score:.2f}")
        
        return qa_results

    async def test_complete_workflow(self):
        """Test complete legal query workflow"""
        print("\n🔄 Testing complete workflow...")
        
        test_query = "What are the requirements for a valid contract in South African law?"
        
        # Mock vector store results
        mock_sources = [
            {
                "document_id": "contract_law_001",
                "document_title": "South African Contract Law Principles",
                "content": "A valid contract requires consensus, capacity, formalities, and legality of performance.",
                "similarity_score": 0.92,
                "jurisdiction": "South Africa",
                "document_type": "legal_textbook"
            }
        ]
        
        # Generate response
        response = await generate_legal_response(
            query=test_query,
            search_results=mock_sources,
            jurisdiction="South Africa"
        )
        
        # Extract legal elements
        citations = extract_legal_citations(response)
        legal_terms = extract_legal_terms(response)
        
        # Quality assessment
        assessment = await qa_service.assess_legal_response(
            query=test_query,
            response=response,
            sources=mock_sources
        )
        
        # Cache the result
        response_data = {
            "success": True,
            "response": response,
            "sources": mock_sources,
            "query": test_query,
            "legal_citations": citations,
            "legal_terms": legal_terms,
            "confidence_score": assessment.overall_score,
            "jurisdiction": "South Africa"
        }
        
        await cache_service.set_legal_query(test_query, response_data, "South Africa")
        
        # Validate workflow results
        workflow_result = {
            "query": test_query,
            "response_generated": len(response) > 0,
            "citations_extracted": len(citations),
            "legal_terms_extracted": len(legal_terms),
            "quality_score": assessment.overall_score,
            "cached_successfully": True,
            "workflow_complete": True
        }
        
        # Assert workflow quality
        assert assessment.overall_score >= 0.7, "Workflow should produce quality responses"
        assert len(response) > 100, "Response should be substantive"
        assert assessment.sa_legal_context_score >= 0.6, "Should maintain SA legal context"
        
        print(f"✅ Workflow complete - Quality: {assessment.overall_score:.2f}")
        
        return workflow_result

# Test runner function
async def run_sa_legal_tests():
    """Run all South African legal tests"""
    test_suite = TestSALegalScenarios()
    
    print("🇿🇦 Starting South African Legal System Tests...")
    print("=" * 60)
    
    try:
        # Load test fixtures
        sa_test_cases = test_suite.sa_legal_test_cases()
        complex_scenarios = test_suite.complex_legal_scenarios()
        
        # Run test suites
        basic_results = await test_suite.test_basic_sa_legal_scenarios(sa_test_cases)
        citation_results = await test_suite.test_citation_accuracy(sa_test_cases)
        terminology_results = await test_suite.test_legal_terminology_validation(sa_test_cases)
        cache_results = await test_suite.test_cache_performance()
        qa_results = await test_suite.test_quality_assurance_thresholds()
        workflow_results = await test_suite.test_complete_workflow()
        
        # Compile final report
        test_report = {
            "test_timestamp": datetime.now().isoformat(),
            "total_test_cases": len(sa_test_cases),
            "basic_scenarios": {
                "passed": sum(1 for r in basic_results if r['passed']),
                "total": len(basic_results),
                "average_quality": sum(r['quality_score'] for r in basic_results) / len(basic_results)
            },
            "citation_accuracy": {
                "average_accuracy": sum(r['citation_accuracy'] for r in citation_results) / len(citation_results),
                "total_citations_tested": sum(r['total_citations'] for r in citation_results)
            },
            "terminology_validation": {
                "average_score": sum(r['terminology_score'] for r in terminology_results) / len(terminology_results)
            },
            "cache_performance": cache_results,
            "quality_assurance": qa_results,
            "workflow_test": workflow_results
        }
        
        print("\n📊 TEST SUMMARY")
        print("=" * 40)
        print(f"✅ Basic scenarios passed: {test_report['basic_scenarios']['passed']}/{test_report['basic_scenarios']['total']}")
        print(f"📈 Average quality score: {test_report['basic_scenarios']['average_quality']:.2f}")
        print(f"📚 Citation accuracy: {test_report['citation_accuracy']['average_accuracy']:.2f}")
        print(f"📖 Terminology score: {test_report['terminology_validation']['average_score']:.2f}")
        print(f"⚡ Cache hit rate: {cache_results['cache_stats']['hit_rate_percent']:.1f}%")
        print(f"🎯 QA thresholds validated: {len(qa_results)} scenarios")
        print(f"🔄 Complete workflow: {'✅ PASSED' if workflow_results['workflow_complete'] else '❌ FAILED'}")
        
        return test_report
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        raise

if __name__ == "__main__":
    # Run the test suite
    import asyncio
    
    async def main():
        report = await run_sa_legal_tests()
        
        # Save test report
        with open("/Users/thando/Documents/verdict360-app/api-python/tests/sa_legal_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📋 Test report saved to: sa_legal_test_report.json")
        return report
    
    asyncio.run(main())
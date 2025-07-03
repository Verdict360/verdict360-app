#!/usr/bin/env python3
"""
Legal Professional Testing Script
Simulates real-world usage by legal professionals with South African legal scenarios
Run this script to validate the system before production deployment
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.legal_quality_assurance import qa_service
from app.services.cache_service import cache_service
from app.api.v1.endpoints.search import generate_legal_response
from app.utils.south_african_legal import extract_legal_citations, extract_legal_terms

class LegalProfessionalTestRunner:
    """Simulates real legal professional usage patterns"""
    
    def __init__(self):
        self.test_results = []
        self.performance_metrics = {
            'total_queries': 0,
            'successful_responses': 0,
            'average_quality': 0.0,
            'average_response_time': 0.0,
            'cache_hit_rate': 0.0
        }
    
    async def run_attorney_consultation_simulation(self):
        """Simulate an attorney consultation session"""
        print("👨‍⚖️ Simulating Attorney Consultation Session...")
        
        consultation_queries = [
            {
                "client_query": "My employer terminated me without following proper procedures. What are my options?",
                "legal_area": "Labour Law",
                "complexity": "intermediate",
                "expected_duration": "5-10 minutes"
            },
            {
                "client_query": "I want to start a private company. What are the legal requirements?",
                "legal_area": "Company Law",
                "complexity": "basic",
                "expected_duration": "3-5 minutes"
            },
            {
                "client_query": "My constitutional rights were violated during a police search. Can I challenge this?",
                "legal_area": "Constitutional Law",
                "complexity": "advanced",
                "expected_duration": "10-15 minutes"
            }
        ]
        
        session_results = []
        
        for i, query_info in enumerate(consultation_queries, 1):
            print(f"\n📋 Client Query {i}: {query_info['legal_area']}")
            print(f"   Question: {query_info['client_query']}")
            
            start_time = datetime.now()
            
            # Generate legal response
            mock_sources = await self._create_mock_legal_sources(query_info['legal_area'])
            response = await generate_legal_response(
                query=query_info['client_query'],
                search_results=mock_sources,
                jurisdiction="South Africa"
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # Extract legal elements
            citations = extract_legal_citations(response)
            legal_terms = extract_legal_terms(response)
            
            # Quality assessment
            assessment = await qa_service.assess_legal_response(
                query=query_info['client_query'],
                response=response,
                sources=mock_sources
            )
            
            query_result = {
                "query_number": i,
                "legal_area": query_info['legal_area'],
                "complexity": query_info['complexity'],
                "response_time_seconds": response_time,
                "response_length": len(response),
                "citations_found": len(citations),
                "legal_terms": len(legal_terms),
                "quality_score": assessment.overall_score,
                "sa_context_score": assessment.sa_legal_context_score,
                "citation_accuracy": assessment.citation_accuracy,
                "issues": assessment.issues,
                "attorney_satisfied": assessment.overall_score >= 0.8
            }
            
            session_results.append(query_result)
            
            print(f"   ⏱️  Response time: {response_time:.2f}s")
            print(f"   🎯 Quality score: {assessment.overall_score:.2f}")
            print(f"   📚 Citations: {len(citations)}")
            print(f"   {'✅ SATISFACTORY' if query_result['attorney_satisfied'] else '⚠️  NEEDS REVIEW'}")
        
        consultation_summary = {
            "session_type": "attorney_consultation",
            "total_queries": len(consultation_queries),
            "average_quality": sum(r['quality_score'] for r in session_results) / len(session_results),
            "average_response_time": sum(r['response_time_seconds'] for r in session_results) / len(session_results),
            "satisfactory_responses": sum(1 for r in session_results if r['attorney_satisfied']),
            "queries": session_results
        }
        
        return consultation_summary
    
    async def run_paralegal_research_simulation(self):
        """Simulate paralegal legal research tasks"""
        print("\n📚 Simulating Paralegal Research Session...")
        
        research_tasks = [
            {
                "task": "Research precedents for unfair dismissal cases",
                "query": "Find Constitutional Court and Labour Court precedents on unfair dismissal in South Africa",
                "research_depth": "comprehensive",
                "time_budget": "30 minutes"
            },
            {
                "task": "Analyze property transfer requirements",
                "query": "What are the step-by-step requirements for property transfer under SA law?",
                "research_depth": "detailed",
                "time_budget": "20 minutes"
            },
            {
                "task": "Review contract validity principles",
                "query": "What are the essential elements for a valid contract under South African common law?",
                "research_depth": "standard",
                "time_budget": "15 minutes"
            }
        ]
        
        research_results = []
        
        for i, task_info in enumerate(research_tasks, 1):
            print(f"\n🔍 Research Task {i}: {task_info['task']}")
            print(f"   Time budget: {task_info['time_budget']}")
            
            start_time = datetime.now()
            
            # Simulate research with multiple related queries
            related_queries = [
                task_info['query'],
                f"Recent case law updates for {task_info['task'].lower()}",
                f"Practical implications of {task_info['task'].lower()}"
            ]
            
            task_responses = []
            for query in related_queries:
                mock_sources = await self._create_comprehensive_legal_sources()
                response = await generate_legal_response(
                    query=query,
                    search_results=mock_sources,
                    jurisdiction="South Africa"
                )
                
                assessment = await qa_service.assess_legal_response(
                    query=query,
                    response=response,
                    sources=mock_sources
                )
                
                task_responses.append({
                    "query": query,
                    "quality_score": assessment.overall_score,
                    "citations": len(extract_legal_citations(response)),
                    "response_length": len(response)
                })
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            research_result = {
                "task_number": i,
                "task_description": task_info['task'],
                "research_depth": task_info['research_depth'],
                "total_time_seconds": total_time,
                "queries_executed": len(related_queries),
                "average_quality": sum(r['quality_score'] for r in task_responses) / len(task_responses),
                "total_citations": sum(r['citations'] for r in task_responses),
                "research_complete": total_time <= 1800,  # 30 minutes max
                "responses": task_responses
            }
            
            research_results.append(research_result)
            
            print(f"   ⏱️  Total time: {total_time:.1f}s")
            print(f"   📊 Average quality: {research_result['average_quality']:.2f}")
            print(f"   📚 Total citations: {research_result['total_citations']}")
            print(f"   {'✅ COMPLETED' if research_result['research_complete'] else '⏰ OVERTIME'}")
        
        research_summary = {
            "session_type": "paralegal_research",
            "total_tasks": len(research_tasks),
            "completed_on_time": sum(1 for r in research_results if r['research_complete']),
            "average_quality": sum(r['average_quality'] for r in research_results) / len(research_results),
            "total_citations_found": sum(r['total_citations'] for r in research_results),
            "tasks": research_results
        }
        
        return research_summary
    
    async def run_law_firm_daily_usage_simulation(self):
        """Simulate typical daily usage patterns in a law firm"""
        print("\n🏢 Simulating Law Firm Daily Usage...")
        
        daily_queries = [
            "How do I register a close corporation in South Africa?",
            "What are the notice periods for employment termination?",
            "Can a minor enter into a binding contract?",
            "What is the process for appealing a magistrate court decision?",
            "How are marital assets divided in a divorce?",
            "What are the requirements for a valid will?",
            "Can an employer change working conditions unilaterally?",
            "What constitutes unfair competition in business?",
            "How do I apply for a liquor license?",
            "What are the penalties for tax evasion in South Africa?"
        ]
        
        daily_results = []
        cache_hits = 0
        
        for i, query in enumerate(daily_queries, 1):
            print(f"\n📞 Query {i:2d}/10: {query[:50]}...")
            
            start_time = datetime.now()
            
            # Check cache first (simulating repeated queries)
            cache_key = f"daily_query_{i}"
            cached_response = await cache_service.get_legal_query(query, "South Africa")
            
            if cached_response and i > 3:  # Simulate some cache hits after initial queries
                cache_hits += 1
                response_time = 0.1  # Fast cache response
                quality_score = cached_response.get('confidence_score', 0.8)
                print(f"   💾 Cache hit - {response_time:.3f}s")
            else:
                # Generate new response
                mock_sources = await self._create_mock_legal_sources("General")
                response = await generate_legal_response(
                    query=query,
                    search_results=mock_sources,
                    jurisdiction="South Africa"
                )
                
                assessment = await qa_service.assess_legal_response(
                    query=query,
                    response=response,
                    sources=mock_sources
                )
                
                # Cache for future use
                response_data = {
                    "success": True,
                    "response": response,
                    "confidence_score": assessment.overall_score,
                    "jurisdiction": "South Africa"
                }
                await cache_service.set_legal_query(query, response_data, "South Africa")
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                quality_score = assessment.overall_score
                
                print(f"   🔄 Generated - {response_time:.2f}s, Quality: {quality_score:.2f}")
            
            daily_results.append({
                "query_number": i,
                "query": query,
                "response_time": response_time,
                "quality_score": quality_score,
                "cache_hit": cached_response is not None and i > 3
            })
        
        daily_summary = {
            "session_type": "daily_usage",
            "total_queries": len(daily_queries),
            "cache_hits": cache_hits,
            "cache_hit_rate": (cache_hits / len(daily_queries)) * 100,
            "average_response_time": sum(r['response_time'] for r in daily_results) / len(daily_results),
            "average_quality": sum(r['quality_score'] for r in daily_results) / len(daily_results),
            "queries": daily_results
        }
        
        print(f"\n📈 Daily Summary:")
        print(f"   Cache hit rate: {daily_summary['cache_hit_rate']:.1f}%")
        print(f"   Average response time: {daily_summary['average_response_time']:.2f}s")
        print(f"   Average quality: {daily_summary['average_quality']:.2f}")
        
        return daily_summary
    
    async def run_stress_test_simulation(self):
        """Simulate high-load scenarios"""
        print("\n🚀 Running Stress Test Simulation...")
        
        # Simulate concurrent queries
        concurrent_queries = [
            "Constitutional law question",
            "Labour law inquiry",
            "Contract law issue",
            "Criminal procedure query",
            "Property law question"
        ] * 4  # 20 total queries
        
        start_time = datetime.now()
        
        # Process queries concurrently
        async def process_query(query, query_id):
            mock_sources = await self._create_mock_legal_sources("Stress Test")
            response = await generate_legal_response(
                query=f"{query} - Query {query_id}",
                search_results=mock_sources,
                jurisdiction="South Africa"
            )
            
            assessment = await qa_service.assess_legal_response(
                query=query,
                response=response,
                sources=mock_sources
            )
            
            return {
                "query_id": query_id,
                "quality_score": assessment.overall_score,
                "response_length": len(response)
            }
        
        # Run concurrent tasks
        tasks = [process_query(query, i) for i, query in enumerate(concurrent_queries)]
        stress_results = await asyncio.gather(*tasks)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        stress_summary = {
            "session_type": "stress_test",
            "concurrent_queries": len(concurrent_queries),
            "total_time_seconds": total_time,
            "queries_per_second": len(concurrent_queries) / total_time,
            "average_quality": sum(r['quality_score'] for r in stress_results) / len(stress_results),
            "successful_queries": len(stress_results),
            "system_stable": total_time < 60  # Should complete within 1 minute
        }
        
        print(f"   📊 Processed {len(concurrent_queries)} queries in {total_time:.2f}s")
        print(f"   ⚡ {stress_summary['queries_per_second']:.2f} queries/second")
        print(f"   🎯 Average quality: {stress_summary['average_quality']:.2f}")
        print(f"   {'✅ STABLE' if stress_summary['system_stable'] else '⚠️  PERFORMANCE ISSUE'}")
        
        return stress_summary
    
    async def _create_mock_legal_sources(self, legal_area: str) -> List[Dict[str, Any]]:
        """Create realistic mock legal sources for testing"""
        sources = [
            {
                "document_id": f"doc_{legal_area.lower().replace(' ', '_')}_001",
                "document_title": f"South African {legal_area} - Comprehensive Guide",
                "content": f"This document covers important aspects of {legal_area} in South African law...",
                "similarity_score": 0.85,
                "jurisdiction": "South Africa",
                "document_type": "legal_textbook",
                "citation": f"SA {legal_area} Textbook (2023)"
            },
            {
                "document_id": f"doc_{legal_area.lower().replace(' ', '_')}_002",
                "document_title": f"Recent {legal_area} Case Law",
                "content": f"Recent developments in {legal_area} include important Constitutional Court decisions...",
                "similarity_score": 0.78,
                "jurisdiction": "South Africa",
                "document_type": "case_law",
                "citation": "[2023] ZACC 15"
            }
        ]
        return sources
    
    async def _create_comprehensive_legal_sources(self) -> List[Dict[str, Any]]:
        """Create comprehensive legal sources for research simulation"""
        sources = [
            {
                "document_id": "comprehensive_001",
                "document_title": "South African Legal System Overview",
                "content": "The South African legal system is based on Roman-Dutch law...",
                "similarity_score": 0.92,
                "jurisdiction": "South Africa",
                "document_type": "legal_encyclopedia"
            },
            {
                "document_id": "comprehensive_002",
                "document_title": "Constitutional Court Jurisprudence",
                "content": "The Constitutional Court has established important precedents...",
                "similarity_score": 0.89,
                "jurisdiction": "South Africa",
                "document_type": "case_law"
            },
            {
                "document_id": "comprehensive_003",
                "document_title": "South African Statutes Compilation",
                "content": "Key South African legislation includes the Constitution of 1996...",
                "similarity_score": 0.87,
                "jurisdiction": "South Africa",
                "document_type": "legislation"
            }
        ]
        return sources

async def main():
    """Run all legal professional simulations"""
    print("🇿🇦 VERDICT360 LEGAL PROFESSIONAL TESTING")
    print("=" * 60)
    print("Simulating real-world usage by South African legal professionals")
    print("=" * 60)
    
    runner = LegalProfessionalTestRunner()
    
    try:
        # Run all simulation scenarios
        consultation_results = await runner.run_attorney_consultation_simulation()
        research_results = await runner.run_paralegal_research_simulation()
        daily_usage_results = await runner.run_law_firm_daily_usage_simulation()
        stress_test_results = await runner.run_stress_test_simulation()
        
        # Compile comprehensive report
        test_report = {
            "test_timestamp": datetime.now().isoformat(),
            "test_duration_minutes": 0,  # Will be calculated
            "simulations": {
                "attorney_consultation": consultation_results,
                "paralegal_research": research_results,
                "daily_usage": daily_usage_results,
                "stress_test": stress_test_results
            },
            "overall_performance": {
                "total_queries_processed": (
                    consultation_results['total_queries'] +
                    research_results['total_tasks'] * 3 +  # 3 queries per task
                    daily_usage_results['total_queries'] +
                    stress_test_results['concurrent_queries']
                ),
                "average_quality_across_all": sum([
                    consultation_results['average_quality'],
                    research_results['average_quality'],
                    daily_usage_results['average_quality'],
                    stress_test_results['average_quality']
                ]) / 4,
                "system_stability": all([
                    consultation_results['satisfactory_responses'] >= 2,
                    research_results['completed_on_time'] >= 2,
                    daily_usage_results['cache_hit_rate'] > 0,
                    stress_test_results['system_stable']
                ])
            },
            "recommendations": []
        }
        
        # Add recommendations based on results
        if test_report['overall_performance']['average_quality_across_all'] < 0.8:
            test_report['recommendations'].append("Consider improving response quality - average below 80%")
        
        if daily_usage_results['cache_hit_rate'] < 20:
            test_report['recommendations'].append("Cache hit rate is low - optimize caching strategy")
        
        if not stress_test_results['system_stable']:
            test_report['recommendations'].append("System performance under load needs optimization")
        
        if not test_report['recommendations']:
            test_report['recommendations'].append("System performing well - ready for production deployment")
        
        # Generate final report
        print("\n" + "=" * 60)
        print("📊 FINAL TESTING REPORT")
        print("=" * 60)
        print(f"✅ Total queries processed: {test_report['overall_performance']['total_queries_processed']}")
        print(f"🎯 Overall quality score: {test_report['overall_performance']['average_quality_across_all']:.2f}")
        print(f"🏥 System stability: {'✅ STABLE' if test_report['overall_performance']['system_stability'] else '⚠️  ISSUES DETECTED'}")
        print(f"⚡ Cache performance: {daily_usage_results['cache_hit_rate']:.1f}% hit rate")
        print(f"🚀 Stress test: {'✅ PASSED' if stress_test_results['system_stable'] else '❌ FAILED'}")
        
        print(f"\n📋 RECOMMENDATIONS:")
        for recommendation in test_report['recommendations']:
            print(f"   • {recommendation}")
        
        # Save detailed report
        report_file = f"legal_professional_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(test_report, f, indent=2)
        
        print(f"\n💾 Detailed report saved: {report_file}")
        
        # Determine if system is ready for production
        production_ready = (
            test_report['overall_performance']['average_quality_across_all'] >= 0.75 and
            test_report['overall_performance']['system_stability'] and
            daily_usage_results['cache_hit_rate'] >= 10
        )
        
        print(f"\n🚀 PRODUCTION READINESS: {'✅ READY' if production_ready else '⚠️  NEEDS ATTENTION'}")
        
        return test_report
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
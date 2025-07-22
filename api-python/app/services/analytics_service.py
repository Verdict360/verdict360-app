"""
Analytics service for legal chatbot dashboard
Processes conversation data and generates business intelligence insights
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from app.models.analytics import (
    ConversationAnalytics, LegalKeywordAnalytics, LawFirmMetrics,
    ClientJourney, AnalyticsSnapshot
)

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for processing and analyzing conversation data"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Legal keyword categories for analysis
        self.legal_keywords = {
            'statutes': [
                'constitution', 'criminal procedure act', 'companies act', 
                'labour relations act', 'consumer protection act', 'matrimonial property act'
            ],
            'case_law': [
                'constitutional court', 'supreme court of appeal', 'high court',
                'precedent', 'judgment', 'ruling'
            ],
            'procedures': [
                'application', 'motion', 'appeal', 'trial', 'hearing', 
                'pleading', 'discovery', 'subpoena'
            ],
            'concepts': [
                'damages', 'liability', 'negligence', 'contract', 'breach',
                'custody', 'maintenance', 'divorce', 'arrest', 'bail'
            ]
        }

    # Core Analytics Processing

    async def process_conversation_analytics(
        self,
        conversation_data: Dict[str, Any],
        conversation_type: str = "chat"
    ) -> ConversationAnalytics:
        """Process conversation data and create analytics record"""
        try:
            # Extract metrics from conversation data
            metrics = self._extract_conversation_metrics(conversation_data, conversation_type)
            
            # Analyze legal context
            legal_analysis = self._analyze_legal_content(
                conversation_data.get('messages', []),
                conversation_data.get('transcript', [])
            )
            
            # Create analytics record
            analytics = ConversationAnalytics(
                conversation_id=conversation_data.get('conversation_id'),
                voice_call_id=conversation_data.get('voice_call_id'),
                consultation_id=conversation_data.get('consultation_id'),
                conversation_type=conversation_type,
                source_channel=conversation_data.get('source_channel', 'website_widget'),
                
                # Legal context
                legal_area=legal_analysis['legal_area'],
                legal_complexity=legal_analysis['complexity'],
                urgency_level=legal_analysis['urgency'],
                
                # Conversation metrics
                total_messages=metrics['total_messages'],
                user_messages=metrics['user_messages'],
                assistant_messages=metrics['assistant_messages'],
                total_words=metrics['total_words'],
                
                # Duration and timing
                duration_seconds=metrics['duration_seconds'],
                response_time_avg_ms=metrics['response_time_avg_ms'],
                first_response_time_ms=metrics['first_response_time_ms'],
                
                # Legal intelligence
                legal_terms_count=legal_analysis['terms_count'],
                legal_citations_mentioned=legal_analysis['citations'],
                legal_concepts_identified=legal_analysis['concepts'],
                
                # Quality metrics
                ai_confidence_avg=metrics['ai_confidence_avg'],
                escalation_triggered=conversation_data.get('escalation_triggered', False),
                escalation_reason=conversation_data.get('escalation_reason'),
                
                # Outcome tracking
                consultation_booked=conversation_data.get('consultation_booked', False),
                follow_up_required=legal_analysis['follow_up_required'],
                
                # Session data
                session_id=conversation_data.get('session_id'),
                user_agent=conversation_data.get('user_agent'),
                ip_address=conversation_data.get('ip_address'),
                
                # Timestamps
                started_at=conversation_data.get('started_at', datetime.utcnow()),
                ended_at=conversation_data.get('ended_at')
            )
            
            self.db.add(analytics)
            self.db.commit()
            self.db.refresh(analytics)
            
            # Update keyword analytics
            await self._update_keyword_analytics(
                legal_analysis['legal_area'],
                legal_analysis['keywords'],
                conversation_data.get('started_at', datetime.utcnow()).date()
            )
            
            logger.info(f"Processed analytics for {conversation_type} conversation {analytics.id}")
            return analytics
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to process conversation analytics: {str(e)}")
            raise

    async def generate_daily_metrics(self, target_date: date = None) -> LawFirmMetrics:
        """Generate daily metrics for law firm performance"""
        try:
            if not target_date:
                target_date = date.today()
            
            # Get all conversations for the day
            conversations = self.db.query(ConversationAnalytics).filter(
                func.date(ConversationAnalytics.started_at) == target_date
            ).all()
            
            # Calculate metrics
            total_conversations = len(conversations)
            chat_conversations = len([c for c in conversations if c.conversation_type == 'chat'])
            voice_conversations = len([c for c in conversations if c.conversation_type == 'voice'])
            
            # Legal area breakdown
            legal_areas = {}
            for conv in conversations:
                area = conv.legal_area or 'other'
                legal_areas[area] = legal_areas.get(area, 0) + 1
            
            # Conversion metrics
            consultations_requested = len([c for c in conversations if c.consultation_booked])
            conversion_rate = (consultations_requested / total_conversations * 100) if total_conversations > 0 else 0
            
            # Quality metrics
            avg_satisfaction = sum(c.user_satisfaction_score or 0 for c in conversations) / len(conversations) if conversations else 0
            escalation_rate = (len([c for c in conversations if c.escalation_triggered]) / total_conversations * 100) if total_conversations > 0 else 0
            
            # Response time metrics
            avg_first_response = sum(c.first_response_time_ms or 0 for c in conversations) / len(conversations) / 60000 if conversations else 0  # Convert to minutes
            
            # Create metrics record
            metrics = LawFirmMetrics(
                metric_date=target_date,
                metric_period="daily",
                
                # Conversation volume
                total_conversations=total_conversations,
                chat_conversations=chat_conversations,
                voice_conversations=voice_conversations,
                
                # Legal area breakdown
                criminal_cases=legal_areas.get('criminal', 0),
                civil_cases=legal_areas.get('civil', 0),
                commercial_cases=legal_areas.get('commercial', 0),
                family_cases=legal_areas.get('family', 0),
                property_cases=legal_areas.get('property', 0),
                employment_cases=legal_areas.get('employment', 0),
                other_cases=legal_areas.get('other', 0),
                
                # Conversion metrics
                consultations_requested=consultations_requested,
                conversion_rate=conversion_rate,
                
                # Quality metrics
                average_satisfaction=avg_satisfaction,
                escalation_rate=escalation_rate,
                
                # Response time
                avg_first_response_time_minutes=avg_first_response
            )
            
            self.db.add(metrics)
            self.db.commit()
            self.db.refresh(metrics)
            
            logger.info(f"Generated daily metrics for {target_date}")
            return metrics
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to generate daily metrics: {str(e)}")
            raise

    # Keyword Analysis

    async def _update_keyword_analytics(
        self,
        legal_area: str,
        keywords: List[str],
        analysis_date: date
    ):
        """Update keyword analytics for the given date"""
        try:
            for keyword in keywords:
                # Find or create keyword analytics record
                existing = self.db.query(LegalKeywordAnalytics).filter(
                    and_(
                        LegalKeywordAnalytics.analysis_date == analysis_date,
                        LegalKeywordAnalytics.legal_area == legal_area,
                        LegalKeywordAnalytics.keyword == keyword
                    )
                ).first()
                
                if existing:
                    existing.mention_count += 1
                    existing.conversation_count += 1
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new record
                    keyword_analytics = LegalKeywordAnalytics(
                        analysis_date=analysis_date,
                        legal_area=legal_area,
                        keyword=keyword,
                        keyword_category=self._get_keyword_category(keyword),
                        mention_count=1,
                        conversation_count=1
                    )
                    self.db.add(keyword_analytics)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update keyword analytics: {str(e)}")

    async def get_trending_keywords(
        self,
        legal_area: Optional[str] = None,
        days: int = 7,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get trending legal keywords for the specified period"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.query(LegalKeywordAnalytics).filter(
                LegalKeywordAnalytics.analysis_date >= start_date
            )
            
            if legal_area:
                query = query.filter(LegalKeywordAnalytics.legal_area == legal_area)
            
            # Group by keyword and sum mentions
            results = query.group_by(LegalKeywordAnalytics.keyword).all()
            
            # Calculate trending scores
            trending_keywords = []
            for result in results:
                # Get historical average (previous period)
                historical_start = start_date - timedelta(days=days)
                historical_end = start_date
                
                historical = self.db.query(LegalKeywordAnalytics).filter(
                    and_(
                        LegalKeywordAnalytics.keyword == result.keyword,
                        LegalKeywordAnalytics.analysis_date >= historical_start,
                        LegalKeywordAnalytics.analysis_date < historical_end
                    )
                ).first()
                
                historical_avg = historical.mention_count if historical else 0
                
                trending_score = self._calculate_trending_score(
                    result.mention_count,
                    result.conversation_count,
                    historical_avg
                )
                
                trending_keywords.append({
                    "keyword": result.keyword,
                    "legal_area": result.legal_area,
                    "mention_count": result.mention_count,
                    "conversation_count": result.conversation_count,
                    "trending_score": trending_score,
                    "category": result.keyword_category,
                    "growth_rate": ((result.mention_count - historical_avg) / historical_avg * 100) if historical_avg > 0 else 100
                })
            
            # Sort by trending score and return top results
            trending_keywords.sort(key=lambda x: x['trending_score'], reverse=True)
            return trending_keywords[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get trending keywords: {str(e)}")
            return []

    # Client Journey Tracking

    async def track_client_journey(
        self,
        client_hash: str,
        interaction_type: str,
        legal_area: str,
        conversation_data: Dict[str, Any]
    ) -> ClientJourney:
        """Track or update client journey"""
        try:
            # Find existing journey or create new one
            journey = self.db.query(ClientJourney).filter(
                ClientJourney.client_hash == client_hash
            ).first()
            
            if not journey:
                journey = ClientJourney(
                    client_hash=client_hash,
                    first_contact_date=datetime.utcnow(),
                    first_contact_channel=interaction_type,
                    legal_area=legal_area,
                    matter_complexity=conversation_data.get('complexity', 'medium'),
                    urgency_level=conversation_data.get('urgency', 'normal')
                )
                self.db.add(journey)
            
            # Update journey based on interaction
            journey.total_interactions += 1
            
            if interaction_type == 'chat':
                journey.chat_interactions += 1
            elif interaction_type == 'voice':
                journey.voice_interactions += 1
            
            # Track consultation booking
            if conversation_data.get('consultation_booked'):
                if not journey.consultation_requested_date:
                    journey.consultation_requested_date = datetime.utcnow()
                    journey.time_to_consultation_hours = (
                        journey.consultation_requested_date - journey.first_contact_date
                    ).total_seconds() / 3600
                
                journey.journey_stage = "consultation_requested"
            
            # Update satisfaction if provided
            if conversation_data.get('satisfaction_score'):
                journey.client_satisfaction_score = conversation_data['satisfaction_score']
            
            journey.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(journey)
            
            return journey
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to track client journey: {str(e)}")
            raise

    # Dashboard Data Aggregation

    async def get_dashboard_summary(
        self,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        try:
            if not start_date:
                start_date = date.today() - timedelta(days=30)
            if not end_date:
                end_date = date.today()
            
            # Get conversation analytics
            conversations = self.db.query(ConversationAnalytics).filter(
                func.date(ConversationAnalytics.started_at).between(start_date, end_date)
            ).all()
            
            # Calculate summary metrics
            total_conversations = len(conversations)
            total_consultations = len([c for c in conversations if c.consultation_booked])
            avg_satisfaction = sum(c.user_satisfaction_score or 0 for c in conversations) / len(conversations) if conversations else 0
            
            # Legal area breakdown
            legal_areas = {}
            for conv in conversations:
                area = conv.legal_area or 'other'
                legal_areas[area] = legal_areas.get(area, 0) + 1
            
            # Conversion funnel
            conversion_funnel = {
                "conversations_started": total_conversations,
                "consultations_requested": total_consultations,
                "conversion_rate": (total_consultations / total_conversations * 100) if total_conversations > 0 else 0
            }
            
            # Recent trends (compare with previous period)
            previous_start = start_date - (end_date - start_date)
            previous_conversations = self.db.query(ConversationAnalytics).filter(
                func.date(ConversationAnalytics.started_at).between(previous_start, start_date)
            ).count()
            
            growth_rate = ((total_conversations - previous_conversations) / previous_conversations * 100) if previous_conversations > 0 else 0
            
            # Get trending keywords
            trending_keywords = await self.get_trending_keywords(days=7, limit=10)
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary_metrics": {
                    "total_conversations": total_conversations,
                    "total_consultations": total_consultations,
                    "conversion_rate": conversion_funnel["conversion_rate"],
                    "average_satisfaction": round(avg_satisfaction, 2),
                    "growth_rate": round(growth_rate, 1)
                },
                "legal_area_breakdown": legal_areas,
                "conversion_funnel": conversion_funnel,
                "trending_keywords": trending_keywords[:5],  # Top 5 for dashboard
                "channel_breakdown": {
                    "chat": len([c for c in conversations if c.conversation_type == 'chat']),
                    "voice": len([c for c in conversations if c.conversation_type == 'voice'])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard summary: {str(e)}")
            return {}

    # Helper Methods

    def _extract_conversation_metrics(
        self,
        conversation_data: Dict[str, Any],
        conversation_type: str
    ) -> Dict[str, Any]:
        """Extract metrics from conversation data"""
        
        if conversation_type == "chat":
            messages = conversation_data.get('messages', [])
            user_messages = len([m for m in messages if m.get('type') == 'user'])
            assistant_messages = len([m for m in messages if m.get('type') == 'assistant'])
            total_words = sum(len(m.get('content', '').split()) for m in messages)
            
            # Calculate response times
            response_times = []
            first_response_time = 0
            
            for i in range(1, len(messages)):
                if messages[i-1].get('type') == 'user' and messages[i].get('type') == 'assistant':
                    prev_time = messages[i-1].get('timestamp', 0)
                    curr_time = messages[i].get('timestamp', 0)
                    response_time = (curr_time - prev_time) * 1000  # Convert to ms
                    response_times.append(response_time)
                    
                    if not first_response_time:
                        first_response_time = response_time
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
        else:  # voice conversation
            transcript = conversation_data.get('transcript', [])
            user_messages = len([t for t in transcript if t.get('speaker') == 'user'])
            assistant_messages = len([t for t in transcript if t.get('speaker') == 'assistant'])
            total_words = sum(len(t.get('text', '').split()) for t in transcript)
            avg_response_time = 2000  # Assume 2s average for voice
            first_response_time = 1500
        
        duration = conversation_data.get('duration_seconds', 0)
        ai_confidence = conversation_data.get('ai_confidence_avg', 0.8)
        
        return {
            "total_messages": user_messages + assistant_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "total_words": total_words,
            "duration_seconds": duration,
            "response_time_avg_ms": avg_response_time,
            "first_response_time_ms": first_response_time,
            "ai_confidence_avg": ai_confidence
        }

    def _analyze_legal_content(
        self,
        messages: List[Dict] = None,
        transcript: List[Dict] = None
    ) -> Dict[str, Any]:
        """Analyze legal content from conversation"""
        
        # Combine text from all sources
        all_text = ""
        if messages:
            all_text += " ".join([m.get('content', '') for m in messages])
        if transcript:
            all_text += " ".join([t.get('text', '') for t in transcript])
        
        all_text = all_text.lower()
        
        # Classify legal area
        legal_area = self._classify_legal_area(all_text)
        
        # Assess complexity
        complexity = self._assess_complexity(all_text)
        
        # Assess urgency
        urgency = self._assess_urgency(all_text)
        
        # Extract keywords
        keywords = self._extract_legal_keywords(all_text)
        
        # Extract citations
        citations = self._extract_citations(all_text)
        
        # Extract legal concepts
        concepts = self._extract_legal_concepts(all_text)
        
        # Check if follow-up required
        follow_up_required = self._requires_follow_up(all_text)
        
        return {
            "legal_area": legal_area,
            "complexity": complexity,
            "urgency": urgency,
            "keywords": keywords,
            "citations": citations,
            "concepts": concepts,
            "terms_count": len(keywords),
            "follow_up_required": follow_up_required
        }

    def _classify_legal_area(self, text: str) -> str:
        """Classify legal area from text"""
        area_keywords = {
            "criminal": ["police", "arrest", "charge", "crime", "theft", "assault", "criminal", "bail"],
            "family": ["divorce", "custody", "child", "marriage", "maintenance", "family", "spouse"],
            "commercial": ["business", "contract", "company", "partnership", "trade", "commercial"],
            "property": ["property", "transfer", "deed", "bond", "mortgage", "real estate"],
            "civil": ["damages", "dispute", "claim", "liability", "negligence", "civil"],
            "employment": ["workplace", "dismissal", "employment", "salary", "unfair", "labor"]
        }
        
        scores = {}
        for area, keywords in area_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[area] = score
        
        return max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else "general"

    def _assess_complexity(self, text: str) -> str:
        """Assess legal matter complexity"""
        complex_indicators = [
            "constitutional", "supreme court", "appeal", "precedent",
            "multiple parties", "class action", "international"
        ]
        
        medium_indicators = [
            "contract", "agreement", "dispute", "negotiation", "mediation"
        ]
        
        complex_count = sum(1 for indicator in complex_indicators if indicator in text)
        medium_count = sum(1 for indicator in medium_indicators if indicator in text)
        
        if complex_count > 0:
            return "high"
        elif medium_count > 0:
            return "medium"
        else:
            return "low"

    def _assess_urgency(self, text: str) -> str:
        """Assess urgency level"""
        critical_keywords = ["emergency", "arrest", "court tomorrow", "today", "deadline today"]
        high_keywords = ["urgent", "deadline", "court date", "police", "soon"]
        
        if any(keyword in text for keyword in critical_keywords):
            return "critical"
        elif any(keyword in text for keyword in high_keywords):
            return "high"
        else:
            return "normal"

    def _extract_legal_keywords(self, text: str) -> List[str]:
        """Extract legal keywords from text"""
        found_keywords = []
        
        for category, keywords in self.legal_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    found_keywords.append(keyword)
        
        return found_keywords

    def _extract_citations(self, text: str) -> List[str]:
        """Extract legal citations from text"""
        import re
        
        # SA legal citation patterns
        citation_patterns = [
            r'\b\d{4}\s+ZACC\s+\d+\b',  # Constitutional Court
            r'\b\d{4}\s+ZASCA\s+\d+\b',  # Supreme Court of Appeal
            r'\b\d{4}\s+ZAWCHC\s+\d+\b',  # Western Cape High Court
            r'\b\d{4}\s+SA\s+\d+\b',  # SA Law Reports
        ]
        
        citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
        
        return citations

    def _extract_legal_concepts(self, text: str) -> List[str]:
        """Extract legal concepts from text"""
        concepts = []
        
        for keyword in self.legal_keywords['concepts']:
            if keyword in text:
                concepts.append(keyword)
        
        return concepts

    def _requires_follow_up(self, text: str) -> bool:
        """Determine if follow-up is required"""
        follow_up_indicators = [
            "follow up", "call back", "more information", "documents",
            "review", "next steps", "additional", "further", "complex"
        ]
        
        return any(indicator in text for indicator in follow_up_indicators)

    def _get_keyword_category(self, keyword: str) -> str:
        """Get category for a keyword"""
        for category, keywords in self.legal_keywords.items():
            if keyword in keywords:
                return category
        return "general"

    def _calculate_trending_score(
        self,
        current_count: int,
        total_conversations: int,
        historical_avg: float
    ) -> float:
        """Calculate trending score for keywords"""
        if total_conversations == 0:
            return 0.0
        
        current_rate = current_count / total_conversations
        growth_rate = (current_rate - historical_avg) / historical_avg if historical_avg > 0 else 1.0
        
        # Normalize to 0-1 scale with emphasis on growth
        trending_score = min(1.0, max(0.0, (growth_rate + 1) / 2))
        return trending_score
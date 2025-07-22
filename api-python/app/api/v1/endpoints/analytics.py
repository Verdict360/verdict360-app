"""
Analytics API endpoints for legal chatbot dashboard
Provides conversation metrics, keyword analytics, and performance data
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import logging

from app.dependencies import get_db
from app.services.analytics_service import AnalyticsService
from app.models.analytics import ConversationAnalytics, LegalKeywordAnalytics, LawFirmMetrics
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Pydantic models for API responses

class DashboardSummaryResponse(BaseModel):
    period: Dict[str, str]
    summary_metrics: Dict[str, float]
    legal_area_breakdown: Dict[str, int]
    conversion_funnel: Dict[str, float]
    trending_keywords: List[Dict[str, Any]]
    channel_breakdown: Dict[str, int]

class ConversationAnalyticsResponse(BaseModel):
    id: str
    conversation_type: str
    legal_area: Optional[str]
    duration_seconds: int
    total_messages: int
    consultation_booked: bool
    started_at: datetime

class KeywordTrendResponse(BaseModel):
    keyword: str
    legal_area: str
    mention_count: int
    trending_score: float
    growth_rate: float

class PerformanceMetricsResponse(BaseModel):
    total_conversations: int
    conversion_rate: float
    average_satisfaction: float
    response_time_avg_minutes: float

# Analytics Endpoints

@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    start_date: Optional[date] = Query(None, description="Start date for analytics period"),
    end_date: Optional[date] = Query(None, description="End date for analytics period"),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard summary with key metrics"""
    try:
        analytics_service = AnalyticsService(db)
        
        # Set default date range if not provided
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        summary = await analytics_service.get_dashboard_summary(start_date, end_date)
        
        if not summary:
            raise HTTPException(status_code=404, detail="No analytics data available for the specified period")
        
        return DashboardSummaryResponse(**summary)
        
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard summary")

@router.get("/conversations/analytics", response_model=List[ConversationAnalyticsResponse])
async def get_conversation_analytics(
    limit: int = Query(50, description="Number of conversations to return"),
    conversation_type: Optional[str] = Query(None, description="Filter by conversation type (chat, voice)"),
    legal_area: Optional[str] = Query(None, description="Filter by legal area"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: Session = Depends(get_db)
):
    """Get conversation analytics data"""
    try:
        query = db.query(ConversationAnalytics)
        
        # Apply filters
        if conversation_type:
            query = query.filter(ConversationAnalytics.conversation_type == conversation_type)
        if legal_area:
            query = query.filter(ConversationAnalytics.legal_area == legal_area)
        if start_date:
            query = query.filter(ConversationAnalytics.started_at >= start_date)
        if end_date:
            query = query.filter(ConversationAnalytics.started_at <= end_date)
        
        conversations = query.order_by(ConversationAnalytics.started_at.desc()).limit(limit).all()
        
        return [
            ConversationAnalyticsResponse(
                id=conv.id,
                conversation_type=conv.conversation_type,
                legal_area=conv.legal_area,
                duration_seconds=conv.duration_seconds,
                total_messages=conv.total_messages,
                consultation_booked=conv.consultation_booked,
                started_at=conv.started_at
            )
            for conv in conversations
        ]
        
    except Exception as e:
        logger.error(f"Failed to get conversation analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation analytics")

@router.get("/keywords/trending", response_model=List[KeywordTrendResponse])
async def get_trending_keywords(
    legal_area: Optional[str] = Query(None, description="Filter by legal area"),
    days: int = Query(7, description="Number of days to analyze"),
    limit: int = Query(20, description="Number of keywords to return"),
    db: Session = Depends(get_db)
):
    """Get trending legal keywords"""
    try:
        analytics_service = AnalyticsService(db)
        trending = await analytics_service.get_trending_keywords(legal_area, days, limit)
        
        return [
            KeywordTrendResponse(
                keyword=kw["keyword"],
                legal_area=kw["legal_area"],
                mention_count=kw["mention_count"],
                trending_score=kw["trending_score"],
                growth_rate=kw["growth_rate"]
            )
            for kw in trending
        ]
        
    except Exception as e:
        logger.error(f"Failed to get trending keywords: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trending keywords")

@router.get("/performance/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    start_date: Optional[date] = Query(None, description="Start date for metrics"),
    end_date: Optional[date] = Query(None, description="End date for metrics"),
    db: Session = Depends(get_db)
):
    """Get performance metrics for the specified period"""
    try:
        # Set default date range
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=7)
        
        # Query conversation analytics
        conversations = db.query(ConversationAnalytics).filter(
            ConversationAnalytics.started_at >= start_date,
            ConversationAnalytics.started_at <= end_date
        ).all()
        
        if not conversations:
            return PerformanceMetricsResponse(
                total_conversations=0,
                conversion_rate=0.0,
                average_satisfaction=0.0,
                response_time_avg_minutes=0.0
            )
        
        # Calculate metrics
        total_conversations = len(conversations)
        consultations_booked = sum(1 for c in conversations if c.consultation_booked)
        conversion_rate = (consultations_booked / total_conversations * 100) if total_conversations > 0 else 0
        
        satisfactions = [c.user_satisfaction_score for c in conversations if c.user_satisfaction_score is not None]
        average_satisfaction = sum(satisfactions) / len(satisfactions) if satisfactions else 0
        
        response_times = [c.response_time_avg_ms for c in conversations if c.response_time_avg_ms > 0]
        response_time_avg_minutes = (sum(response_times) / len(response_times) / 1000 / 60) if response_times else 0
        
        return PerformanceMetricsResponse(
            total_conversations=total_conversations,
            conversion_rate=round(conversion_rate, 2),
            average_satisfaction=round(average_satisfaction, 2),
            response_time_avg_minutes=round(response_time_avg_minutes, 2)
        )
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")

@router.get("/legal-areas/breakdown")
async def get_legal_area_breakdown(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """Get breakdown of legal areas from conversations"""
    try:
        # Set default date range
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        conversations = db.query(ConversationAnalytics).filter(
            ConversationAnalytics.started_at >= start_date,
            ConversationAnalytics.started_at <= end_date
        ).all()
        
        # Count by legal area
        legal_areas = {}
        for conv in conversations:
            area = conv.legal_area or 'other'
            legal_areas[area] = legal_areas.get(area, 0) + 1
        
        # Sort by count
        sorted_areas = sorted(legal_areas.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_conversations": len(conversations),
            "legal_areas": dict(sorted_areas),
            "top_areas": sorted_areas[:5]
        }
        
    except Exception as e:
        logger.error(f"Failed to get legal area breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve legal area breakdown")

@router.get("/conversion/funnel")
async def get_conversion_funnel(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """Get conversion funnel metrics"""
    try:
        # Set default date range
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        conversations = db.query(ConversationAnalytics).filter(
            ConversationAnalytics.started_at >= start_date,
            ConversationAnalytics.started_at <= end_date
        ).all()
        
        # Calculate funnel metrics
        total_conversations = len(conversations)
        consultations_requested = sum(1 for c in conversations if c.consultation_booked)
        consultations_completed = sum(1 for c in conversations if c.consultation_completed)
        
        funnel_data = {
            "conversations_started": total_conversations,
            "consultations_requested": consultations_requested,
            "consultations_completed": consultations_completed,
            "request_conversion_rate": (consultations_requested / total_conversations * 100) if total_conversations > 0 else 0,
            "completion_rate": (consultations_completed / consultations_requested * 100) if consultations_requested > 0 else 0,
            "overall_conversion_rate": (consultations_completed / total_conversations * 100) if total_conversations > 0 else 0
        }
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "funnel": funnel_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get conversion funnel: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversion funnel")

# Data Processing Endpoints

@router.post("/process/conversation")
async def process_conversation_analytics(
    conversation_data: Dict[str, Any],
    conversation_type: str = Query("chat", description="Type of conversation (chat, voice)"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Process and store conversation analytics"""
    try:
        analytics_service = AnalyticsService(db)
        
        # Process analytics in background
        background_tasks.add_task(
            analytics_service.process_conversation_analytics,
            conversation_data,
            conversation_type
        )
        
        return {"status": "processing", "message": "Conversation analytics processing initiated"}
        
    except Exception as e:
        logger.error(f"Failed to process conversation analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process conversation analytics")

@router.post("/generate/daily-metrics")
async def generate_daily_metrics(
    target_date: Optional[date] = Query(None, description="Date to generate metrics for"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Generate daily metrics for a specific date"""
    try:
        analytics_service = AnalyticsService(db)
        
        if not target_date:
            target_date = date.today()
        
        # Generate metrics in background
        background_tasks.add_task(
            analytics_service.generate_daily_metrics,
            target_date
        )
        
        return {
            "status": "processing",
            "target_date": target_date.isoformat(),
            "message": f"Daily metrics generation initiated for {target_date}"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate daily metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate daily metrics")

@router.get("/health")
async def analytics_health_check(db: Session = Depends(get_db)):
    """Health check for analytics service"""
    try:
        # Test database connection
        conversation_count = db.query(ConversationAnalytics).count()
        
        return {
            "status": "healthy",
            "service": "analytics",
            "database_connected": True,
            "total_conversations_tracked": conversation_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analytics health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "analytics",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
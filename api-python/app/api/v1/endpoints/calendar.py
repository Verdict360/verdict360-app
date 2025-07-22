"""
Calendar API endpoints for consultation booking and availability management
Provides real-time availability checking and conflict detection
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import logging

from app.dependencies import get_db
from app.services.calendar_service import CalendarService, AvailabilityRequest, TimeSlot, CalendarEvent
from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for API requests and responses

class AvailabilityCheckRequest(BaseModel):
    legal_area: str
    preferred_date: date
    preferred_time: Optional[str] = None
    duration_minutes: int = 60
    urgency_level: str = "normal"
    
    @validator('legal_area')
    def validate_legal_area(cls, v):
        valid_areas = ['criminal', 'family', 'commercial', 'civil', 'property', 'employment', 'general']
        if v not in valid_areas:
            raise ValueError(f'Legal area must be one of: {valid_areas}')
        return v
    
    @validator('urgency_level')
    def validate_urgency(cls, v):
        valid_urgency = ['normal', 'high', 'critical']
        if v not in valid_urgency:
            raise ValueError(f'Urgency level must be one of: {valid_urgency}')
        return v

class ConsultationBookingRequest(BaseModel):
    client_name: str
    client_email: str
    client_phone: Optional[str] = None
    legal_area: str
    matter_description: str
    preferred_date: date
    preferred_time: str
    duration_minutes: int = 60
    urgency_level: str = "normal"
    consultation_id: Optional[str] = None

class TimeSlotResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    available: bool
    lawyer_id: Optional[str] = None
    lawyer_name: Optional[str] = None
    conflict_reason: Optional[str] = None

class BookingResponse(BaseModel):
    success: bool
    consultation_id: Optional[str] = None
    calendar_event_id: Optional[str] = None
    scheduled_time: Optional[str] = None
    confirmation_sent: bool = False
    error: Optional[str] = None
    conflicts: Optional[List[Dict]] = None
    alternative_slots: Optional[List[TimeSlotResponse]] = None
    next_steps: Optional[List[str]] = None

class CalendarEventResponse(BaseModel):
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    status: str
    description: Optional[str] = None

class DailyScheduleResponse(BaseModel):
    date: date
    events: List[CalendarEventResponse]
    total_events: int
    available_slots: int

# Calendar endpoints

@router.post("/availability/check", response_model=List[TimeSlotResponse])
async def check_availability(
    request: AvailabilityCheckRequest,
    db: Session = Depends(get_db)
):
    """Check real-time availability for consultation booking"""
    try:
        calendar_service = CalendarService(db)
        
        # Create availability request
        availability_request = AvailabilityRequest(
            legal_area=request.legal_area,
            preferred_date=request.preferred_date,
            preferred_time=request.preferred_time,
            duration_minutes=request.duration_minutes,
            urgency_level=request.urgency_level
        )
        
        # Get available slots
        available_slots = await calendar_service.check_availability(availability_request)
        
        if not available_slots:
            # If no slots available on preferred date, suggest next few days
            alternative_dates = []
            for days_ahead in range(1, 8):  # Check next 7 days
                alt_date = request.preferred_date + timedelta(days=days_ahead)
                alt_request = AvailabilityRequest(
                    legal_area=request.legal_area,
                    preferred_date=alt_date,
                    preferred_time=request.preferred_time,
                    duration_minutes=request.duration_minutes,
                    urgency_level=request.urgency_level
                )
                alt_slots = await calendar_service.check_availability(alt_request)
                if alt_slots:
                    alternative_dates.extend(alt_slots[:3])  # Take first 3 slots from each day
                    if len(alternative_dates) >= 10:  # Maximum 10 alternative slots
                        break
            
            if alternative_dates:
                available_slots = alternative_dates
            else:
                raise HTTPException(status_code=404, detail="No available slots found in the next 7 days")
        
        # Convert to response format
        slot_responses = []
        for slot in available_slots:
            slot_responses.append(TimeSlotResponse(
                start_time=slot.start_time,
                end_time=slot.end_time,
                available=slot.available,
                lawyer_id=slot.lawyer_id,
                lawyer_name=slot.lawyer_name,
                conflict_reason=slot.conflict_reason
            ))
        
        return slot_responses
        
    except Exception as e:
        logger.error(f"Failed to check availability: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check availability")

@router.post("/consultations/book", response_model=BookingResponse)
async def book_consultation(
    request: ConsultationBookingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Book a consultation with conflict detection"""
    try:
        calendar_service = CalendarService(db)
        
        # Prepare consultation data
        consultation_data = {
            'client_name': request.client_name,
            'client_email': request.client_email,
            'client_phone': request.client_phone,
            'legal_area': request.legal_area,
            'matter_description': request.matter_description,
            'preferred_date': request.preferred_date.isoformat(),
            'preferred_time': request.preferred_time,
            'duration_minutes': request.duration_minutes,
            'urgency_level': request.urgency_level,
            'consultation_id': request.consultation_id or f"cons_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Attempt to book consultation
        booking_result = await calendar_service.book_consultation(consultation_data)
        
        if booking_result['success']:
            # Schedule follow-up tasks in background
            background_tasks.add_task(
                _schedule_follow_up_tasks,
                booking_result['consultation_id'],
                request.legal_area,
                request.urgency_level
            )
            
            return BookingResponse(
                success=True,
                consultation_id=booking_result['consultation_id'],
                calendar_event_id=booking_result.get('calendar_event_id'),
                scheduled_time=booking_result['scheduled_time'],
                confirmation_sent=booking_result['confirmation_sent'],
                next_steps=booking_result.get('next_steps', [])
            )
        else:
            # Handle booking failure with alternatives
            alternative_slots = booking_result.get('alternative_slots', [])
            alt_responses = [
                TimeSlotResponse(
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    available=slot.available,
                    lawyer_id=slot.lawyer_id,
                    lawyer_name=slot.lawyer_name
                )
                for slot in alternative_slots
            ]
            
            return BookingResponse(
                success=False,
                error=booking_result.get('error'),
                conflicts=booking_result.get('conflicts', []),
                alternative_slots=alt_responses
            )
        
    except Exception as e:
        logger.error(f"Failed to book consultation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to book consultation")

@router.get("/schedule/daily", response_model=DailyScheduleResponse)
async def get_daily_schedule(
    target_date: date = Query(default_factory=date.today, description="Date to get schedule for"),
    lawyer_id: Optional[str] = Query(None, description="Specific lawyer ID to filter by"),
    db: Session = Depends(get_db)
):
    """Get daily schedule for lawyers"""
    try:
        calendar_service = CalendarService(db)
        
        # Get daily events
        events = await calendar_service.get_daily_schedule(target_date, lawyer_id)
        
        # Convert to response format
        event_responses = []
        for event in events:
            event_responses.append(CalendarEventResponse(
                id=event.id,
                title=event.title,
                start_time=event.start_time,
                end_time=event.end_time,
                attendees=event.attendees,
                status=event.status,
                description=event.description
            ))
        
        # Calculate available slots (mock calculation)
        business_hours = 9  # 9 hours per day (8 AM - 5 PM)
        booked_hours = sum((event.end_time - event.start_time).total_seconds() / 3600 for event in events)
        available_hours = max(0, business_hours - booked_hours)
        available_slots = int(available_hours)  # Rough estimate
        
        return DailyScheduleResponse(
            date=target_date,
            events=event_responses,
            total_events=len(events),
            available_slots=available_slots
        )
        
    except Exception as e:
        logger.error(f"Failed to get daily schedule: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve daily schedule")

@router.delete("/consultations/{consultation_id}")
async def cancel_consultation(
    consultation_id: str,
    reason: str = Query(default="Client requested cancellation", description="Reason for cancellation"),
    db: Session = Depends(get_db)
):
    """Cancel a consultation and remove from calendar"""
    try:
        calendar_service = CalendarService(db)
        
        cancellation_result = await calendar_service.cancel_consultation(consultation_id, reason)
        
        if cancellation_result['success']:
            return {
                "success": True,
                "message": "Consultation cancelled successfully",
                "consultation_id": consultation_id,
                "cancelled_at": cancellation_result['cancelled_at'],
                "client_notified": cancellation_result.get('client_notified', False)
            }
        else:
            raise HTTPException(status_code=400, detail=cancellation_result.get('error', 'Failed to cancel consultation'))
        
    except Exception as e:
        logger.error(f"Failed to cancel consultation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel consultation")

@router.get("/availability/lawyers")
async def get_available_lawyers(
    legal_area: str = Query(..., description="Legal area to filter lawyers by"),
    target_date: date = Query(default_factory=date.today, description="Date to check availability for"),
    db: Session = Depends(get_db)
):
    """Get available lawyers for a specific legal area and date"""
    try:
        calendar_service = CalendarService(db)
        
        # Get lawyers by specialization
        suitable_lawyers = calendar_service._get_lawyers_by_specialization(legal_area)
        
        lawyer_availability = []
        for lawyer_id, lawyer_info in suitable_lawyers.items():
            # Check availability for this lawyer
            availability_request = AvailabilityRequest(
                legal_area=legal_area,
                preferred_date=target_date,
                duration_minutes=60
            )
            
            lawyer_slots = await calendar_service._get_lawyer_availability(
                lawyer_id, target_date, 60, None
            )
            
            available_count = len([slot for slot in lawyer_slots if slot.available])
            
            lawyer_availability.append({
                "lawyer_id": lawyer_id,
                "name": lawyer_info['name'],
                "specializations": lawyer_info['specializations'],
                "available_slots": available_count,
                "availability_pattern": lawyer_info.get('availability_pattern', 'standard')
            })
        
        return {
            "date": target_date.isoformat(),
            "legal_area": legal_area,
            "available_lawyers": lawyer_availability,
            "total_lawyers": len(lawyer_availability)
        }
        
    except Exception as e:
        logger.error(f"Failed to get available lawyers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get available lawyers")

@router.get("/stats/booking")
async def get_booking_statistics(
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30), description="Start date for statistics"),
    end_date: date = Query(default_factory=date.today, description="End date for statistics"),
    db: Session = Depends(get_db)
):
    """Get booking statistics for the specified period"""
    try:
        # Mock statistics (in production, would query database)
        total_days = (end_date - start_date).days + 1
        
        mock_stats = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_days": total_days
            },
            "bookings": {
                "total_consultations": 45,
                "completed_consultations": 38,
                "cancelled_consultations": 7,
                "no_show_rate": 8.9,  # percentage
                "average_booking_lead_time_hours": 36.5
            },
            "availability": {
                "average_utilization_rate": 67.8,  # percentage
                "peak_booking_hours": ["09:00-10:00", "14:00-15:00", "16:00-17:00"],
                "most_requested_legal_areas": [
                    {"area": "family", "count": 12},
                    {"area": "criminal", "count": 10},
                    {"area": "commercial", "count": 8},
                    {"area": "civil", "count": 7}
                ]
            },
            "conflicts": {
                "total_conflicts_detected": 3,
                "conflicts_resolved": 3,
                "conflict_resolution_rate": 100.0
            },
            "client_satisfaction": {
                "average_booking_experience_rating": 4.6,
                "booking_completion_rate": 94.2
            }
        }
        
        return mock_stats
        
    except Exception as e:
        logger.error(f"Failed to get booking statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve booking statistics")

@router.get("/health")
async def calendar_health_check(db: Session = Depends(get_db)):
    """Health check for calendar service"""
    try:
        calendar_service = CalendarService(db)
        
        # Test basic calendar functionality
        test_date = date.today()
        test_request = AvailabilityRequest(
            legal_area="general",
            preferred_date=test_date,
            duration_minutes=30
        )
        
        # Quick availability check
        test_slots = await calendar_service.check_availability(test_request)
        
        return {
            "status": "healthy",
            "service": "calendar",
            "features": {
                "availability_checking": True,
                "conflict_detection": True,
                "consultation_booking": True,
                "calendar_integration": True,
                "n8n_workflows": True
            },
            "test_results": {
                "availability_check": len(test_slots) > 0,
                "slots_found": len(test_slots)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Calendar health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "calendar",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Background task functions

async def _schedule_follow_up_tasks(
    consultation_id: str,
    legal_area: str,
    urgency_level: str
):
    """Schedule follow-up tasks after successful booking"""
    try:
        logger.info(f"Scheduling follow-up tasks for consultation {consultation_id}")
        
        # Mock follow-up task scheduling
        tasks = [
            "Send preparation materials to client",
            "Brief assigned lawyer on case details",
            "Set up case file in practice management system"
        ]
        
        if urgency_level == "critical":
            tasks.append("Priority notification to managing partner")
        
        # In production, would integrate with task management system
        logger.info(f"Follow-up tasks scheduled: {tasks}")
        
    except Exception as e:
        logger.error(f"Failed to schedule follow-up tasks: {str(e)}")
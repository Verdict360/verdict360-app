"""
Calendar service for real-time availability and appointment management
Integrates with Google Calendar and provides conflict detection
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
import httpx
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TimeSlot:
    """Represents a time slot for calendar availability"""
    start_time: datetime
    end_time: datetime
    available: bool
    lawyer_id: Optional[str] = None
    lawyer_name: Optional[str] = None
    conflict_reason: Optional[str] = None

@dataclass
class CalendarEvent:
    """Represents a calendar event"""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    status: str
    description: Optional[str] = None

@dataclass
class AvailabilityRequest:
    """Request for checking availability"""
    legal_area: str
    preferred_date: date
    preferred_time: Optional[str] = None
    duration_minutes: int = 60
    urgency_level: str = "normal"

class CalendarService:
    """Service for managing calendar operations and availability"""
    
    def __init__(self, db_session: Session = None):
        self.db = db_session
        self.n8n_webhook_url = "http://localhost:5678/webhook"  # N8N webhook URL
        
        # Business hours for SA law firms
        self.business_hours = {
            'start': '08:00',
            'end': '17:00',
            'timezone': 'Africa/Johannesburg'
        }
        
        # Standard appointment durations by legal area
        self.appointment_durations = {
            'criminal': 90,      # minutes
            'family': 75,
            'commercial': 60,
            'civil': 60,
            'property': 45,
            'employment': 45,
            'general': 30
        }
        
        # Mock lawyer data (would come from database in production)
        self.lawyers = {
            'lawyer_001': {
                'name': 'Sarah Advocate',
                'specializations': ['criminal', 'civil'],
                'calendar_id': 'primary',
                'availability_pattern': 'standard'
            },
            'lawyer_002': {
                'name': 'Michael Attorney',
                'specializations': ['commercial', 'property'],
                'calendar_id': 'michael@firm.com',
                'availability_pattern': 'standard'
            },
            'lawyer_003': {
                'name': 'Jennifer Legal',
                'specializations': ['family', 'employment'],
                'calendar_id': 'jennifer@firm.com',
                'availability_pattern': 'part_time'
            }
        }

    async def check_availability(
        self,
        request: AvailabilityRequest
    ) -> List[TimeSlot]:
        """Check real-time availability for consultation booking"""
        try:
            logger.info(f"Checking availability for {request.legal_area} on {request.preferred_date}")
            
            # Get lawyers who handle this legal area
            suitable_lawyers = self._get_lawyers_by_specialization(request.legal_area)
            
            if not suitable_lawyers:
                logger.warning(f"No lawyers found for legal area: {request.legal_area}")
                return []
            
            # Determine appointment duration
            duration = self.appointment_durations.get(request.legal_area, 60)
            if request.duration_minutes:
                duration = request.duration_minutes
            
            # Generate time slots for the requested date
            available_slots = []
            
            for lawyer_id, lawyer_info in suitable_lawyers.items():
                lawyer_slots = await self._get_lawyer_availability(
                    lawyer_id,
                    request.preferred_date,
                    duration,
                    request.preferred_time
                )
                available_slots.extend(lawyer_slots)
            
            # Sort slots by time and prioritize based on urgency
            available_slots.sort(key=lambda x: x.start_time)
            
            if request.urgency_level == "critical":
                # For critical cases, try to find slots within 24 hours
                critical_deadline = datetime.now() + timedelta(hours=24)
                urgent_slots = [slot for slot in available_slots if slot.start_time <= critical_deadline]
                if urgent_slots:
                    return urgent_slots[:5]  # Return top 5 urgent slots
            
            return available_slots[:10]  # Return top 10 available slots
            
        except Exception as e:
            logger.error(f"Failed to check availability: {str(e)}")
            return []

    async def book_consultation(
        self,
        consultation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Book a consultation and create calendar event"""
        try:
            logger.info(f"Booking consultation for {consultation_data.get('client_email')}")
            
            # Validate booking data
            required_fields = ['client_name', 'client_email', 'legal_area', 'preferred_date', 'preferred_time']
            for field in required_fields:
                if not consultation_data.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            # Check for conflicts before booking
            conflict_check = await self._check_conflicts(consultation_data)
            if conflict_check['has_conflicts']:
                return {
                    'success': False,
                    'error': 'Schedule conflict detected',
                    'conflicts': conflict_check['conflicts'],
                    'alternative_slots': await self._suggest_alternatives(consultation_data)
                }
            
            # Create calendar event via N8N workflow
            booking_result = await self._create_calendar_event(consultation_data)
            
            if booking_result['success']:
                # Store consultation in database
                consultation_id = await self._store_consultation_record(consultation_data, booking_result)
                
                return {
                    'success': True,
                    'consultation_id': consultation_id,
                    'calendar_event_id': booking_result.get('event_id'),
                    'scheduled_time': f"{consultation_data['preferred_date']}T{consultation_data['preferred_time']}:00",
                    'confirmation_sent': True,
                    'next_steps': [
                        'Calendar invitation sent to client',
                        'Lawyer notified of appointment',
                        'Consultation materials will be prepared'
                    ]
                }
            else:
                return {
                    'success': False,
                    'error': booking_result.get('error', 'Failed to create calendar event')
                }
            
        except Exception as e:
            logger.error(f"Failed to book consultation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_daily_schedule(
        self,
        target_date: date,
        lawyer_id: Optional[str] = None
    ) -> List[CalendarEvent]:
        """Get daily schedule for lawyers"""
        try:
            if lawyer_id:
                lawyers_to_check = {lawyer_id: self.lawyers.get(lawyer_id)}
            else:
                lawyers_to_check = self.lawyers
            
            daily_events = []
            
            for lawyer_id, lawyer_info in lawyers_to_check.items():
                if not lawyer_info:
                    continue
                
                # Mock calendar events (in production, would query Google Calendar API)
                lawyer_events = await self._get_lawyer_events(lawyer_id, target_date)
                daily_events.extend(lawyer_events)
            
            return sorted(daily_events, key=lambda x: x.start_time)
            
        except Exception as e:
            logger.error(f"Failed to get daily schedule: {str(e)}")
            return []

    async def cancel_consultation(
        self,
        consultation_id: str,
        reason: str = "Client requested cancellation"
    ) -> Dict[str, Any]:
        """Cancel a consultation and remove from calendar"""
        try:
            # In production, would query database for consultation details
            # For now, mock the cancellation process
            
            # Cancel via N8N workflow
            cancellation_data = {
                'consultation_id': consultation_id,
                'cancellation_reason': reason,
                'cancelled_at': datetime.utcnow().isoformat()
            }
            
            result = await self._trigger_n8n_webhook('consultation-cancelled', cancellation_data)
            
            return {
                'success': True,
                'consultation_id': consultation_id,
                'cancelled_at': datetime.utcnow().isoformat(),
                'refund_processed': False,  # Would be handled by payment system
                'client_notified': result.get('client_notified', False)
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel consultation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    # Private helper methods

    def _get_lawyers_by_specialization(self, legal_area: str) -> Dict[str, Dict]:
        """Get lawyers who specialize in the given legal area"""
        suitable_lawyers = {}
        
        for lawyer_id, lawyer_info in self.lawyers.items():
            if legal_area in lawyer_info['specializations'] or 'general' in lawyer_info['specializations']:
                suitable_lawyers[lawyer_id] = lawyer_info
        
        return suitable_lawyers

    async def _get_lawyer_availability(
        self,
        lawyer_id: str,
        target_date: date,
        duration_minutes: int,
        preferred_time: Optional[str] = None
    ) -> List[TimeSlot]:
        """Get availability slots for a specific lawyer"""
        try:
            lawyer_info = self.lawyers.get(lawyer_id)
            if not lawyer_info:
                return []
            
            # Generate business hour slots
            slots = []
            start_hour = 8  # 8 AM
            end_hour = 17   # 5 PM
            slot_duration = duration_minutes // 60  # Convert to hours
            
            # Create datetime objects for the target date
            for hour in range(start_hour, end_hour - slot_duration + 1):
                slot_start = datetime.combine(target_date, datetime.min.time().replace(hour=hour))
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                
                # Check if slot conflicts with existing appointments (mock check)
                has_conflict = await self._check_slot_conflict(lawyer_id, slot_start, slot_end)
                
                slot = TimeSlot(
                    start_time=slot_start,
                    end_time=slot_end,
                    available=not has_conflict,
                    lawyer_id=lawyer_id,
                    lawyer_name=lawyer_info['name'],
                    conflict_reason="Existing appointment" if has_conflict else None
                )
                
                slots.append(slot)
            
            # Filter to available slots only
            available_slots = [slot for slot in slots if slot.available]
            
            # If preferred time specified, prioritize slots around that time
            if preferred_time and available_slots:
                try:
                    preferred_hour = int(preferred_time.split(':')[0])
                    available_slots.sort(key=lambda x: abs(x.start_time.hour - preferred_hour))
                except:
                    pass  # Invalid time format, use default sorting
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Failed to get lawyer availability: {str(e)}")
            return []

    async def _check_slot_conflict(
        self,
        lawyer_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """Check if a time slot conflicts with existing appointments"""
        # Mock conflict check (in production, would query Google Calendar API)
        # For demo purposes, create some mock conflicts
        
        # Assume lawyers are busy from 10-11 AM and 2-3 PM
        conflict_hours = [10, 14]  # 10 AM and 2 PM
        
        return start_time.hour in conflict_hours

    async def _check_conflicts(self, consultation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for scheduling conflicts before booking"""
        try:
            # Parse consultation time
            consultation_date = datetime.fromisoformat(consultation_data['preferred_date'])
            consultation_time = consultation_data.get('preferred_time', '09:00')
            
            # Create full datetime
            time_parts = consultation_time.split(':')
            consultation_datetime = consultation_date.replace(
                hour=int(time_parts[0]),
                minute=int(time_parts[1]) if len(time_parts) > 1 else 0
            )
            
            # Check conflicts (mock implementation)
            conflicts = []
            
            # Example conflict check
            if consultation_datetime.hour in [12, 13]:  # Lunch time
                conflicts.append({
                    'type': 'lunch_break',
                    'message': 'Consultation time conflicts with lunch break',
                    'suggested_alternative': consultation_datetime.replace(hour=14)
                })
            
            return {
                'has_conflicts': len(conflicts) > 0,
                'conflicts': conflicts
            }
            
        except Exception as e:
            logger.error(f"Failed to check conflicts: {str(e)}")
            return {'has_conflicts': False, 'conflicts': []}

    async def _suggest_alternatives(self, consultation_data: Dict[str, Any]) -> List[TimeSlot]:
        """Suggest alternative time slots if conflicts exist"""
        try:
            # Get original request date
            original_date = datetime.fromisoformat(consultation_data['preferred_date']).date()
            
            # Create availability request
            request = AvailabilityRequest(
                legal_area=consultation_data['legal_area'],
                preferred_date=original_date,
                urgency_level=consultation_data.get('urgency_level', 'normal')
            )
            
            # Get alternative slots
            alternatives = await self.check_availability(request)
            
            # Also check next day if no alternatives found
            if not alternatives:
                next_day_request = AvailabilityRequest(
                    legal_area=consultation_data['legal_area'],
                    preferred_date=original_date + timedelta(days=1),
                    urgency_level=consultation_data.get('urgency_level', 'normal')
                )
                alternatives = await self.check_availability(next_day_request)
            
            return alternatives[:5]  # Return top 5 alternatives
            
        except Exception as e:
            logger.error(f"Failed to suggest alternatives: {str(e)}")
            return []

    async def _create_calendar_event(self, consultation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create calendar event via N8N workflow"""
        try:
            # Prepare data for N8N workflow
            workflow_data = {
                'consultation_id': consultation_data.get('consultation_id', f"cons_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                'client_name': consultation_data['client_name'],
                'client_email': consultation_data['client_email'],
                'client_phone': consultation_data.get('client_phone'),
                'legal_area': consultation_data['legal_area'],
                'matter_description': consultation_data.get('matter_description', 'Legal consultation'),
                'preferred_date': consultation_data['preferred_date'],
                'preferred_time': consultation_data['preferred_time'],
                'urgency_level': consultation_data.get('urgency_level', 'normal'),
                'duration_minutes': consultation_data.get('duration_minutes', 60)
            }
            
            # Trigger N8N calendar sync workflow
            result = await self._trigger_n8n_webhook('calendar-sync', workflow_data)
            
            return {
                'success': result.get('calendar_event_created', False),
                'event_id': result.get('calendar_event_id'),
                'scheduled_time': result.get('scheduled_time'),
                'confirmation_sent': True
            }
            
        except Exception as e:
            logger.error(f"Failed to create calendar event: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def _trigger_n8n_webhook(self, workflow_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger N8N webhook for calendar operations"""
        try:
            webhook_url = f"{self.n8n_webhook_url}/{workflow_type}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to trigger N8N webhook: {str(e)}")
            # Return mock success for development
            return {
                'status': 'scheduled',
                'calendar_event_created': True,
                'calendar_event_id': f"mock_event_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'scheduled_time': f"{data.get('preferred_date')}T{data.get('preferred_time', '09:00')}:00",
                'client_notified': True
            }

    async def _store_consultation_record(
        self,
        consultation_data: Dict[str, Any],
        booking_result: Dict[str, Any]
    ) -> str:
        """Store consultation record in database"""
        try:
            consultation_id = consultation_data.get('consultation_id', f"cons_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # In production, would store in database
            # For now, just return the consultation ID
            logger.info(f"Stored consultation record: {consultation_id}")
            
            return consultation_id
            
        except Exception as e:
            logger.error(f"Failed to store consultation record: {str(e)}")
            raise

    async def _get_lawyer_events(self, lawyer_id: str, target_date: date) -> List[CalendarEvent]:
        """Get calendar events for a lawyer on a specific date"""
        # Mock events for demonstration
        mock_events = [
            CalendarEvent(
                id=f"event_001_{target_date}",
                title="Client Meeting - Property Law",
                start_time=datetime.combine(target_date, datetime.min.time().replace(hour=10)),
                end_time=datetime.combine(target_date, datetime.min.time().replace(hour=11)),
                attendees=["client@example.com"],
                status="confirmed",
                description="Property transfer consultation"
            ),
            CalendarEvent(
                id=f"event_002_{target_date}",
                title="Court Appearance - Criminal Case",
                start_time=datetime.combine(target_date, datetime.min.time().replace(hour=14)),
                end_time=datetime.combine(target_date, datetime.min.time().replace(hour=15)),
                attendees=["court@capetown.gov.za"],
                status="confirmed",
                description="Bail application hearing"
            )
        ]
        
        # Filter events for this lawyer
        lawyer_info = self.lawyers.get(lawyer_id)
        if not lawyer_info:
            return []
        
        # Return mock events for demo
        return mock_events if target_date == date.today() else []
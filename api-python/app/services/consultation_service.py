"""
Consultation Service for Legal Appointment Booking
Handles consultation scheduling, lawyer assignment, and appointment management
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time, timedelta
import uuid

from app.models.chat_schemas import LawyerInfo, TimeSlot, ConsultationSummary

logger = logging.getLogger(__name__)

class Consultation:
    """Consultation model for in-memory representation"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.client_name = kwargs['client_name']
        self.client_email = kwargs['client_email']
        self.client_phone = kwargs.get('client_phone')
        self.legal_area = kwargs['legal_area']
        self.urgency_level = kwargs.get('urgency_level', 'normal')
        self.matter_description = kwargs['matter_description']
        self.matter_priority = kwargs.get('matter_priority', 'normal')
        self.consultation_type = kwargs.get('consultation_type', 'consultation')
        
        # Scheduling
        self.preferred_date = kwargs.get('preferred_date')
        self.preferred_time = kwargs.get('preferred_time')
        self.scheduled_date = kwargs.get('scheduled_date')
        self.scheduled_time = kwargs.get('scheduled_time')
        self.estimated_duration = kwargs.get('estimated_duration', 60)
        self.estimated_cost = kwargs.get('estimated_cost', 0.0)
        
        # Assignment
        self.status = kwargs.get('status', 'pending_assignment')
        self.assigned_lawyer_id = kwargs.get('assigned_lawyer_id')
        self.assigned_lawyer_name = kwargs.get('assigned_lawyer_name')
        
        # Metadata
        self.matter_analysis = kwargs.get('matter_analysis', {})
        self.preparation_notes = kwargs.get('preparation_notes')
        self.cancellation_reason = kwargs.get('cancellation_reason')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = datetime.utcnow()

class LawyerAvailability:
    """Lawyer availability model"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.lawyer_id = kwargs['lawyer_id']
        self.lawyer_name = kwargs['lawyer_name']
        self.legal_areas = kwargs.get('legal_areas', [])
        self.date = kwargs['date']
        self.start_time = kwargs['start_time']
        self.end_time = kwargs['end_time']
        self.is_available = kwargs.get('is_available', True)
        self.consultation_id = kwargs.get('consultation_id')
        self.notes = kwargs.get('notes')

class ConsultationService:
    """Service for managing legal consultation bookings"""
    
    def __init__(self):
        # In-memory storage (replace with database in production)
        self._consultations = {}  # consultation_id -> Consultation
        self._lawyer_availability = []  # List of LawyerAvailability
        
        # Initialize with sample lawyer availability
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample lawyer availability"""
        sample_lawyers = [
            {
                'lawyer_id': 'lawyer_001',
                'lawyer_name': 'Advocate Sarah Mthembu',
                'legal_areas': ['criminal', 'constitutional'],
                'date': date.today() + timedelta(days=1),
                'start_time': time(9, 0),
                'end_time': time(12, 0)
            },
            {
                'lawyer_id': 'lawyer_001',
                'lawyer_name': 'Advocate Sarah Mthembu',
                'legal_areas': ['criminal', 'constitutional'],
                'date': date.today() + timedelta(days=1),
                'start_time': time(14, 0),
                'end_time': time(17, 0)
            },
            {
                'lawyer_id': 'lawyer_002',
                'lawyer_name': 'Attorney Johan van der Merwe',
                'legal_areas': ['commercial', 'civil'],
                'date': date.today() + timedelta(days=1),
                'start_time': time(8, 0),
                'end_time': time(12, 0)
            },
            {
                'lawyer_id': 'lawyer_003',
                'lawyer_name': 'Attorney Nomsa Radebe',
                'legal_areas': ['family', 'property'],
                'date': date.today() + timedelta(days=2),
                'start_time': time(9, 0),
                'end_time': time(16, 0)
            }
        ]
        
        self._lawyer_availability = [
            LawyerAvailability(**lawyer_data) 
            for lawyer_data in sample_lawyers
        ]

    async def create_consultation(self, **kwargs) -> Consultation:
        """Create a new consultation booking"""
        try:
            consultation = Consultation(**kwargs)
            
            # Analyze matter and set priority
            await self._analyze_consultation_priority(consultation)
            
            # Try to auto-assign if urgent
            if consultation.urgency_level in ['high', 'critical']:
                await self._attempt_urgent_assignment(consultation)
            
            self._consultations[consultation.id] = consultation
            
            logger.info(f"Created consultation {consultation.id} for {consultation.client_email}")
            return consultation
            
        except Exception as e:
            logger.error(f"Failed to create consultation: {str(e)}")
            raise

    async def get_consultation(self, consultation_id: str) -> Optional[Consultation]:
        """Get consultation by ID"""
        return self._consultations.get(consultation_id)

    async def update_consultation(
        self, 
        consultation_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[Consultation]:
        """Update consultation details"""
        try:
            consultation = self._consultations.get(consultation_id)
            if not consultation:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(consultation, key) and value is not None:
                    setattr(consultation, key, value)
            
            consultation.updated_at = datetime.utcnow()
            
            logger.info(f"Updated consultation {consultation_id}")
            return consultation
            
        except Exception as e:
            logger.error(f"Failed to update consultation: {str(e)}")
            return None

    async def cancel_consultation(
        self, 
        consultation_id: str, 
        cancellation_reason: Optional[str] = None
    ) -> bool:
        """Cancel a consultation"""
        try:
            consultation = self._consultations.get(consultation_id)
            if not consultation or consultation.status == 'cancelled':
                return False
            
            consultation.status = 'cancelled'
            consultation.cancellation_reason = cancellation_reason
            consultation.updated_at = datetime.utcnow()
            
            # Free up lawyer availability if scheduled
            await self._free_lawyer_availability(consultation_id)
            
            logger.info(f"Cancelled consultation {consultation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel consultation: {str(e)}")
            return False

    async def get_available_slots(
        self,
        date: date,
        legal_area: Optional[str] = None,
        urgency_level: str = 'normal'
    ) -> List[Dict[str, Any]]:
        """Get available time slots for a specific date"""
        try:
            available_slots = []
            
            # Filter availability by date and legal area
            for availability in self._lawyer_availability:
                if availability.date != date or not availability.is_available:
                    continue
                
                if legal_area and legal_area not in availability.legal_areas:
                    continue
                
                # Create time slots (1-hour intervals)
                current_time = availability.start_time
                end_time = availability.end_time
                
                while current_time < end_time:
                    slot_end = time(
                        (current_time.hour + 1) % 24,
                        current_time.minute
                    )
                    
                    if slot_end <= end_time:
                        available_slots.append({
                            "start_time": current_time.strftime("%H:%M"),
                            "end_time": slot_end.strftime("%H:%M"),
                            "lawyer_id": availability.lawyer_id,
                            "lawyer_name": availability.lawyer_name,
                            "legal_areas": availability.legal_areas,
                            "urgency_compatible": self._is_urgency_compatible(
                                urgency_level, 
                                availability.legal_areas
                            )
                        })
                    
                    # Move to next hour
                    current_time = slot_end
                    if current_time.hour == 0:  # Midnight wrap
                        break
            
            return available_slots[:20]  # Limit results
            
        except Exception as e:
            logger.error(f"Failed to get available slots: {str(e)}")
            return []

    async def get_recommended_lawyers(
        self,
        legal_area: Optional[str] = None,
        target_date: Optional[date] = None
    ) -> List[LawyerInfo]:
        """Get recommended lawyers based on legal area and availability"""
        try:
            lawyer_info = {}
            
            # Aggregate lawyer information
            for availability in self._lawyer_availability:
                if target_date and availability.date != target_date:
                    continue
                
                if legal_area and legal_area not in availability.legal_areas:
                    continue
                
                lawyer_id = availability.lawyer_id
                if lawyer_id not in lawyer_info:
                    lawyer_info[lawyer_id] = {
                        'id': lawyer_id,
                        'name': availability.lawyer_name,
                        'legal_areas': list(set(availability.legal_areas)),
                        'rating': self._get_lawyer_rating(lawyer_id),
                        'experience_years': self._get_lawyer_experience(lawyer_id),
                        'hourly_rate': self._get_lawyer_hourly_rate(lawyer_id, legal_area)
                    }
                else:
                    # Combine legal areas
                    existing_areas = set(lawyer_info[lawyer_id]['legal_areas'])
                    new_areas = set(availability.legal_areas)
                    lawyer_info[lawyer_id]['legal_areas'] = list(existing_areas.union(new_areas))
            
            # Convert to LawyerInfo objects
            recommendations = [
                LawyerInfo(**info) for info in lawyer_info.values()
            ]
            
            # Sort by rating and experience
            recommendations.sort(
                key=lambda x: (x.rating or 0, x.experience_years or 0),
                reverse=True
            )
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommended lawyers: {str(e)}")
            return []

    async def get_next_available_date(
        self,
        legal_area: Optional[str] = None,
        from_date: Optional[date] = None
    ) -> Optional[str]:
        """Get next available date for consultation"""
        try:
            if from_date is None:
                from_date = date.today()
            
            # Check next 30 days
            for i in range(1, 31):
                check_date = from_date + timedelta(days=i)
                slots = await self.get_available_slots(check_date, legal_area)
                
                if slots:
                    return check_date.strftime("%Y-%m-%d")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get next available date: {str(e)}")
            return None

    async def get_client_consultations(
        self,
        client_email: str,
        status_filter: Optional[str] = None,
        limit: int = 20
    ) -> List[Consultation]:
        """Get all consultations for a specific client"""
        try:
            client_consultations = [
                consultation for consultation in self._consultations.values()
                if consultation.client_email == client_email
            ]
            
            # Apply status filter
            if status_filter:
                client_consultations = [
                    c for c in client_consultations 
                    if c.status == status_filter
                ]
            
            # Sort by creation date (most recent first)
            client_consultations.sort(
                key=lambda c: c.created_at,
                reverse=True
            )
            
            return client_consultations[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get client consultations: {str(e)}")
            return []

    # Helper methods

    async def _analyze_consultation_priority(self, consultation: Consultation):
        """Analyze consultation and set priority level"""
        try:
            # Keywords that indicate high priority
            high_priority_keywords = [
                'urgent', 'emergency', 'court', 'deadline', 'arrest',
                'police', 'tomorrow', 'today', 'immediate'
            ]
            
            description_lower = consultation.matter_description.lower()
            
            # Check for high priority indicators
            if any(keyword in description_lower for keyword in high_priority_keywords):
                consultation.matter_priority = 'high'
            elif consultation.urgency_level in ['high', 'critical']:
                consultation.matter_priority = 'high'
            elif consultation.legal_area in ['criminal', 'constitutional']:
                consultation.matter_priority = 'elevated'
            else:
                consultation.matter_priority = 'normal'
                
            logger.info(f"Set consultation {consultation.id} priority to {consultation.matter_priority}")
            
        except Exception as e:
            logger.error(f"Failed to analyze consultation priority: {str(e)}")

    async def _attempt_urgent_assignment(self, consultation: Consultation):
        """Attempt to auto-assign urgent consultations"""
        try:
            if consultation.urgency_level not in ['high', 'critical']:
                return
            
            # Find available lawyers for this legal area
            tomorrow = date.today() + timedelta(days=1)
            slots = await self.get_available_slots(
                tomorrow, 
                consultation.legal_area, 
                consultation.urgency_level
            )
            
            if slots:
                # Assign to first available lawyer
                first_slot = slots[0]
                consultation.assigned_lawyer_id = first_slot['lawyer_id']
                consultation.assigned_lawyer_name = first_slot['lawyer_name']
                consultation.scheduled_date = tomorrow
                consultation.scheduled_time = time.fromisoformat(first_slot['start_time'])
                consultation.status = 'scheduled'
                
                # Mark lawyer slot as unavailable
                await self._book_lawyer_slot(
                    first_slot['lawyer_id'],
                    tomorrow,
                    first_slot['start_time'],
                    consultation.id
                )
                
                logger.info(f"Auto-assigned urgent consultation {consultation.id} to {consultation.assigned_lawyer_name}")
            
        except Exception as e:
            logger.error(f"Failed to auto-assign urgent consultation: {str(e)}")

    async def _book_lawyer_slot(
        self,
        lawyer_id: str,
        date: date,
        start_time: str,
        consultation_id: str
    ):
        """Book a specific lawyer time slot"""
        try:
            start_time_obj = time.fromisoformat(start_time)
            
            for availability in self._lawyer_availability:
                if (availability.lawyer_id == lawyer_id and 
                    availability.date == date and
                    availability.start_time <= start_time_obj < availability.end_time):
                    
                    availability.is_available = False
                    availability.consultation_id = consultation_id
                    break
                    
        except Exception as e:
            logger.error(f"Failed to book lawyer slot: {str(e)}")

    async def _free_lawyer_availability(self, consultation_id: str):
        """Free up lawyer availability when consultation is cancelled"""
        try:
            for availability in self._lawyer_availability:
                if availability.consultation_id == consultation_id:
                    availability.is_available = True
                    availability.consultation_id = None
                    
        except Exception as e:
            logger.error(f"Failed to free lawyer availability: {str(e)}")

    def _is_urgency_compatible(self, urgency_level: str, legal_areas: List[str]) -> bool:
        """Check if lawyer can handle urgent matters in this area"""
        urgent_capable_areas = ['criminal', 'constitutional', 'emergency']
        
        if urgency_level in ['high', 'critical']:
            return any(area in urgent_capable_areas for area in legal_areas)
        
        return True

    def _get_lawyer_rating(self, lawyer_id: str) -> float:
        """Get lawyer rating (mock implementation)"""
        ratings = {
            'lawyer_001': 4.8,
            'lawyer_002': 4.5,
            'lawyer_003': 4.7
        }
        return ratings.get(lawyer_id, 4.0)

    def _get_lawyer_experience(self, lawyer_id: str) -> int:
        """Get lawyer experience in years (mock implementation)"""
        experience = {
            'lawyer_001': 15,
            'lawyer_002': 12,
            'lawyer_003': 8
        }
        return experience.get(lawyer_id, 5)

    def _get_lawyer_hourly_rate(self, lawyer_id: str, legal_area: Optional[str]) -> float:
        """Get lawyer hourly rate (mock implementation)"""
        base_rates = {
            'lawyer_001': 1800.0,
            'lawyer_002': 1500.0,
            'lawyer_003': 1200.0
        }
        
        base_rate = base_rates.get(lawyer_id, 1000.0)
        
        # Area-specific multipliers
        if legal_area in ['constitutional', 'commercial']:
            base_rate *= 1.2
        elif legal_area in ['criminal']:
            base_rate *= 1.1
        
        return base_rate

# Global service instance
consultation_service = ConsultationService()
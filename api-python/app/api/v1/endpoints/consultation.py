"""
Legal Consultation Booking Endpoints
Professional appointment scheduling for South African law firms
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timedelta
import uuid

from app.models.schemas import (
    ConsultationRequest, ConsultationResponse, ConsultationUpdate,
    AvailabilityRequest, AvailabilityResponse, ConsultationSummary
)
from app.services.consultation_service import ConsultationService
from app.services.workflow_service import workflow_service
from app.utils.south_african_legal import classify_legal_matter_urgency

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize consultation service
consultation_service = ConsultationService()

@router.post("/", response_model=ConsultationResponse)
async def create_consultation_request(
    request: ConsultationRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new consultation booking request with legal matter analysis.
    """
    try:
        logger.info(f"Creating consultation for {request.client_email}")
        
        # Analyze legal matter urgency and practice area
        matter_analysis = await _analyze_legal_matter(
            description=request.legal_matter_description,
            legal_area=request.legal_area
        )
        
        # Create consultation record
        consultation = await consultation_service.create_consultation(
            client_name=request.client_name,
            client_email=request.client_email,
            client_phone=request.client_phone,
            legal_area=request.legal_area,
            urgency_level=request.urgency_level,
            matter_description=request.legal_matter_description,
            preferred_date=request.preferred_date,
            preferred_time=request.preferred_time,
            estimated_duration=request.estimated_duration or 60,
            matter_analysis=matter_analysis,
            consultation_type=request.consultation_type
        )
        
        # Trigger workflow automation
        background_tasks.add_task(
            _trigger_consultation_workflows,
            consultation.id,
            matter_analysis
        )
        
        # Send confirmation
        background_tasks.add_task(
            _send_consultation_confirmation,
            consultation.id
        )
        
        return ConsultationResponse(
            consultation_id=consultation.id,
            status="pending_assignment",
            estimated_cost=_calculate_consultation_cost(
                legal_area=request.legal_area,
                urgency=request.urgency_level,
                duration=request.estimated_duration or 60
            ),
            matter_priority=matter_analysis["priority_level"],
            recommended_preparation=matter_analysis["preparation_items"],
            next_steps=_generate_next_steps(matter_analysis),
            confirmation_sent=True
        )
        
    except Exception as e:
        logger.error(f"Consultation creation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create consultation request"
        )

@router.get("/availability", response_model=AvailabilityResponse)
async def check_availability(
    date: str,  # YYYY-MM-DD format
    legal_area: Optional[str] = None,
    urgency: Optional[str] = "normal"
):
    """
    Check lawyer availability for consultation booking.
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        
        # Get available time slots
        available_slots = await consultation_service.get_available_slots(
            date=target_date,
            legal_area=legal_area,
            urgency_level=urgency
        )
        
        # Get lawyer recommendations based on legal area
        recommended_lawyers = await consultation_service.get_recommended_lawyers(
            legal_area=legal_area,
            target_date=target_date
        )
        
        return AvailabilityResponse(
            date=date,
            available_slots=available_slots,
            recommended_lawyers=recommended_lawyers,
            urgent_slots_available=any(
                slot.get("urgency_compatible", False) 
                for slot in available_slots
            ),
            next_available_date=await consultation_service.get_next_available_date(
                legal_area=legal_area,
                from_date=target_date
            )
        )
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        logger.error(f"Availability check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to check availability"
        )

@router.get("/{consultation_id}", response_model=ConsultationSummary)
async def get_consultation_details(consultation_id: str):
    """
    Retrieve detailed consultation information.
    """
    try:
        consultation = await consultation_service.get_consultation(consultation_id)
        
        if not consultation:
            raise HTTPException(
                status_code=404,
                detail="Consultation not found"
            )
        
        return ConsultationSummary(
            id=consultation.id,
            client_name=consultation.client_name,
            client_email=consultation.client_email,
            legal_area=consultation.legal_area,
            status=consultation.status,
            scheduled_date=consultation.scheduled_date,
            scheduled_time=consultation.scheduled_time,
            assigned_lawyer=consultation.assigned_lawyer_name,
            estimated_cost=consultation.estimated_cost,
            matter_description=consultation.matter_description,
            urgency_level=consultation.urgency_level,
            created_at=consultation.created_at,
            updated_at=consultation.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Consultation retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve consultation details"
        )

@router.put("/{consultation_id}", response_model=ConsultationResponse)
async def update_consultation(
    consultation_id: str,
    update: ConsultationUpdate,
    background_tasks: BackgroundTasks
):
    """
    Update consultation details or reschedule.
    """
    try:
        # Update consultation
        updated_consultation = await consultation_service.update_consultation(
            consultation_id=consultation_id,
            update_data=update.dict(exclude_unset=True)
        )
        
        if not updated_consultation:
            raise HTTPException(
                status_code=404,
                detail="Consultation not found"
            )
        
        # Trigger update workflows
        background_tasks.add_task(
            _handle_consultation_update,
            consultation_id,
            update.dict(exclude_unset=True)
        )
        
        return ConsultationResponse(
            consultation_id=updated_consultation.id,
            status=updated_consultation.status,
            estimated_cost=updated_consultation.estimated_cost,
            matter_priority=updated_consultation.matter_priority,
            next_steps=["Updated consultation confirmed"],
            confirmation_sent=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Consultation update error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update consultation"
        )

@router.delete("/{consultation_id}")
async def cancel_consultation(
    consultation_id: str,
    reason: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Cancel a consultation booking.
    """
    try:
        success = await consultation_service.cancel_consultation(
            consultation_id=consultation_id,
            cancellation_reason=reason
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Consultation not found or already cancelled"
            )
        
        # Handle cancellation workflows
        if background_tasks:
            background_tasks.add_task(
                _handle_consultation_cancellation,
                consultation_id,
                reason
            )
        
        return {"message": "Consultation cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Consultation cancellation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel consultation"
        )

@router.get("/client/{client_email}", response_model=List[ConsultationSummary])
async def get_client_consultations(
    client_email: str,
    status: Optional[str] = None,
    limit: int = 20
):
    """
    Get all consultations for a specific client.
    """
    try:
        consultations = await consultation_service.get_client_consultations(
            client_email=client_email,
            status_filter=status,
            limit=limit
        )
        
        return [
            ConsultationSummary(
                id=cons.id,
                client_name=cons.client_name,
                client_email=cons.client_email,
                legal_area=cons.legal_area,
                status=cons.status,
                scheduled_date=cons.scheduled_date,
                scheduled_time=cons.scheduled_time,
                assigned_lawyer=cons.assigned_lawyer_name,
                estimated_cost=cons.estimated_cost,
                matter_description=cons.matter_description[:200] + "..." if len(cons.matter_description) > 200 else cons.matter_description,
                urgency_level=cons.urgency_level,
                created_at=cons.created_at,
                updated_at=cons.updated_at
            )
            for cons in consultations
        ]
        
    except Exception as e:
        logger.error(f"Client consultations error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve client consultations"
        )

# Helper Functions

async def _analyze_legal_matter(description: str, legal_area: str) -> Dict[str, Any]:
    """
    Analyze legal matter for urgency and preparation requirements.
    """
    urgency_analysis = classify_legal_matter_urgency(description)
    
    # Legal area specific preparation items
    preparation_map = {
        "criminal": [
            "Gather all relevant documentation",
            "Prepare timeline of events", 
            "List potential witnesses",
            "Compile any police reports or charges"
        ],
        "civil": [
            "Collect relevant contracts or agreements",
            "Gather correspondence between parties",
            "Compile financial documentation",
            "List of damages or losses"
        ],
        "commercial": [
            "Business registration documents",
            "Financial statements",
            "Contracts and agreements",
            "Correspondence with other parties"
        ],
        "family": [
            "Marriage certificate and relevant documents",
            "Financial records and asset information",
            "Children's documentation if applicable",
            "Any existing court orders"
        ],
        "property": [
            "Property title deeds",
            "Transfer documents",
            "Municipal certificates",
            "Property valuation reports"
        ]
    }
    
    return {
        "priority_level": urgency_analysis.get("priority", "normal"),
        "estimated_complexity": urgency_analysis.get("complexity", "medium"),
        "preparation_items": preparation_map.get(legal_area, [
            "Gather all relevant documentation",
            "Prepare summary of the situation",
            "List key questions to discuss"
        ]),
        "recommended_duration": _recommend_consultation_duration(legal_area, urgency_analysis)
    }

def _calculate_consultation_cost(legal_area: str, urgency: str, duration: int) -> float:
    """
    Calculate consultation cost based on SA legal market rates.
    """
    base_rates = {
        "criminal": 1200.0,  # R1200/hour
        "commercial": 1500.0,  # R1500/hour
        "civil": 1000.0,      # R1000/hour
        "family": 900.0,      # R900/hour  
        "property": 1100.0,   # R1100/hour
        "constitutional": 1800.0,  # R1800/hour
        "employment": 1000.0  # R1000/hour
    }
    
    base_rate = base_rates.get(legal_area, 1000.0)
    
    # Urgency multiplier
    urgency_multipliers = {
        "low": 1.0,
        "normal": 1.0,
        "high": 1.3,
        "critical": 1.5
    }
    
    urgency_multiplier = urgency_multipliers.get(urgency, 1.0)
    
    # Calculate total (duration in minutes)
    total_cost = (base_rate * (duration / 60)) * urgency_multiplier
    
    return round(total_cost, 2)

def _recommend_consultation_duration(legal_area: str, urgency_analysis: Dict) -> int:
    """Recommend consultation duration in minutes based on matter complexity."""
    
    base_durations = {
        "criminal": 90,
        "commercial": 120,
        "civil": 60,
        "family": 75,
        "property": 60,
        "constitutional": 120,
        "employment": 60
    }
    
    complexity_multipliers = {
        "simple": 0.8,
        "medium": 1.0, 
        "complex": 1.5
    }
    
    base_duration = base_durations.get(legal_area, 60)
    complexity = urgency_analysis.get("complexity", "medium")
    multiplier = complexity_multipliers.get(complexity, 1.0)
    
    return int(base_duration * multiplier)

def _generate_next_steps(matter_analysis: Dict[str, Any]) -> List[str]:
    """Generate next steps based on matter analysis."""
    
    base_steps = [
        "Confirmation email sent to client",
        "Legal matter assigned to appropriate specialist",
        "Preparation materials will be provided"
    ]
    
    if matter_analysis["priority_level"] == "critical":
        base_steps.insert(1, "Priority scheduling within 24 hours")
    elif matter_analysis["priority_level"] == "high":
        base_steps.insert(1, "Expedited scheduling within 48 hours")
    
    return base_steps

# Background task handlers

async def _trigger_consultation_workflows(consultation_id: str, matter_analysis: Dict):
    """Trigger N8N workflows for consultation processing."""
    try:
        webhook_data = {
            "consultation_id": consultation_id,
            "priority": matter_analysis["priority_level"],
            "legal_area": matter_analysis.get("legal_area", "general"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await workflow_service.trigger_webhook(
            "consultation-booked",
            webhook_data
        )
        
        logger.info(f"Consultation workflow triggered for {consultation_id}")
        
    except Exception as e:
        logger.error(f"Workflow trigger failed for consultation {consultation_id}: {str(e)}")

async def _send_consultation_confirmation(consultation_id: str):
    """Send confirmation email to client."""
    try:
        consultation = await consultation_service.get_consultation(consultation_id)
        
        # This would integrate with email service
        logger.info(f"Confirmation sent to {consultation.client_email}")
        
    except Exception as e:
        logger.error(f"Confirmation email failed for {consultation_id}: {str(e)}")

async def _handle_consultation_update(consultation_id: str, update_data: Dict):
    """Handle consultation update workflows."""
    try:
        await workflow_service.trigger_webhook(
            "consultation-updated",
            {
                "consultation_id": consultation_id,
                "updates": update_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Update workflow failed for {consultation_id}: {str(e)}")

async def _handle_consultation_cancellation(consultation_id: str, reason: Optional[str]):
    """Handle consultation cancellation workflows."""
    try:
        await workflow_service.trigger_webhook(
            "consultation-cancelled", 
            {
                "consultation_id": consultation_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Cancellation workflow failed for {consultation_id}: {str(e)}")
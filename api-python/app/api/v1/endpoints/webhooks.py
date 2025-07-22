"""
Webhook Endpoints for N8N Workflow Integration
Trigger automation workflows for legal practice management
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Optional, Dict, Any
import logging
import json
from datetime import datetime

from app.services.workflow_service import workflow_service
from app.services.consultation_service import ConsultationService
from app.services.conversation_service import ConversationService

router = APIRouter()
logger = logging.getLogger(__name__)

consultation_service = ConsultationService()
conversation_service = ConversationService()

@router.post("/consultation-booked")
async def webhook_consultation_booked(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook triggered when a consultation is booked.
    Initiates scheduling, confirmation, and CRM workflows.
    """
    try:
        payload = await request.json()
        consultation_id = payload.get("consultation_id")
        
        logger.info(f"Consultation booked webhook: {consultation_id}")
        
        # Get consultation details
        consultation = await consultation_service.get_consultation(consultation_id)
        if not consultation:
            return {"error": "Consultation not found", "status": "failed"}
        
        # Trigger parallel workflows
        workflow_data = {
            "consultation_id": consultation_id,
            "client_email": consultation.client_email,
            "client_name": consultation.client_name,
            "legal_area": consultation.legal_area,
            "urgency_level": consultation.urgency_level,
            "preferred_date": consultation.preferred_date.isoformat() if consultation.preferred_date else None,
            "estimated_cost": consultation.estimated_cost,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 1. Calendar Scheduling Workflow
        background_tasks.add_task(
            _trigger_calendar_workflow,
            consultation_id,
            workflow_data
        )
        
        # 2. Client Confirmation Workflow
        background_tasks.add_task(
            _trigger_confirmation_workflow,
            consultation_id,
            workflow_data
        )
        
        # 3. CRM Integration Workflow
        background_tasks.add_task(
            _trigger_crm_workflow,
            consultation_id,
            workflow_data
        )
        
        # 4. Lawyer Assignment Workflow
        if consultation.urgency_level in ["high", "critical"]:
            background_tasks.add_task(
                _trigger_urgent_assignment_workflow,
                consultation_id,
                workflow_data
            )
        
        return {
            "status": "processed",
            "consultation_id": consultation_id,
            "workflows_triggered": [
                "calendar_scheduling",
                "client_confirmation", 
                "crm_integration",
                "lawyer_assignment" if consultation.urgency_level in ["high", "critical"] else None
            ]
        }
        
    except Exception as e:
        logger.error(f"Consultation booked webhook error: {str(e)}")
        return {"error": str(e), "status": "failed"}

@router.post("/chat-escalation")
async def webhook_chat_escalation(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook triggered when chat conversation needs human escalation.
    """
    try:
        payload = await request.json()
        conversation_id = payload.get("conversation_id")
        escalation_reason = payload.get("reason", "unknown")
        
        logger.info(f"Chat escalation webhook: {conversation_id}, reason: {escalation_reason}")
        
        # Get conversation details
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            return {"error": "Conversation not found", "status": "failed"}
        
        escalation_data = {
            "conversation_id": conversation_id,
            "session_id": conversation.session_id,
            "user_id": conversation.user_id,
            "escalation_reason": escalation_reason,
            "legal_context": conversation.legal_matter_context,
            "message_count": conversation.message_count,
            "urgency": _determine_escalation_urgency(escalation_reason),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Trigger escalation workflows
        background_tasks.add_task(
            _trigger_escalation_workflow,
            escalation_data
        )
        
        # Update conversation status
        await conversation_service.update_conversation_status(
            conversation_id=conversation_id,
            status="escalated",
            escalation_reason=escalation_reason
        )
        
        return {
            "status": "escalated",
            "conversation_id": conversation_id,
            "urgency_level": escalation_data["urgency"],
            "estimated_response_time": _estimate_response_time(escalation_data["urgency"])
        }
        
    except Exception as e:
        logger.error(f"Chat escalation webhook error: {str(e)}")
        return {"error": str(e), "status": "failed"}

@router.post("/document-uploaded")
async def webhook_document_uploaded(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook triggered when legal document is uploaded for processing.
    """
    try:
        payload = await request.json()
        document_id = payload.get("document_id")
        document_type = payload.get("document_type", "unknown")
        
        logger.info(f"Document uploaded webhook: {document_id}, type: {document_type}")
        
        document_data = {
            "document_id": document_id,
            "document_type": document_type,
            "upload_timestamp": payload.get("upload_timestamp", datetime.utcnow().isoformat()),
            "client_id": payload.get("client_id"),
            "matter_id": payload.get("matter_id"),
            "file_size": payload.get("file_size", 0),
            "jurisdiction": payload.get("jurisdiction", "South Africa")
        }
        
        # Trigger document processing workflows
        background_tasks.add_task(
            _trigger_document_processing_workflow,
            document_data
        )
        
        # Trigger legal analysis workflow
        if document_type in ["contract", "legal_brief", "court_filing"]:
            background_tasks.add_task(
                _trigger_legal_analysis_workflow,
                document_data
            )
        
        return {
            "status": "processing_initiated",
            "document_id": document_id,
            "workflows_triggered": [
                "document_processing",
                "legal_analysis" if document_type in ["contract", "legal_brief", "court_filing"] else None
            ]
        }
        
    except Exception as e:
        logger.error(f"Document uploaded webhook error: {str(e)}")
        return {"error": str(e), "status": "failed"}

@router.post("/legal-deadline")
async def webhook_legal_deadline(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook triggered for legal deadline reminders and compliance tracking.
    """
    try:
        payload = await request.json()
        deadline_type = payload.get("deadline_type")
        matter_id = payload.get("matter_id")
        deadline_date = payload.get("deadline_date")
        
        logger.info(f"Legal deadline webhook: {deadline_type} for matter {matter_id}")
        
        deadline_data = {
            "deadline_type": deadline_type,
            "matter_id": matter_id,
            "deadline_date": deadline_date,
            "client_id": payload.get("client_id"),
            "urgency_level": payload.get("urgency_level", "normal"),
            "court_details": payload.get("court_details", {}),
            "required_documents": payload.get("required_documents", []),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Trigger deadline management workflows
        background_tasks.add_task(
            _trigger_deadline_workflow,
            deadline_data
        )
        
        # Trigger compliance monitoring
        if deadline_type in ["court_filing", "regulatory_compliance"]:
            background_tasks.add_task(
                _trigger_compliance_workflow,
                deadline_data
            )
        
        return {
            "status": "deadline_tracked",
            "matter_id": matter_id,
            "deadline_type": deadline_type,
            "monitoring_active": True
        }
        
    except Exception as e:
        logger.error(f"Legal deadline webhook error: {str(e)}")
        return {"error": str(e), "status": "failed"}

@router.post("/crm-sync")
async def webhook_crm_sync(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook for CRM data synchronization with legal practice management systems.
    """
    try:
        payload = await request.json()
        sync_type = payload.get("sync_type", "full")
        entity_type = payload.get("entity_type")  # client, matter, consultation
        entity_id = payload.get("entity_id")
        
        logger.info(f"CRM sync webhook: {sync_type} sync for {entity_type} {entity_id}")
        
        sync_data = {
            "sync_type": sync_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "target_systems": payload.get("target_systems", ["primary_crm"]),
            "data_payload": payload.get("data", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Trigger CRM synchronization workflows
        background_tasks.add_task(
            _trigger_crm_sync_workflow,
            sync_data
        )
        
        # Trigger billing integration if needed
        if entity_type in ["consultation", "matter"]:
            background_tasks.add_task(
                _trigger_billing_integration_workflow,
                sync_data
            )
        
        return {
            "status": "sync_initiated",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "target_systems": sync_data["target_systems"]
        }
        
    except Exception as e:
        logger.error(f"CRM sync webhook error: {str(e)}")
        return {"error": str(e), "status": "failed"}

@router.post("/emergency-escalation")
async def webhook_emergency_escalation(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Webhook for emergency legal matter escalation.
    """
    try:
        payload = await request.json()
        escalation_source = payload.get("source")  # chat, voice, consultation
        entity_id = payload.get("entity_id")
        emergency_type = payload.get("emergency_type", "unknown")
        
        logger.critical(f"EMERGENCY ESCALATION: {emergency_type} from {escalation_source}")
        
        emergency_data = {
            "escalation_source": escalation_source,
            "entity_id": entity_id,
            "emergency_type": emergency_type,
            "client_contact": payload.get("client_contact", {}),
            "legal_context": payload.get("legal_context", {}),
            "urgency_score": payload.get("urgency_score", 10),  # Max urgency
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Trigger immediate emergency response
        background_tasks.add_task(
            _trigger_emergency_response_workflow,
            emergency_data
        )
        
        return {
            "status": "emergency_escalated",
            "entity_id": entity_id,
            "emergency_type": emergency_type,
            "response_initiated": True,
            "escalation_id": f"EMG_{entity_id}_{int(datetime.utcnow().timestamp())}"
        }
        
    except Exception as e:
        logger.error(f"Emergency escalation webhook error: {str(e)}")
        return {"error": str(e), "status": "failed"}

# Helper Functions

def _determine_escalation_urgency(reason: str) -> str:
    """Determine urgency level based on escalation reason."""
    high_urgency_triggers = [
        "emergency", "urgent", "court", "deadline", "arrest", "police"
    ]
    
    if any(trigger in reason.lower() for trigger in high_urgency_triggers):
        return "high"
    return "normal"

def _estimate_response_time(urgency: str) -> str:
    """Estimate human response time based on urgency."""
    response_times = {
        "high": "Within 15 minutes",
        "normal": "Within 2 hours",
        "low": "Within 24 hours"
    }
    return response_times.get(urgency, "Within 2 hours")

# Background Workflow Triggers

async def _trigger_calendar_workflow(consultation_id: str, data: Dict):
    """Trigger calendar scheduling workflow."""
    try:
        await workflow_service.trigger_workflow(
            "calendar-sync",
            {
                **data,
                "workflow_type": "calendar_scheduling",
                "action": "schedule_consultation"
            }
        )
        logger.info(f"Calendar workflow triggered for consultation {consultation_id}")
    except Exception as e:
        logger.error(f"Calendar workflow failed for consultation {consultation_id}: {str(e)}")

async def _trigger_confirmation_workflow(consultation_id: str, data: Dict):
    """Trigger client confirmation workflow."""
    try:
        await workflow_service.trigger_workflow(
            "confirmation-email",
            {
                **data,
                "workflow_type": "client_confirmation",
                "email_template": "consultation_confirmation_sa"
            }
        )
        logger.info(f"Confirmation workflow triggered for consultation {consultation_id}")
    except Exception as e:
        logger.error(f"Confirmation workflow failed for consultation {consultation_id}: {str(e)}")

async def _trigger_crm_workflow(consultation_id: str, data: Dict):
    """Trigger CRM integration workflow."""
    try:
        await workflow_service.trigger_workflow(
            "crm-sync",
            {
                **data,
                "workflow_type": "crm_integration",
                "entity_type": "consultation",
                "sync_target": "primary_crm"
            }
        )
        logger.info(f"CRM workflow triggered for consultation {consultation_id}")
    except Exception as e:
        logger.error(f"CRM workflow failed for consultation {consultation_id}: {str(e)}")

async def _trigger_urgent_assignment_workflow(consultation_id: str, data: Dict):
    """Trigger urgent lawyer assignment workflow."""
    try:
        await workflow_service.trigger_workflow(
            "urgent-assignment",
            {
                **data,
                "workflow_type": "urgent_assignment",
                "assignment_criteria": {
                    "legal_area": data["legal_area"],
                    "urgency": data["urgency_level"],
                    "availability_required": "immediate"
                }
            }
        )
        logger.info(f"Urgent assignment workflow triggered for consultation {consultation_id}")
    except Exception as e:
        logger.error(f"Urgent assignment workflow failed for consultation {consultation_id}: {str(e)}")

async def _trigger_escalation_workflow(escalation_data: Dict):
    """Trigger chat escalation workflow."""
    try:
        await workflow_service.trigger_workflow(
            "chat-escalation",
            {
                **escalation_data,
                "workflow_type": "human_escalation",
                "notification_channels": ["email", "sms", "dashboard"]
            }
        )
        logger.info(f"Escalation workflow triggered for conversation {escalation_data['conversation_id']}")
    except Exception as e:
        logger.error(f"Escalation workflow failed: {str(e)}")

async def _trigger_document_processing_workflow(document_data: Dict):
    """Trigger document processing workflow."""
    try:
        await workflow_service.trigger_workflow(
            "document-processing",
            {
                **document_data,
                "workflow_type": "document_processing",
                "processing_steps": ["ocr", "classification", "indexing", "search_preparation"]
            }
        )
        logger.info(f"Document processing workflow triggered for {document_data['document_id']}")
    except Exception as e:
        logger.error(f"Document processing workflow failed: {str(e)}")

async def _trigger_legal_analysis_workflow(document_data: Dict):
    """Trigger legal document analysis workflow."""
    try:
        await workflow_service.trigger_workflow(
            "legal-analysis",
            {
                **document_data,
                "workflow_type": "legal_analysis",
                "analysis_types": ["risk_assessment", "compliance_check", "citation_extraction"]
            }
        )
        logger.info(f"Legal analysis workflow triggered for {document_data['document_id']}")
    except Exception as e:
        logger.error(f"Legal analysis workflow failed: {str(e)}")

async def _trigger_deadline_workflow(deadline_data: Dict):
    """Trigger legal deadline management workflow."""
    try:
        await workflow_service.trigger_workflow(
            "deadline-management",
            {
                **deadline_data,
                "workflow_type": "deadline_tracking",
                "reminder_schedule": ["7_days", "3_days", "1_day", "2_hours"]
            }
        )
        logger.info(f"Deadline workflow triggered for matter {deadline_data['matter_id']}")
    except Exception as e:
        logger.error(f"Deadline workflow failed: {str(e)}")

async def _trigger_compliance_workflow(deadline_data: Dict):
    """Trigger compliance monitoring workflow."""
    try:
        await workflow_service.trigger_workflow(
            "compliance-monitoring",
            {
                **deadline_data,
                "workflow_type": "compliance_tracking",
                "compliance_framework": "south_african_legal"
            }
        )
        logger.info(f"Compliance workflow triggered for matter {deadline_data['matter_id']}")
    except Exception as e:
        logger.error(f"Compliance workflow failed: {str(e)}")

async def _trigger_crm_sync_workflow(sync_data: Dict):
    """Trigger CRM synchronization workflow."""
    try:
        await workflow_service.trigger_workflow(
            "crm-synchronization",
            {
                **sync_data,
                "workflow_type": "data_synchronization"
            }
        )
        logger.info(f"CRM sync workflow triggered for {sync_data['entity_type']} {sync_data['entity_id']}")
    except Exception as e:
        logger.error(f"CRM sync workflow failed: {str(e)}")

async def _trigger_billing_integration_workflow(sync_data: Dict):
    """Trigger billing integration workflow."""
    try:
        await workflow_service.trigger_workflow(
            "billing-integration",
            {
                **sync_data,
                "workflow_type": "billing_integration",
                "billing_rules": "south_african_legal_rates"
            }
        )
        logger.info(f"Billing integration workflow triggered for {sync_data['entity_type']} {sync_data['entity_id']}")
    except Exception as e:
        logger.error(f"Billing integration workflow failed: {str(e)}")

async def _trigger_emergency_response_workflow(emergency_data: Dict):
    """Trigger emergency response workflow."""
    try:
        await workflow_service.trigger_workflow(
            "emergency-response",
            {
                **emergency_data,
                "workflow_type": "emergency_escalation",
                "response_channels": ["phone", "email", "sms", "dashboard_alert"],
                "escalation_chain": ["senior_partner", "managing_partner", "emergency_contact"]
            }
        )
        logger.critical(f"Emergency response workflow triggered for {emergency_data['entity_id']}")
    except Exception as e:
        logger.error(f"Emergency response workflow failed: {str(e)}")
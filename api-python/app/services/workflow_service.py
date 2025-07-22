"""
Workflow Service for N8N Integration
Handles workflow triggers and automation for legal practice management
"""

import asyncio
import logging
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class WorkflowTrigger:
    """Workflow trigger model"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.trigger_type = kwargs['trigger_type']
        self.entity_type = kwargs['entity_type']
        self.entity_id = kwargs['entity_id']
        self.webhook_url = kwargs.get('webhook_url')
        self.trigger_data = kwargs.get('trigger_data', {})
        self.status = kwargs.get('status', 'pending')
        self.response_data = kwargs.get('response_data', {})
        self.error_message = kwargs.get('error_message')
        self.triggered_at = kwargs.get('triggered_at', datetime.utcnow())
        self.completed_at = kwargs.get('completed_at')

class WorkflowService:
    """Service for managing N8N workflow integrations"""
    
    def __init__(self):
        # N8N configuration (these would come from environment variables)
        self.n8n_webhook_base_url = "http://localhost:5678/webhook"
        self.n8n_api_key = "your_n8n_api_key"
        
        # Workflow trigger tracking
        self._triggers = {}  # trigger_id -> WorkflowTrigger
        
        # Workflow endpoint mappings
        self._workflow_endpoints = {
            # Consultation workflows
            "calendar-sync": f"{self.n8n_webhook_base_url}/calendar-sync",
            "confirmation-email": f"{self.n8n_webhook_base_url}/confirmation-email",
            "reminder-sequence": f"{self.n8n_webhook_base_url}/reminder-sequence",
            
            # CRM workflows
            "crm-sync": f"{self.n8n_webhook_base_url}/crm-sync",
            "contact-sync": f"{self.n8n_webhook_base_url}/contact-sync",
            "matter-creation": f"{self.n8n_webhook_base_url}/matter-creation",
            
            # Legal automation workflows
            "urgent-assignment": f"{self.n8n_webhook_base_url}/urgent-assignment",
            "chat-escalation": f"{self.n8n_webhook_base_url}/chat-escalation",
            "document-processing": f"{self.n8n_webhook_base_url}/document-processing",
            "legal-analysis": f"{self.n8n_webhook_base_url}/legal-analysis",
            
            # Deadline and compliance workflows
            "deadline-management": f"{self.n8n_webhook_base_url}/deadline-management",
            "compliance-monitoring": f"{self.n8n_webhook_base_url}/compliance-monitoring",
            
            # Emergency workflows
            "emergency-response": f"{self.n8n_webhook_base_url}/emergency-response",
            
            # Billing workflows
            "billing-integration": f"{self.n8n_webhook_base_url}/billing-integration",
            "time-tracking": f"{self.n8n_webhook_base_url}/time-tracking"
        }

    async def trigger_webhook(
        self,
        webhook_name: str,
        data: Dict[str, Any],
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """Trigger a specific webhook by name"""
        try:
            webhook_url = self._get_webhook_url(webhook_name)
            if not webhook_url:
                raise ValueError(f"Unknown webhook: {webhook_name}")
            
            return await self._send_webhook_request(webhook_url, data, timeout_seconds)
            
        except Exception as e:
            logger.error(f"Failed to trigger webhook {webhook_name}: {str(e)}")
            raise

    async def trigger_workflow(
        self,
        workflow_name: str,
        data: Dict[str, Any],
        entity_type: str = "unknown",
        entity_id: str = "unknown",
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """Trigger a workflow and track the trigger"""
        try:
            # Create workflow trigger record
            trigger = WorkflowTrigger(
                trigger_type=workflow_name,
                entity_type=entity_type,
                entity_id=entity_id,
                webhook_url=self._get_webhook_url(workflow_name),
                trigger_data=data
            )
            
            self._triggers[trigger.id] = trigger
            
            # Send webhook request
            response = await self.trigger_webhook(workflow_name, data, timeout_seconds)
            
            # Update trigger with response
            trigger.response_data = response
            trigger.status = "completed"
            trigger.completed_at = datetime.utcnow()
            
            logger.info(f"Successfully triggered workflow {workflow_name} (trigger: {trigger.id})")
            return response
            
        except Exception as e:
            # Update trigger with error
            if 'trigger' in locals():
                trigger.status = "failed"
                trigger.error_message = str(e)
                trigger.completed_at = datetime.utcnow()
            
            logger.error(f"Failed to trigger workflow {workflow_name}: {str(e)}")
            raise

    async def get_trigger_status(self, trigger_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow trigger"""
        trigger = self._triggers.get(trigger_id)
        if not trigger:
            return None
        
        return {
            "trigger_id": trigger.id,
            "trigger_type": trigger.trigger_type,
            "entity_type": trigger.entity_type,
            "entity_id": trigger.entity_id,
            "status": trigger.status,
            "triggered_at": trigger.triggered_at.isoformat(),
            "completed_at": trigger.completed_at.isoformat() if trigger.completed_at else None,
            "error_message": trigger.error_message,
            "response_data": trigger.response_data
        }

    async def get_workflow_history(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 50
    ) -> list:
        """Get workflow trigger history"""
        try:
            triggers = list(self._triggers.values())
            
            # Filter by entity if specified
            if entity_type:
                triggers = [t for t in triggers if t.entity_type == entity_type]
            if entity_id:
                triggers = [t for t in triggers if t.entity_id == entity_id]
            
            # Sort by trigger time (most recent first)
            triggers.sort(key=lambda t: t.triggered_at, reverse=True)
            
            # Convert to dictionaries and apply limit
            return [
                {
                    "trigger_id": t.id,
                    "trigger_type": t.trigger_type,
                    "entity_type": t.entity_type,
                    "entity_id": t.entity_id,
                    "status": t.status,
                    "triggered_at": t.triggered_at.isoformat(),
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                    "error_message": t.error_message
                }
                for t in triggers[:limit]
            ]
            
        except Exception as e:
            logger.error(f"Failed to get workflow history: {str(e)}")
            return []

    async def register_webhook_endpoint(
        self,
        workflow_name: str,
        webhook_url: str
    ) -> bool:
        """Register a new webhook endpoint"""
        try:
            self._workflow_endpoints[workflow_name] = webhook_url
            logger.info(f"Registered webhook endpoint: {workflow_name} -> {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register webhook endpoint: {str(e)}")
            return False

    async def test_webhook_connectivity(self, workflow_name: str) -> Dict[str, Any]:
        """Test connectivity to a webhook endpoint"""
        try:
            webhook_url = self._get_webhook_url(workflow_name)
            if not webhook_url:
                return {
                    "workflow_name": workflow_name,
                    "status": "error",
                    "message": "Webhook URL not configured"
                }
            
            # Send test payload
            test_data = {
                "test": True,
                "workflow_name": workflow_name,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "verdict360_connectivity_test"
            }
            
            response = await self._send_webhook_request(webhook_url, test_data, 10)
            
            return {
                "workflow_name": workflow_name,
                "webhook_url": webhook_url,
                "status": "success",
                "response": response,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "workflow_name": workflow_name,
                "status": "error",
                "message": str(e),
                "test_timestamp": datetime.utcnow().isoformat()
            }

    async def batch_trigger_workflows(
        self,
        workflows: list,
        base_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger multiple workflows in parallel"""
        try:
            tasks = []
            
            for workflow_config in workflows:
                workflow_name = workflow_config.get("name")
                workflow_data = {**base_data, **workflow_config.get("data", {})}
                
                task = self.trigger_workflow(
                    workflow_name,
                    workflow_data,
                    entity_type=workflow_config.get("entity_type", "batch"),
                    entity_id=workflow_config.get("entity_id", "batch")
                )
                tasks.append((workflow_name, task))
            
            # Execute all workflows in parallel
            results = {}
            for workflow_name, task in tasks:
                try:
                    result = await task
                    results[workflow_name] = {"status": "success", "data": result}
                except Exception as e:
                    results[workflow_name] = {"status": "error", "message": str(e)}
            
            logger.info(f"Batch triggered {len(workflows)} workflows")
            return results
            
        except Exception as e:
            logger.error(f"Failed to batch trigger workflows: {str(e)}")
            raise

    # Helper methods

    def _get_webhook_url(self, workflow_name: str) -> Optional[str]:
        """Get webhook URL for workflow name"""
        return self._workflow_endpoints.get(workflow_name)

    async def _send_webhook_request(
        self,
        webhook_url: str,
        data: Dict[str, Any],
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """Send HTTP request to webhook endpoint"""
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Verdict360-Legal-Platform/1.0"
            }
            
            # Add API key if configured
            if self.n8n_api_key and self.n8n_api_key != "your_n8n_api_key":
                headers["Authorization"] = f"Bearer {self.n8n_api_key}"
            
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                response = await client.post(
                    webhook_url,
                    json=data,
                    headers=headers
                )
                
                response.raise_for_status()
                
                # Try to parse JSON response, fallback to text
                try:
                    response_data = response.json()
                except:
                    response_data = {"message": response.text}
                
                logger.info(f"Webhook request successful: {webhook_url}")
                return {
                    "status_code": response.status_code,
                    "data": response_data,
                    "webhook_url": webhook_url,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except httpx.TimeoutException:
            logger.error(f"Webhook request timeout: {webhook_url}")
            return {
                "status_code": 408,
                "error": "Request timeout",
                "webhook_url": webhook_url,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Webhook request HTTP error: {e.response.status_code} - {webhook_url}")
            return {
                "status_code": e.response.status_code,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "webhook_url": webhook_url,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Webhook request error: {str(e)} - {webhook_url}")
            return {
                "status_code": 500,
                "error": str(e),
                "webhook_url": webhook_url,
                "timestamp": datetime.utcnow().isoformat()
            }

    # Workflow-specific helper methods

    async def trigger_consultation_workflows(
        self,
        consultation_id: str,
        consultation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger all consultation-related workflows"""
        workflows = [
            {
                "name": "calendar-sync",
                "entity_type": "consultation",
                "entity_id": consultation_id,
                "data": {"action": "schedule", "consultation": consultation_data}
            },
            {
                "name": "confirmation-email", 
                "entity_type": "consultation",
                "entity_id": consultation_id,
                "data": {"template": "consultation_confirmation", "consultation": consultation_data}
            },
            {
                "name": "crm-sync",
                "entity_type": "consultation", 
                "entity_id": consultation_id,
                "data": {"operation": "create", "consultation": consultation_data}
            }
        ]
        
        return await self.batch_trigger_workflows(workflows, consultation_data)

    async def trigger_emergency_workflows(
        self,
        entity_id: str,
        emergency_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger emergency response workflows"""
        workflows = [
            {
                "name": "emergency-response",
                "entity_type": "emergency",
                "entity_id": entity_id,
                "data": {
                    "priority": "CRITICAL",
                    "escalation_chain": ["senior_partner", "managing_partner"],
                    **emergency_data
                }
            },
            {
                "name": "urgent-assignment",
                "entity_type": "emergency",
                "entity_id": entity_id,
                "data": {
                    "urgency": "critical",
                    "require_immediate_response": True,
                    **emergency_data
                }
            }
        ]
        
        return await self.batch_trigger_workflows(workflows, emergency_data)

# Global service instance
workflow_service = WorkflowService()
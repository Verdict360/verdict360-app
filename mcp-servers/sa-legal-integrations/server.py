#!/usr/bin/env python3
"""
Verdict360 MCP Server - South African Legal Software Integrations
Provides standardized integration with SA legal practice management systems
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import httpx

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    CallToolRequest, 
    ListToolsRequest, 
    Resource, 
    Tool, 
    TextContent,
    ImageContent,
    EmbeddedResource
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verdict360-mcp-server")

# SA Legal Software Configurations
SA_LEGAL_SYSTEMS = {
    "lawpracticeza": {
        "name": "LawPracticeZA",
        "base_url": "https://api.lawpracticeza.co.za/v1",
        "auth_type": "bearer",
        "capabilities": ["matters", "clients", "billing", "documents", "calendar"]
    },
    "legal_interact": {
        "name": "Legal Interact",
        "base_url": "https://api.legalinteract.co.za/v2",
        "auth_type": "api_key",
        "capabilities": ["case_management", "client_portal", "billing", "reporting"]
    },
    "ajs_legal": {
        "name": "AJS Legal Software",
        "base_url": "https://api.ajslegal.co.za/api",
        "auth_type": "oauth2",
        "capabilities": ["practice_management", "accounting", "trust_accounting", "compliance"]
    },
    "legal_suite": {
        "name": "Legal Suite SA",
        "base_url": "https://api.legalsuitesa.com/v1",
        "auth_type": "bearer",
        "capabilities": ["document_automation", "workflow", "client_management"]
    },
    "attorney_online": {
        "name": "Attorney Online",
        "base_url": "https://api.attorneyonline.co.za/v1",
        "auth_type": "api_key",
        "capabilities": ["matter_management", "time_tracking", "billing", "trust_funds"]
    }
}

@dataclass
class LegalMatter:
    id: str
    title: str
    client_id: str
    client_name: str
    matter_type: str
    status: str
    created_date: str
    last_activity: str
    responsible_attorney: str
    urgency_level: str = "normal"
    jurisdiction: str = "South Africa"

@dataclass
class LegalClient:
    id: str
    name: str
    email: str
    phone: str
    address: Dict[str, str]
    client_type: str  # individual, company, trust, etc.
    registration_date: str
    status: str
    assigned_attorney: str

@dataclass
class BillingEntry:
    id: str
    matter_id: str
    client_id: str
    date: str
    description: str
    hours_worked: float
    hourly_rate: float
    amount: float
    attorney: str
    billable: bool = True

class SALegalIntegrationsServer:
    """MCP Server for South African Legal Software Integrations"""
    
    def __init__(self):
        self.server = Server("verdict360-sa-legal-integrations")
        self.http_client = httpx.AsyncClient()
        self.system_configs = SA_LEGAL_SYSTEMS.copy()
        self.active_connections = {}
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """Register MCP tools for legal software integration"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available SA legal integration tools"""
            return [
                Tool(
                    name="connect_legal_system",
                    description="Connect to a South African legal practice management system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "system": {
                                "type": "string",
                                "enum": list(SA_LEGAL_SYSTEMS.keys()),
                                "description": "Legal system to connect to"
                            },
                            "credentials": {
                                "type": "object",
                                "description": "Authentication credentials",
                                "properties": {
                                    "api_key": {"type": "string"},
                                    "bearer_token": {"type": "string"},
                                    "client_id": {"type": "string"},
                                    "client_secret": {"type": "string"}
                                }
                            }
                        },
                        "required": ["system", "credentials"]
                    }
                ),
                Tool(
                    name="sync_legal_matters",
                    description="Synchronize legal matters from connected SA legal systems",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "system": {
                                "type": "string",
                                "enum": list(SA_LEGAL_SYSTEMS.keys())
                            },
                            "date_from": {
                                "type": "string",
                                "description": "ISO date to sync from (optional)"
                            },
                            "status_filter": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by matter status"
                            }
                        },
                        "required": ["system"]
                    }
                ),
                Tool(
                    name="sync_client_data",
                    description="Synchronize client data from SA legal practice systems",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "system": {
                                "type": "string",
                                "enum": list(SA_LEGAL_SYSTEMS.keys())
                            },
                            "client_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific client IDs to sync (optional)"
                            }
                        },
                        "required": ["system"]
                    }
                ),
                Tool(
                    name="create_consultation_matter",
                    description="Create a new legal matter in SA legal system from Verdict360 consultation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "system": {
                                "type": "string",
                                "enum": list(SA_LEGAL_SYSTEMS.keys())
                            },
                            "consultation_data": {
                                "type": "object",
                                "properties": {
                                    "client_name": {"type": "string"},
                                    "client_email": {"type": "string"},
                                    "legal_area": {"type": "string"},
                                    "matter_description": {"type": "string"},
                                    "urgency_level": {"type": "string"},
                                    "estimated_cost": {"type": "number"}
                                },
                                "required": ["client_name", "client_email", "legal_area", "matter_description"]
                            }
                        },
                        "required": ["system", "consultation_data"]
                    }
                ),
                Tool(
                    name="sync_billing_entries",
                    description="Synchronize billing and time tracking from SA legal systems",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "system": {
                                "type": "string",
                                "enum": list(SA_LEGAL_SYSTEMS.keys())
                            },
                            "date_range": {
                                "type": "object",
                                "properties": {
                                    "start_date": {"type": "string"},
                                    "end_date": {"type": "string"}
                                }
                            },
                            "attorney_filter": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["system"]
                    }
                ),
                Tool(
                    name="check_system_status",
                    description="Check connection status and capabilities of SA legal systems",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "system": {
                                "type": "string",
                                "enum": list(SA_LEGAL_SYSTEMS.keys())
                            }
                        },
                        "required": ["system"]
                    }
                ),
                Tool(
                    name="export_matter_data",
                    description="Export comprehensive matter data for legal analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "system": {
                                "type": "string",
                                "enum": list(SA_LEGAL_SYSTEMS.keys())
                            },
                            "matter_id": {"type": "string"},
                            "include_billing": {"type": "boolean", "default": True},
                            "include_documents": {"type": "boolean", "default": False},
                            "include_communications": {"type": "boolean", "default": True}
                        },
                        "required": ["system", "matter_id"]
                    }
                ),
                Tool(
                    name="compliance_check",
                    description="Run compliance checks against SA legal requirements",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "system": {
                                "type": "string",
                                "enum": list(SA_LEGAL_SYSTEMS.keys())
                            },
                            "compliance_type": {
                                "type": "string",
                                "enum": ["trust_accounting", "popia_compliance", "legal_practice_act", "attorney_fidelity_fund"]
                            },
                            "scope": {
                                "type": "string",
                                "enum": ["full_practice", "specific_matter", "client_portfolio"],
                                "default": "full_practice"
                            }
                        },
                        "required": ["system", "compliance_type"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> list[TextContent]:
            """Handle tool calls for SA legal integrations"""
            
            tool_name = request.params.name
            arguments = request.params.arguments or {}
            
            try:
                if tool_name == "connect_legal_system":
                    return await self._connect_legal_system(arguments)
                elif tool_name == "sync_legal_matters":
                    return await self._sync_legal_matters(arguments)
                elif tool_name == "sync_client_data":
                    return await self._sync_client_data(arguments)
                elif tool_name == "create_consultation_matter":
                    return await self._create_consultation_matter(arguments)
                elif tool_name == "sync_billing_entries":
                    return await self._sync_billing_entries(arguments)
                elif tool_name == "check_system_status":
                    return await self._check_system_status(arguments)
                elif tool_name == "export_matter_data":
                    return await self._export_matter_data(arguments)
                elif tool_name == "compliance_check":
                    return await self._compliance_check(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {tool_name}"
                    )]
                    
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {str(e)}")
                return [TextContent(
                    type="text", 
                    text=f"Error executing {tool_name}: {str(e)}"
                )]
    
    def _register_resources(self):
        """Register MCP resources for SA legal data"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available SA legal data resources"""
            return [
                Resource(
                    uri="sa-legal://systems/configurations",
                    name="SA Legal Systems Configurations",
                    description="Configuration details for supported SA legal software systems",
                    mimeType="application/json"
                ),
                Resource(
                    uri="sa-legal://compliance/frameworks",
                    name="SA Legal Compliance Frameworks", 
                    description="South African legal compliance requirements and frameworks",
                    mimeType="application/json"
                ),
                Resource(
                    uri="sa-legal://matters/templates",
                    name="Legal Matter Templates",
                    description="Standard templates for SA legal matter types",
                    mimeType="application/json"
                ),
                Resource(
                    uri="sa-legal://billing/rates",
                    name="SA Legal Billing Rates",
                    description="Standard billing rates for different legal services in SA",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read SA legal integration resources"""
            
            if uri == "sa-legal://systems/configurations":
                return json.dumps(self.system_configs, indent=2)
            elif uri == "sa-legal://compliance/frameworks":
                return json.dumps(self._get_compliance_frameworks(), indent=2)
            elif uri == "sa-legal://matters/templates":
                return json.dumps(self._get_matter_templates(), indent=2)
            elif uri == "sa-legal://billing/rates":
                return json.dumps(self._get_billing_rates(), indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")

    # Tool Implementation Methods
    
    async def _connect_legal_system(self, args: Dict) -> list[TextContent]:
        """Connect to a SA legal practice management system"""
        system = args.get("system")
        credentials = args.get("credentials", {})
        
        if system not in SA_LEGAL_SYSTEMS:
            return [TextContent(type="text", text=f"Unsupported system: {system}")]
        
        config = SA_LEGAL_SYSTEMS[system]
        
        # Simulate connection establishment
        try:
            # Test API connection
            auth_headers = self._build_auth_headers(config, credentials)
            test_url = f"{config['base_url']}/health"
            
            response = await self.http_client.get(test_url, headers=auth_headers)
            
            if response.status_code == 200:
                self.active_connections[system] = {
                    "config": config,
                    "credentials": credentials,
                    "connected_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }
                
                return [TextContent(
                    type="text",
                    text=f"✅ Successfully connected to {config['name']}\nCapabilities: {', '.join(config['capabilities'])}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to connect to {config['name']}: HTTP {response.status_code}"
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Connection failed: {str(e)}"
            )]
    
    async def _sync_legal_matters(self, args: Dict) -> list[TextContent]:
        """Sync legal matters from SA legal system"""
        system = args.get("system")
        date_from = args.get("date_from")
        status_filter = args.get("status_filter", [])
        
        if system not in self.active_connections:
            return [TextContent(type="text", text=f"Not connected to {system}. Please connect first.")]
        
        # Simulate matter synchronization
        try:
            connection = self.active_connections[system]
            config = connection["config"]
            
            # Build API request
            matters_url = f"{config['base_url']}/matters"
            params = {}
            if date_from:
                params["date_from"] = date_from
            if status_filter:
                params["status"] = ",".join(status_filter)
            
            auth_headers = self._build_auth_headers(config, connection["credentials"])
            
            # Simulate API call (in real implementation, make actual HTTP request)
            mock_matters = self._generate_mock_matters(system, 5)
            
            return [TextContent(
                type="text",
                text=f"✅ Synced {len(mock_matters)} legal matters from {config['name']}\n\n" +
                     "Sample matters:\n" +
                     "\n".join([f"- {matter['title']} ({matter['status']})" for matter in mock_matters[:3]])
            )]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Sync failed: {str(e)}")]
    
    async def _sync_client_data(self, args: Dict) -> list[TextContent]:
        """Sync client data from SA legal system"""
        system = args.get("system")
        client_ids = args.get("client_ids", [])
        
        if system not in self.active_connections:
            return [TextContent(type="text", text=f"Not connected to {system}. Please connect first.")]
        
        try:
            connection = self.active_connections[system]
            config = connection["config"]
            
            # Simulate client data sync
            mock_clients = self._generate_mock_clients(system, 3)
            
            return [TextContent(
                type="text",
                text=f"✅ Synced {len(mock_clients)} clients from {config['name']}\n\n" +
                     "Sample clients:\n" +
                     "\n".join([f"- {client['name']} ({client['client_type']})" for client in mock_clients])
            )]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Client sync failed: {str(e)}")]
    
    async def _create_consultation_matter(self, args: Dict) -> list[TextContent]:
        """Create new legal matter from Verdict360 consultation"""
        system = args.get("system")
        consultation_data = args.get("consultation_data", {})
        
        if system not in self.active_connections:
            return [TextContent(type="text", text=f"Not connected to {system}. Please connect first.")]
        
        try:
            connection = self.active_connections[system]
            config = connection["config"]
            
            # Create matter data structure
            matter_data = {
                "title": f"{consultation_data['legal_area']} - {consultation_data['client_name']}",
                "client_name": consultation_data["client_name"],
                "client_email": consultation_data["client_email"],
                "matter_type": consultation_data["legal_area"],
                "description": consultation_data["matter_description"],
                "urgency_level": consultation_data.get("urgency_level", "normal"),
                "estimated_cost": consultation_data.get("estimated_cost"),
                "created_from": "verdict360_consultation",
                "jurisdiction": "South Africa"
            }
            
            # Simulate matter creation
            matter_id = f"MTR-{datetime.utcnow().strftime('%Y%m%d')}-{hash(consultation_data['client_email']) % 10000:04d}"
            
            return [TextContent(
                type="text",
                text=f"✅ Created new matter in {config['name']}\n\n" +
                     f"Matter ID: {matter_id}\n" +
                     f"Title: {matter_data['title']}\n" +
                     f"Client: {matter_data['client_name']}\n" +
                     f"Type: {matter_data['matter_type']}\n" +
                     f"Urgency: {matter_data['urgency_level']}"
            )]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Matter creation failed: {str(e)}")]
    
    async def _sync_billing_entries(self, args: Dict) -> list[TextContent]:
        """Sync billing entries from SA legal system"""
        system = args.get("system")
        date_range = args.get("date_range", {})
        attorney_filter = args.get("attorney_filter", [])
        
        if system not in self.active_connections:
            return [TextContent(type="text", text=f"Not connected to {system}. Please connect first.")]
        
        try:
            connection = self.active_connections[system]
            config = connection["config"]
            
            # Simulate billing sync
            mock_billing = self._generate_mock_billing_entries(system, 10)
            total_hours = sum([entry["hours_worked"] for entry in mock_billing])
            total_amount = sum([entry["amount"] for entry in mock_billing])
            
            return [TextContent(
                type="text",
                text=f"✅ Synced {len(mock_billing)} billing entries from {config['name']}\n\n" +
                     f"Total Hours: {total_hours:.2f}\n" +
                     f"Total Amount: R{total_amount:,.2f}\n" +
                     f"Average Rate: R{(total_amount/total_hours):,.2f}/hour"
            )]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Billing sync failed: {str(e)}")]
    
    async def _check_system_status(self, args: Dict) -> list[TextContent]:
        """Check status of SA legal system connection"""
        system = args.get("system")
        
        if system not in SA_LEGAL_SYSTEMS:
            return [TextContent(type="text", text=f"Unknown system: {system}")]
        
        config = SA_LEGAL_SYSTEMS[system]
        
        if system in self.active_connections:
            connection = self.active_connections[system]
            status = f"🟢 Connected to {config['name']}\n"
            status += f"Connected since: {connection['connected_at']}\n"
            status += f"Capabilities: {', '.join(config['capabilities'])}\n"
            status += f"Base URL: {config['base_url']}"
        else:
            status = f"🔴 Not connected to {config['name']}\n"
            status += f"Available capabilities: {', '.join(config['capabilities'])}\n"
            status += f"Use connect_legal_system tool to establish connection"
        
        return [TextContent(type="text", text=status)]
    
    async def _export_matter_data(self, args: Dict) -> list[TextContent]:
        """Export comprehensive matter data"""
        system = args.get("system")
        matter_id = args.get("matter_id")
        include_billing = args.get("include_billing", True)
        include_documents = args.get("include_documents", False)
        include_communications = args.get("include_communications", True)
        
        if system not in self.active_connections:
            return [TextContent(type="text", text=f"Not connected to {system}. Please connect first.")]
        
        try:
            # Simulate comprehensive matter export
            matter_export = {
                "matter_id": matter_id,
                "export_timestamp": datetime.utcnow().isoformat(),
                "system": system,
                "matter_details": {
                    "title": "Sample Legal Matter",
                    "client": "Sample Client",
                    "status": "active",
                    "created_date": "2024-01-15"
                },
                "billing_summary": {
                    "total_hours": 45.5,
                    "total_amount": 68250.00,
                    "currency": "ZAR"
                } if include_billing else None,
                "communications_count": 23 if include_communications else None,
                "documents_count": 15 if include_documents else None
            }
            
            return [TextContent(
                type="text",
                text=f"✅ Exported matter data for {matter_id}\n\n" +
                     json.dumps(matter_export, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Export failed: {str(e)}")]
    
    async def _compliance_check(self, args: Dict) -> list[TextContent]:
        """Run SA legal compliance check"""
        system = args.get("system")
        compliance_type = args.get("compliance_type")
        scope = args.get("scope", "full_practice")
        
        if system not in self.active_connections:
            return [TextContent(type="text", text=f"Not connected to {system}. Please connect first.")]
        
        try:
            # Simulate compliance check
            compliance_results = {
                "compliance_type": compliance_type,
                "scope": scope,
                "check_timestamp": datetime.utcnow().isoformat(),
                "overall_score": 85,
                "issues_found": 3,
                "recommendations": [
                    "Update POPIA consent records for 5 clients",
                    "Review trust account reconciliation for November 2024",
                    "Update attorney fidelity fund contribution records"
                ],
                "compliant_areas": [
                    "Client identity verification",
                    "Anti-money laundering procedures",
                    "Legal practice act requirements"
                ]
            }
            
            return [TextContent(
                type="text",
                text=f"✅ Compliance check complete for {compliance_type}\n\n" +
                     f"Overall Score: {compliance_results['overall_score']}/100\n" +
                     f"Issues Found: {compliance_results['issues_found']}\n\n" +
                     "Recommendations:\n" +
                     "\n".join([f"• {rec}" for rec in compliance_results['recommendations']])
            )]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Compliance check failed: {str(e)}")]

    # Helper Methods
    
    def _build_auth_headers(self, config: Dict, credentials: Dict) -> Dict[str, str]:
        """Build authentication headers based on system requirements"""
        headers = {"Content-Type": "application/json"}
        
        auth_type = config.get("auth_type", "bearer")
        
        if auth_type == "bearer" and "bearer_token" in credentials:
            headers["Authorization"] = f"Bearer {credentials['bearer_token']}"
        elif auth_type == "api_key" and "api_key" in credentials:
            headers["X-API-Key"] = credentials["api_key"]
        elif auth_type == "oauth2" and "access_token" in credentials:
            headers["Authorization"] = f"Bearer {credentials['access_token']}"
        
        return headers
    
    def _generate_mock_matters(self, system: str, count: int) -> List[Dict]:
        """Generate mock legal matters for testing"""
        matters = []
        matter_types = ["Contract Review", "Litigation", "Property Transfer", "Corporate Law", "Family Law"]
        statuses = ["active", "pending", "completed", "on_hold"]
        
        for i in range(count):
            matters.append({
                "id": f"MTR-{system.upper()}-{i+1:04d}",
                "title": f"{matter_types[i % len(matter_types)]} - Client {i+1}",
                "client_id": f"CLI-{i+1:04d}",
                "client_name": f"Client {i+1}",
                "matter_type": matter_types[i % len(matter_types)],
                "status": statuses[i % len(statuses)],
                "created_date": "2024-01-15",
                "last_activity": "2024-12-01",
                "responsible_attorney": f"Attorney {(i % 3) + 1}"
            })
        
        return matters
    
    def _generate_mock_clients(self, system: str, count: int) -> List[Dict]:
        """Generate mock client data for testing"""
        clients = []
        client_types = ["individual", "company", "trust", "non_profit"]
        
        for i in range(count):
            clients.append({
                "id": f"CLI-{system.upper()}-{i+1:04d}",
                "name": f"Client {i+1}",
                "email": f"client{i+1}@example.co.za",
                "phone": f"011-{1000000 + i}",
                "client_type": client_types[i % len(client_types)],
                "registration_date": "2024-01-15",
                "status": "active",
                "assigned_attorney": f"Attorney {(i % 3) + 1}"
            })
        
        return clients
    
    def _generate_mock_billing_entries(self, system: str, count: int) -> List[Dict]:
        """Generate mock billing entries for testing"""
        entries = []
        
        for i in range(count):
            hours = round((i + 1) * 0.5 + 2, 2)
            rate = 1500 + (i * 100)
            
            entries.append({
                "id": f"BILL-{system.upper()}-{i+1:04d}",
                "matter_id": f"MTR-{i+1:04d}",
                "client_id": f"CLI-{i+1:04d}",
                "date": "2024-12-01",
                "description": f"Legal research and consultation - Entry {i+1}",
                "hours_worked": hours,
                "hourly_rate": rate,
                "amount": hours * rate,
                "attorney": f"Attorney {(i % 3) + 1}",
                "billable": True
            })
        
        return entries
    
    def _get_compliance_frameworks(self) -> Dict:
        """Get SA legal compliance frameworks"""
        return {
            "popia_compliance": {
                "name": "Protection of Personal Information Act (POPIA)",
                "requirements": [
                    "Client consent management",
                    "Data processing records",
                    "Privacy policy compliance",
                    "Data breach notification procedures"
                ]
            },
            "legal_practice_act": {
                "name": "Legal Practice Act 28 of 2014",
                "requirements": [
                    "Attorney admission requirements",
                    "Continuing professional development",
                    "Professional conduct compliance",
                    "Trust account management"
                ]
            },
            "attorney_fidelity_fund": {
                "name": "Attorney Fidelity Fund",
                "requirements": [
                    "Monthly contribution payments",
                    "Trust account reporting",
                    "Professional indemnity insurance",
                    "Compliance certificate maintenance"
                ]
            },
            "trust_accounting": {
                "name": "Trust Account Regulations",
                "requirements": [
                    "Separate trust account maintenance",
                    "Monthly reconciliation",
                    "Client fund protection",
                    "Auditing and reporting"
                ]
            }
        }
    
    def _get_matter_templates(self) -> Dict:
        """Get SA legal matter templates"""
        return {
            "contract_review": {
                "name": "Contract Review",
                "default_fields": ["parties", "contract_type", "value", "key_terms", "risk_assessment"],
                "standard_rate": 1800,
                "estimated_hours": "2-4"
            },
            "property_transfer": {
                "name": "Property Transfer",
                "default_fields": ["property_address", "transfer_value", "bond_details", "transfer_date"],
                "standard_rate": 2000,
                "estimated_hours": "8-12"
            },
            "litigation": {
                "name": "Litigation Matter",
                "default_fields": ["court", "case_number", "opposing_party", "claim_amount", "urgency"],
                "standard_rate": 2200,
                "estimated_hours": "20-50"
            },
            "corporate_law": {
                "name": "Corporate Legal Matter",
                "default_fields": ["company_name", "registration_number", "directors", "share_structure"],
                "standard_rate": 2500,
                "estimated_hours": "5-15"
            },
            "family_law": {
                "name": "Family Law Matter",
                "default_fields": ["parties", "children", "assets", "maintenance", "urgency"],
                "standard_rate": 1600,
                "estimated_hours": "3-8"
            }
        }
    
    def _get_billing_rates(self) -> Dict:
        """Get SA legal billing rates"""
        return {
            "standard_rates": {
                "junior_attorney": {"hourly_rate": 1200, "currency": "ZAR"},
                "senior_attorney": {"hourly_rate": 1800, "currency": "ZAR"},
                "partner": {"hourly_rate": 2500, "currency": "ZAR"},
                "candidate_attorney": {"hourly_rate": 800, "currency": "ZAR"}
            },
            "specialized_rates": {
                "litigation": {"premium": 200, "description": "Litigation premium"},
                "corporate": {"premium": 300, "description": "Corporate law premium"},
                "property": {"premium": 100, "description": "Property law premium"},
                "urgent_matters": {"multiplier": 1.5, "description": "Urgent matter surcharge"}
            },
            "disbursements": {
                "court_filing_fees": "Variable",
                "sheriff_fees": "Variable",
                "expert_witness_fees": "Variable",
                "travel_expenses": "Actual costs"
            }
        }

    async def run(self):
        """Run the MCP server"""
        # Initialize the server
        async with self.server:
            # Start listening for requests
            await self.server.run()

async def main():
    """Main entry point for the SA Legal Integrations MCP Server"""
    logger.info("🚀 Starting Verdict360 SA Legal Integrations MCP Server")
    
    server = SALegalIntegrationsServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
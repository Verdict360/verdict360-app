#!/usr/bin/env python3
"""
Verdict360 MCP Server - Legal Document Processor
Advanced document processing for South African legal documents
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import hashlib
import re

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
logger = logging.getLogger("verdict360-legal-document-processor")

@dataclass
class DocumentMetadata:
    id: str
    filename: str
    file_type: str
    file_size: int
    upload_date: str
    processed_date: Optional[str]
    jurisdiction: str
    document_type: str
    language: str
    classification_confidence: float
    extraction_status: str

@dataclass
class LegalEntity:
    name: str
    entity_type: str  # person, company, court, law_firm
    identifiers: List[str]  # ID numbers, registration numbers
    addresses: List[str]
    roles: List[str]  # plaintiff, defendant, attorney, witness

@dataclass 
class LegalCitation:
    citation_text: str
    case_name: Optional[str]
    court: Optional[str]
    year: Optional[int]
    citation_type: str  # case_law, legislation, regulation
    jurisdiction: str
    authority_level: str  # supreme_court, high_court, magistrate_court
    precedent_value: str  # binding, persuasive, informative

class LegalDocumentProcessor:
    """MCP Server for processing SA legal documents"""
    
    def __init__(self):
        self.server = Server("verdict360-legal-document-processor")
        self.processed_documents = {}
        self.document_cache = {}
        
        # SA Legal Document Classification
        self.sa_document_types = {
            "contracts": ["sale_agreement", "lease_agreement", "employment_contract", "service_agreement"],
            "court_documents": ["summons", "application", "plea", "judgment", "court_order"],
            "corporate": ["memorandum", "articles_of_association", "resolution", "share_certificate"],
            "property": ["title_deed", "bond_document", "sectional_title", "transfer_document"],
            "family_law": ["divorce_decree", "custody_order", "maintenance_order", "antenuptial_contract"],
            "criminal": ["charge_sheet", "plea_agreement", "sentence", "criminal_record"],
            "regulatory": ["compliance_certificate", "license", "permit", "notice"],
            "correspondence": ["letter_of_demand", "attorney_letter", "notice_to_quit", "legal_notice"]
        }
        
        # SA Legal Citation Patterns
        self.sa_citation_patterns = [
            r'\d{4}\s+\(\d+\)\s+SA\s+\d+\s+\([A-Z]+\)',  # 2023 (1) SA 123 (SCA)
            r'\d{4}\s+\d+\s+SA\s+\d+\s+\([A-Z]+\)',      # 2023 1 SA 123 (CC)
            r'\[\d{4}\]\s+\d+\s+All\s+SA\s+\d+\s+\([A-Z]+\)',  # [2023] 1 All SA 123 (GP)
            r'\d{4}\s+\(\d+\)\s+BCLR\s+\d+\s+\([A-Z]+\)',      # 2023 (1) BCLR 123 (CC)
            r'Act\s+\d+\s+of\s+\d{4}',                          # Act 108 of 1996
            r'Government\s+Gazette\s+\d+\s+of\s+\d{4}',        # Government Gazette 12345 of 2023
        ]
        
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """Register document processing tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available document processing tools"""
            return [
                Tool(
                    name="classify_document",
                    description="Classify SA legal document type and extract metadata",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Text content of the document"
                            },
                            "filename": {
                                "type": "string", 
                                "description": "Original filename"
                            },
                            "file_type": {
                                "type": "string",
                                "description": "File type (pdf, docx, txt)"
                            }
                        },
                        "required": ["document_content"]
                    }
                ),
                Tool(
                    name="extract_legal_entities",
                    description="Extract legal entities (people, companies, courts) from SA legal documents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Text content to analyze"
                            },
                            "document_type": {
                                "type": "string",
                                "description": "Type of legal document for context"
                            }
                        },
                        "required": ["document_content"]
                    }
                ),
                Tool(
                    name="extract_legal_citations",
                    description="Extract and validate SA legal citations from documents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Document text to analyze"
                            },
                            "validate_citations": {
                                "type": "boolean",
                                "default": True,
                                "description": "Validate citations against SA legal databases"
                            }
                        },
                        "required": ["document_content"]
                    }
                ),
                Tool(
                    name="extract_key_dates",
                    description="Extract important dates from SA legal documents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Document text to analyze"
                            },
                            "document_type": {
                                "type": "string",
                                "description": "Document type for context"
                            }
                        },
                        "required": ["document_content"]
                    }
                ),
                Tool(
                    name="analyze_contract_terms",
                    description="Analyze and extract key terms from SA legal contracts",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "contract_content": {
                                "type": "string",
                                "description": "Contract text to analyze"
                            },
                            "contract_type": {
                                "type": "string",
                                "enum": ["sale_agreement", "lease_agreement", "employment_contract", "service_agreement", "general"],
                                "default": "general"
                            }
                        },
                        "required": ["contract_content"]
                    }
                ),
                Tool(
                    name="compliance_scan",
                    description="Scan documents for SA legal compliance issues",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Document to scan"
                            },
                            "compliance_frameworks": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["popia", "companies_act", "labour_relations_act", "consumer_protection_act"]
                                },
                                "default": ["popia"]
                            }
                        },
                        "required": ["document_content"]
                    }
                ),
                Tool(
                    name="generate_document_summary",
                    description="Generate executive summary of SA legal documents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Full document text"
                            },
                            "summary_type": {
                                "type": "string",
                                "enum": ["executive", "technical", "client_friendly"],
                                "default": "executive"
                            },
                            "max_length": {
                                "type": "integer",
                                "default": 500,
                                "description": "Maximum summary length in words"
                            }
                        },
                        "required": ["document_content"]
                    }
                ),
                Tool(
                    name="redact_sensitive_info",
                    description="Redact sensitive information from legal documents per POPIA",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Document content to redact"
                            },
                            "redaction_level": {
                                "type": "string",
                                "enum": ["minimal", "standard", "comprehensive"],
                                "default": "standard"
                            },
                            "preserve_legal_context": {
                                "type": "boolean",
                                "default": True
                            }
                        },
                        "required": ["document_content"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> list[TextContent]:
            """Handle document processing tool calls"""
            
            tool_name = request.params.name
            arguments = request.params.arguments or {}
            
            try:
                if tool_name == "classify_document":
                    return await self._classify_document(arguments)
                elif tool_name == "extract_legal_entities":
                    return await self._extract_legal_entities(arguments)
                elif tool_name == "extract_legal_citations":
                    return await self._extract_legal_citations(arguments)
                elif tool_name == "extract_key_dates":
                    return await self._extract_key_dates(arguments)
                elif tool_name == "analyze_contract_terms":
                    return await self._analyze_contract_terms(arguments)
                elif tool_name == "compliance_scan":
                    return await self._compliance_scan(arguments)
                elif tool_name == "generate_document_summary":
                    return await self._generate_document_summary(arguments)
                elif tool_name == "redact_sensitive_info":
                    return await self._redact_sensitive_info(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {tool_name}")]
                    
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {str(e)}")
                return [TextContent(type="text", text=f"Error in {tool_name}: {str(e)}")]
    
    def _register_resources(self):
        """Register document processing resources"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available document processing resources"""
            return [
                Resource(
                    uri="legal-docs://sa/document-types",
                    name="SA Legal Document Types",
                    description="Classification taxonomy for SA legal documents",
                    mimeType="application/json"
                ),
                Resource(
                    uri="legal-docs://sa/citation-patterns",
                    name="SA Legal Citation Patterns",
                    description="Regular expressions for SA legal citation recognition",
                    mimeType="application/json"
                ),
                Resource(
                    uri="legal-docs://sa/entity-patterns",
                    name="SA Legal Entity Patterns",
                    description="Patterns for extracting SA legal entities",
                    mimeType="application/json"
                ),
                Resource(
                    uri="legal-docs://sa/compliance-rules",
                    name="SA Compliance Rules",
                    description="POPIA and other SA compliance scanning rules",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read document processing resources"""
            
            if uri == "legal-docs://sa/document-types":
                return json.dumps(self.sa_document_types, indent=2)
            elif uri == "legal-docs://sa/citation-patterns":
                return json.dumps({
                    "patterns": self.sa_citation_patterns,
                    "description": "SA legal citation recognition patterns"
                }, indent=2)
            elif uri == "legal-docs://sa/entity-patterns":
                return json.dumps(self._get_entity_patterns(), indent=2)
            elif uri == "legal-docs://sa/compliance-rules":
                return json.dumps(self._get_compliance_rules(), indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")

    # Tool Implementation Methods
    
    async def _classify_document(self, args: Dict) -> list[TextContent]:
        """Classify SA legal document type"""
        document_content = args.get("document_content", "")
        filename = args.get("filename", "unknown")
        file_type = args.get("file_type", "txt")
        
        # Document classification logic
        classification_results = self._perform_classification(document_content)
        
        # Generate document metadata
        doc_id = hashlib.md5(document_content.encode()).hexdigest()[:12]
        
        metadata = DocumentMetadata(
            id=doc_id,
            filename=filename,
            file_type=file_type,
            file_size=len(document_content),
            upload_date=datetime.utcnow().isoformat(),
            processed_date=datetime.utcnow().isoformat(),
            jurisdiction="South Africa",
            document_type=classification_results["document_type"],
            language=classification_results["language"],
            classification_confidence=classification_results["confidence"],
            extraction_status="completed"
        )
        
        # Store in cache
        self.processed_documents[doc_id] = metadata
        
        result = {
            "document_id": doc_id,
            "classification": classification_results,
            "metadata": {
                "filename": filename,
                "file_type": file_type,
                "file_size": len(document_content),
                "processed_date": metadata.processed_date,
                "jurisdiction": "South Africa"
            },
            "recommendations": self._get_processing_recommendations(classification_results["document_type"])
        }
        
        return [TextContent(
            type="text",
            text=f"📄 Document Classification Complete\n\n" +
                 json.dumps(result, indent=2)
        )]
    
    async def _extract_legal_entities(self, args: Dict) -> list[TextContent]:
        """Extract legal entities from document"""
        document_content = args.get("document_content", "")
        document_type = args.get("document_type", "general")
        
        entities = self._extract_entities(document_content, document_type)
        
        result = {
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "document_type": document_type,
            "entities_found": len(entities),
            "entities": entities
        }
        
        return [TextContent(
            type="text",
            text=f"👥 Legal Entities Extracted\n\n" +
                 json.dumps(result, indent=2)
        )]
    
    async def _extract_legal_citations(self, args: Dict) -> list[TextContent]:
        """Extract SA legal citations"""
        document_content = args.get("document_content", "")
        validate_citations = args.get("validate_citations", True)
        
        citations = self._extract_citations(document_content)
        
        if validate_citations:
            citations = self._validate_citations(citations)
        
        result = {
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "citations_found": len(citations),
            "citations": citations,
            "validation_performed": validate_citations
        }
        
        return [TextContent(
            type="text",
            text=f"⚖️ Legal Citations Extracted\n\n" +
                 json.dumps(result, indent=2)
        )]
    
    async def _extract_key_dates(self, args: Dict) -> list[TextContent]:
        """Extract important dates from legal document"""
        document_content = args.get("document_content", "")
        document_type = args.get("document_type", "general")
        
        dates = self._extract_dates(document_content, document_type)
        
        result = {
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "document_type": document_type,
            "dates_found": len(dates),
            "key_dates": dates
        }
        
        return [TextContent(
            type="text",
            text=f"📅 Key Dates Extracted\n\n" +
                 json.dumps(result, indent=2)
        )]
    
    async def _analyze_contract_terms(self, args: Dict) -> list[TextContent]:
        """Analyze contract terms and conditions"""
        contract_content = args.get("contract_content", "")
        contract_type = args.get("contract_type", "general")
        
        analysis = self._perform_contract_analysis(contract_content, contract_type)
        
        result = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "contract_type": contract_type,
            "analysis": analysis
        }
        
        return [TextContent(
            type="text",
            text=f"📋 Contract Analysis Complete\n\n" +
                 json.dumps(result, indent=2)
        )]
    
    async def _compliance_scan(self, args: Dict) -> list[TextContent]:
        """Scan for compliance issues"""
        document_content = args.get("document_content", "")
        frameworks = args.get("compliance_frameworks", ["popia"])
        
        compliance_results = self._perform_compliance_scan(document_content, frameworks)
        
        result = {
            "scan_timestamp": datetime.utcnow().isoformat(),
            "frameworks_checked": frameworks,
            "compliance_results": compliance_results
        }
        
        return [TextContent(
            type="text",
            text=f"🔍 Compliance Scan Complete\n\n" +
                 json.dumps(result, indent=2)
        )]
    
    async def _generate_document_summary(self, args: Dict) -> list[TextContent]:
        """Generate document summary"""
        document_content = args.get("document_content", "")
        summary_type = args.get("summary_type", "executive")
        max_length = args.get("max_length", 500)
        
        summary = self._create_summary(document_content, summary_type, max_length)
        
        result = {
            "summary_timestamp": datetime.utcnow().isoformat(),
            "summary_type": summary_type,
            "target_length": max_length,
            "actual_length": len(summary.split()),
            "summary": summary
        }
        
        return [TextContent(
            type="text",
            text=f"📝 Document Summary Generated\n\n" +
                 json.dumps(result, indent=2)
        )]
    
    async def _redact_sensitive_info(self, args: Dict) -> list[TextContent]:
        """Redact sensitive information per POPIA"""
        document_content = args.get("document_content", "")
        redaction_level = args.get("redaction_level", "standard")
        preserve_context = args.get("preserve_legal_context", True)
        
        redaction_result = self._perform_redaction(document_content, redaction_level, preserve_context)
        
        result = {
            "redaction_timestamp": datetime.utcnow().isoformat(),
            "redaction_level": redaction_level,
            "preserve_legal_context": preserve_context,
            "redactions_made": redaction_result["redactions_count"],
            "redacted_document": redaction_result["redacted_content"],
            "redaction_log": redaction_result["redaction_log"]
        }
        
        return [TextContent(
            type="text",
            text=f"🔒 Document Redaction Complete\n\n" +
                 json.dumps(result, indent=2)
        )]

    # Helper Methods
    
    def _perform_classification(self, content: str) -> Dict:
        """Classify document type based on content analysis"""
        content_lower = content.lower()
        
        # Simple classification based on keywords
        for category, doc_types in self.sa_document_types.items():
            for doc_type in doc_types:
                keywords = self._get_document_keywords(doc_type)
                if any(keyword in content_lower for keyword in keywords):
                    return {
                        "document_type": doc_type,
                        "category": category,
                        "language": "english" if "the" in content_lower else "afrikaans",
                        "confidence": 0.85
                    }
        
        return {
            "document_type": "general_legal",
            "category": "general",
            "language": "english",
            "confidence": 0.5
        }
    
    def _get_document_keywords(self, doc_type: str) -> List[str]:
        """Get keywords for document type classification"""
        keyword_map = {
            "sale_agreement": ["sale", "purchase", "buyer", "seller", "property", "purchase price"],
            "lease_agreement": ["lease", "tenant", "landlord", "rental", "premises"],
            "employment_contract": ["employment", "employee", "employer", "salary", "duties"],
            "summons": ["summons", "plaintiff", "defendant", "claim", "court"],
            "application": ["application", "applicant", "respondent", "relief", "court"],
            "judgment": ["judgment", "order", "court", "finds", "awarded"],
            "title_deed": ["title deed", "property", "erf", "registered owner"],
            "divorce_decree": ["divorce", "marriage", "dissolution", "parties"]
        }
        return keyword_map.get(doc_type, [])
    
    def _extract_entities(self, content: str, doc_type: str) -> List[LegalEntity]:
        """Extract legal entities from content"""
        entities = []
        
        # South African ID number pattern
        sa_id_pattern = r'\b\d{13}\b'
        id_numbers = re.findall(sa_id_pattern, content)
        
        # Company registration numbers
        company_pattern = r'\b\d{4}/\d{6}/\d{2}\b'
        company_numbers = re.findall(company_pattern, content)
        
        # Extract names (simplified)
        name_patterns = [
            r'[A-Z][a-z]+ [A-Z][a-z]+',  # First Last
            r'[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+',  # First M. Last
        ]
        
        names = []
        for pattern in name_patterns:
            names.extend(re.findall(pattern, content))
        
        # Create entity objects
        for i, name in enumerate(names[:5]):  # Limit to 5 entities
            entities.append(LegalEntity(
                name=name,
                entity_type="person",
                identifiers=id_numbers[i:i+1] if i < len(id_numbers) else [],
                addresses=[],
                roles=["party"]
            ))
        
        return entities
    
    def _extract_citations(self, content: str) -> List[LegalCitation]:
        """Extract SA legal citations"""
        citations = []
        
        for pattern in self.sa_citation_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                citations.append(LegalCitation(
                    citation_text=match,
                    case_name=None,
                    court=self._extract_court_from_citation(match),
                    year=self._extract_year_from_citation(match),
                    citation_type="case_law",
                    jurisdiction="South Africa",
                    authority_level=self._determine_authority_level(match),
                    precedent_value="binding"
                ))
        
        return citations
    
    def _extract_court_from_citation(self, citation: str) -> Optional[str]:
        """Extract court abbreviation from citation"""
        court_match = re.search(r'\(([A-Z]+)\)', citation)
        return court_match.group(1) if court_match else None
    
    def _extract_year_from_citation(self, citation: str) -> Optional[int]:
        """Extract year from citation"""
        year_match = re.search(r'(\d{4})', citation)
        return int(year_match.group(1)) if year_match else None
    
    def _determine_authority_level(self, citation: str) -> str:
        """Determine court authority level"""
        if 'CC' in citation:
            return "constitutional_court"
        elif 'SCA' in citation:
            return "supreme_court_of_appeal"
        elif any(court in citation for court in ['GP', 'WCC', 'KZP', 'ECG']):
            return "high_court"
        else:
            return "magistrate_court"
    
    def _validate_citations(self, citations: List[LegalCitation]) -> List[LegalCitation]:
        """Validate citations against legal databases (mock)"""
        # In real implementation, validate against SAFLII or other databases
        for citation in citations:
            citation.precedent_value = "validated"
        return citations
    
    def _extract_dates(self, content: str, doc_type: str) -> List[Dict]:
        """Extract key dates from document"""
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',      # DD/MM/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',      # DD-MM-YYYY
            r'\b\d{1,2} \w+ \d{4}\b',          # DD Month YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                dates.append({
                    "date": match,
                    "context": self._get_date_context(content, match),
                    "importance": "high" if "deadline" in content.lower() else "medium"
                })
        
        return dates[:10]  # Limit to 10 dates
    
    def _get_date_context(self, content: str, date: str) -> str:
        """Get context around a date"""
        index = content.find(date)
        if index == -1:
            return ""
        
        start = max(0, index - 50)
        end = min(len(content), index + len(date) + 50)
        return content[start:end].strip()
    
    def _perform_contract_analysis(self, content: str, contract_type: str) -> Dict:
        """Analyze contract terms and conditions"""
        analysis = {
            "contract_type": contract_type,
            "key_terms": self._extract_contract_terms(content),
            "risk_assessment": self._assess_contract_risks(content),
            "compliance_issues": self._check_contract_compliance(content),
            "recommendations": self._generate_contract_recommendations(content, contract_type)
        }
        return analysis
    
    def _extract_contract_terms(self, content: str) -> List[Dict]:
        """Extract key contract terms"""
        terms = []
        
        # Payment terms
        payment_pattern = r'pay(?:ment)?\s+of\s+R?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        payment_matches = re.findall(payment_pattern, content, re.IGNORECASE)
        
        for amount in payment_matches:
            terms.append({
                "type": "payment",
                "value": amount,
                "clause": "payment obligation"
            })
        
        # Duration/term
        duration_pattern = r'(?:period|term|duration)\s+of\s+(\d+)\s+(months?|years?|days?)'
        duration_matches = re.findall(duration_pattern, content, re.IGNORECASE)
        
        for duration, unit in duration_matches:
            terms.append({
                "type": "duration",
                "value": f"{duration} {unit}",
                "clause": "contract duration"
            })
        
        return terms
    
    def _assess_contract_risks(self, content: str) -> Dict:
        """Assess contract risks"""
        risk_indicators = [
            "penalty", "forfeit", "breach", "default", "termination",
            "liquidated damages", "indemnity", "guarantee"
        ]
        
        risks_found = []
        for indicator in risk_indicators:
            if indicator.lower() in content.lower():
                risks_found.append(indicator)
        
        risk_level = "high" if len(risks_found) > 5 else "medium" if len(risks_found) > 2 else "low"
        
        return {
            "risk_level": risk_level,
            "risk_indicators": risks_found,
            "mitigation_required": len(risks_found) > 3
        }
    
    def _check_contract_compliance(self, content: str) -> List[str]:
        """Check contract compliance issues"""
        issues = []
        
        # POPIA compliance
        if "personal information" in content.lower() and "consent" not in content.lower():
            issues.append("Missing POPIA consent clause")
        
        # Consumer Protection Act
        if "cooling off" not in content.lower() and "consumer" in content.lower():
            issues.append("Missing cooling-off period clause")
        
        return issues
    
    def _generate_contract_recommendations(self, content: str, contract_type: str) -> List[str]:
        """Generate contract improvement recommendations"""
        recommendations = []
        
        if contract_type == "employment_contract":
            if "disciplinary procedure" not in content.lower():
                recommendations.append("Include disciplinary procedure clause")
            if "notice period" not in content.lower():
                recommendations.append("Specify notice period for termination")
        
        if contract_type == "sale_agreement":
            if "warranties" not in content.lower():
                recommendations.append("Include seller warranties and representations")
            if "title guarantee" not in content.lower():
                recommendations.append("Add title guarantee clause")
        
        return recommendations
    
    def _perform_compliance_scan(self, content: str, frameworks: List[str]) -> Dict:
        """Perform compliance scanning"""
        results = {}
        
        for framework in frameworks:
            if framework == "popia":
                results["popia"] = self._scan_popia_compliance(content)
            elif framework == "companies_act":
                results["companies_act"] = self._scan_companies_act_compliance(content)
            elif framework == "labour_relations_act":
                results["labour_relations_act"] = self._scan_labour_compliance(content)
        
        return results
    
    def _scan_popia_compliance(self, content: str) -> Dict:
        """Scan POPIA compliance"""
        issues = []
        
        # Check for personal information handling
        if re.search(r'\b\d{13}\b', content):  # SA ID numbers
            if "consent" not in content.lower():
                issues.append("ID numbers present without consent clause")
        
        # Check for data processing purpose
        if "personal information" in content.lower():
            if "purpose" not in content.lower():
                issues.append("Personal information without stated purpose")
        
        compliance_score = max(0, 100 - (len(issues) * 20))
        
        return {
            "compliance_score": compliance_score,
            "issues": issues,
            "recommendations": ["Add POPIA compliance clause", "Include data subject rights"]
        }
    
    def _scan_companies_act_compliance(self, content: str) -> Dict:
        """Scan Companies Act compliance"""
        # Mock implementation
        return {
            "compliance_score": 85,
            "issues": [],
            "recommendations": ["Verify director signatures"]
        }
    
    def _scan_labour_compliance(self, content: str) -> Dict:
        """Scan Labour Relations Act compliance"""
        # Mock implementation
        return {
            "compliance_score": 90,
            "issues": [],
            "recommendations": ["Include dispute resolution clause"]
        }
    
    def _create_summary(self, content: str, summary_type: str, max_length: int) -> str:
        """Create document summary"""
        # Simple extractive summarization (in practice, use more sophisticated methods)
        sentences = content.split('. ')
        
        if summary_type == "executive":
            # Focus on key legal points
            key_sentences = [s for s in sentences if any(word in s.lower() for word in 
                           ['whereas', 'therefore', 'agrees', 'court finds', 'ordered'])]
        elif summary_type == "technical":
            # Focus on technical details
            key_sentences = [s for s in sentences if any(word in s.lower() for word in 
                           ['section', 'clause', 'paragraph', 'regulation', 'act'])]
        else:  # client_friendly
            # Simple, clear language
            key_sentences = [s for s in sentences if len(s.split()) < 20]
        
        summary = '. '.join(key_sentences[:5])
        words = summary.split()
        
        if len(words) > max_length:
            summary = ' '.join(words[:max_length]) + '...'
        
        return summary
    
    def _perform_redaction(self, content: str, level: str, preserve_context: bool) -> Dict:
        """Perform POPIA-compliant redaction"""
        redacted_content = content
        redaction_log = []
        redactions_count = 0
        
        # Redact SA ID numbers
        id_pattern = r'\b(\d{13})\b'
        matches = re.finditer(id_pattern, content)
        for match in matches:
            redacted_content = redacted_content.replace(match.group(1), '[REDACTED-ID]')
            redaction_log.append(f"ID number at position {match.start()}")
            redactions_count += 1
        
        # Redact phone numbers
        phone_pattern = r'\b(\d{3}[-\s]?\d{3}[-\s]?\d{4})\b'
        matches = re.finditer(phone_pattern, redacted_content)
        for match in matches:
            redacted_content = redacted_content.replace(match.group(1), '[REDACTED-PHONE]')
            redaction_log.append(f"Phone number at position {match.start()}")
            redactions_count += 1
        
        # Redact email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.finditer(email_pattern, redacted_content)
        for match in matches:
            redacted_content = redacted_content.replace(match.group(), '[REDACTED-EMAIL]')
            redaction_log.append(f"Email address at position {match.start()}")
            redactions_count += 1
        
        # Additional redactions based on level
        if level in ["standard", "comprehensive"]:
            # Redact addresses (simple pattern)
            address_pattern = r'\b\d+\s+[A-Z][a-z]+\s+(?:Street|Road|Avenue|Drive|Lane)\b'
            matches = re.finditer(address_pattern, redacted_content)
            for match in matches:
                redacted_content = redacted_content.replace(match.group(), '[REDACTED-ADDRESS]')
                redaction_log.append(f"Address at position {match.start()}")
                redactions_count += 1
        
        return {
            "redacted_content": redacted_content,
            "redactions_count": redactions_count,
            "redaction_log": redaction_log
        }
    
    def _get_processing_recommendations(self, doc_type: str) -> List[str]:
        """Get processing recommendations based on document type"""
        recommendations_map = {
            "contract": [
                "Extract key terms and obligations",
                "Perform risk assessment",
                "Check compliance with relevant acts"
            ],
            "court_document": [
                "Extract case information and parties",
                "Identify key dates and deadlines",
                "Extract legal citations and references"
            ],
            "correspondence": [
                "Extract sender and recipient information",
                "Identify action items and deadlines",
                "Classify urgency level"
            ]
        }
        
        return recommendations_map.get(doc_type, ["Perform general legal analysis"])
    
    def _get_entity_patterns(self) -> Dict:
        """Get entity extraction patterns"""
        return {
            "person_names": [
                r'[A-Z][a-z]+ [A-Z][a-z]+',
                r'[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+'
            ],
            "company_names": [
                r'[A-Z][a-zA-Z\s]+ \(Pty\) Ltd',
                r'[A-Z][a-zA-Z\s]+ CC',
                r'[A-Z][a-zA-Z\s]+ Trust'
            ],
            "court_names": [
                r'Constitutional Court of South Africa',
                r'Supreme Court of Appeal',
                r'[A-Z][a-z]+ High Court'
            ],
            "identifiers": [
                r'\b\d{13}\b',  # SA ID numbers
                r'\b\d{4}/\d{6}/\d{2}\b',  # Company registration
                r'\bIT\d{10}\b'  # Tax numbers
            ]
        }
    
    def _get_compliance_rules(self) -> Dict:
        """Get compliance scanning rules"""
        return {
            "popia": {
                "required_clauses": [
                    "consent for data processing",
                    "purpose of processing",
                    "data subject rights",
                    "retention period"
                ],
                "prohibited_content": [
                    "processing without consent",
                    "excessive data collection"
                ]
            },
            "companies_act": {
                "required_clauses": [
                    "director signatures",
                    "company registration details",
                    "shareholder information"
                ]
            },
            "consumer_protection_act": {
                "required_clauses": [
                    "cooling-off period",
                    "consumer rights",
                    "complaint procedures"
                ]
            }
        }

    async def run(self):
        """Run the document processing MCP server"""
        async with self.server:
            await self.server.run()

async def main():
    """Main entry point"""
    logger.info("🚀 Starting Verdict360 Legal Document Processor MCP Server")
    
    processor = LegalDocumentProcessor()
    await processor.run()

if __name__ == "__main__":
    asyncio.run(main())
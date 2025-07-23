"""
Demo AI Service for Legal Chat Responses
Provides realistic legal responses for demonstration purposes
"""

import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DemoAIService:
    """Demo AI service for generating realistic legal responses"""
    
    def __init__(self):
        self.legal_responses = {
            # Criminal law responses
            r'criminal|arrest|bail|court|charge|prison|jail|police': {
                'response': """Based on South African criminal law, I can provide general guidance on your criminal law matter.

**Key Points:**
• You have constitutional rights under the Bill of Rights in Chapter 2 of the Constitution
• The right to remain silent (Section 35 of the Constitution)
• The right to legal representation
• The right to be presumed innocent until proven guilty

**Immediate Steps:**
1. Exercise your right to remain silent until you have legal representation
2. Contact a qualified criminal defense attorney immediately
3. Do not sign any documents without legal advice
4. Ensure all your constitutional rights are protected

**Important Legal Citations:**
• Constitution of South Africa, 1996 - Chapter 2 (Bill of Rights)
• Criminal Procedure Act 51 of 1977
• Constitutional Court cases on criminal rights

*Please note: This is general information only. Criminal matters are serious and require immediate professional legal assistance. Contact a qualified criminal defense attorney in your area.*

Would you like me to help you understand more about specific criminal law procedures or assist with finding legal representation?""",
                'legal_area': 'Criminal Law',
                'urgency': 'High'
            },
            
            # Family law responses
            r'divorce|custody|maintenance|alimony|marriage|spouse|children': {
                'response': """Regarding your family law matter, South African family law provides specific protections and procedures.

**Family Law Framework:**
• Divorce Act 70 of 1979 governs divorce proceedings
• Children's Act 38 of 2005 protects children's rights and interests
• Maintenance Act 99 of 1998 covers spousal and child support

**Common Procedures:**
1. **Divorce:** No-fault divorce available after irretrievable breakdown of marriage
2. **Child Custody:** Courts prioritize the best interests of the child
3. **Maintenance:** Both parents have obligation to support children financially
4. **Property Division:** Depends on your marriage regime (in/out of community of property)

**Required Steps:**
• Gather all relevant documentation (marriage certificate, financial records)
• Consider mediation for amicable resolution
• Consult with a family law attorney
• Prepare for possible court proceedings

**Legal Citations:**
• Divorce Act 70 of 1979
• Children's Act 38 of 2005
• Matrimonial Property Act 88 of 1984

*Important: Family law matters significantly impact your future and your children's wellbeing. Professional legal advice is essential.*

Would you like information about specific aspects of family law or help finding a qualified family law attorney?""",
                'legal_area': 'Family Law',
                'urgency': 'Normal'
            },
            
            # Commercial/business law
            r'business|company|contract|commercial|employment|work|labour': {
                'response': """I can assist with your commercial law inquiry under South African business legislation.

**Commercial Law Overview:**
• Companies Act 71 of 2008 governs company formation and operations
• Labour Relations Act 66 of 1995 covers employment matters
• Basic Conditions of Employment Act 75 of 1997 sets minimum employment standards

**Key Business Considerations:**
1. **Company Formation:** Choose appropriate business structure (Pty Ltd, CC, etc.)
2. **Contracts:** Ensure all agreements comply with SA contract law
3. **Employment Law:** Follow CCMA procedures and labour legislation
4. **Tax Compliance:** Register for VAT, PAYE, and other tax obligations

**Important Compliance Areas:**
• BEE (Broad-Based Black Economic Empowerment) requirements
• Skills Development Act compliance
• Occupational Health and Safety Act requirements
• Consumer Protection Act compliance

**Legal Framework:**
• Companies Act 71 of 2008
• Labour Relations Act 66 of 1995
• Consumer Protection Act 68 of 2008

*Note: Business law is complex and non-compliance can result in significant penalties. Professional legal advice is recommended for all commercial matters.*

Would you like more specific information about business registration, employment law, or commercial contracts?""",
                'legal_area': 'Commercial Law',
                'urgency': 'Normal'
            },
            
            # Property law
            r'property|house|buying|selling|transfer|bond|mortgage|lease|rent': {
                'response': """Regarding your property law matter, South African property law has specific requirements and procedures.

**Property Law Framework:**
• Deeds Registries Act 47 of 1937 governs property registration
• Alienation of Land Act 68 of 1981 covers property sales
• Property valuers Act and related legislation

**Property Transaction Process:**
1. **Sale Agreement:** Must be in writing and signed by both parties
2. **Bond Application:** If financing is required
3. **Transfer Process:** Handled by conveyancing attorney
4. **Registration:** At the relevant Deeds Office

**Key Requirements:**
• All property transfers must be registered at a Deeds Office
• Use of a conveyancing attorney is mandatory for transfers
• Various certificates required (rates clearance, electrical compliance, etc.)
• Transfer duty or VAT may be payable

**Important Considerations:**
• Voetstoots clauses and property condition
• Municipal rates and taxes
• Body corporate rules (for sectional title properties)
• Zoning and land use restrictions

**Legal Citations:**
• Deeds Registries Act 47 of 1937
• Alienation of Land Act 68 of 1981
• Transfer Duty Act 40 of 1949

*Property transactions involve significant financial and legal implications. Always use qualified conveyancing attorneys.*

Would you like information about specific aspects of property law or assistance with the property transfer process?""",
                'legal_area': 'Property Law',
                'urgency': 'Normal'
            }
        }
        
        # Default responses for general inquiries
        self.general_responses = [
            """Thank you for your legal inquiry. I'm here to provide general guidance on South African law.

Based on your question, I recommend:

1. **Immediate Action:** Gather all relevant documentation related to your legal matter
2. **Professional Consultation:** Schedule a consultation with a qualified South African attorney who specializes in your area of legal need
3. **Know Your Rights:** Understand your constitutional and legal rights under South African law
4. **Time Sensitivity:** Be aware of any statutory time limits that may apply to your situation

**Important Legal Resources:**
• South African Law Reform Commission
• Legal Aid South Africa (for qualifying individuals)
• Provincial Law Societies for attorney referrals
• Constitutional Court and Supreme Court of Appeal judgments

*This information is for general guidance only. For specific legal advice tailored to your situation, please consult with a qualified attorney.*

Would you like me to provide more specific information about any particular area of South African law?""",
            
            """I understand you're seeking legal guidance. Let me provide some general information about South African law that may be helpful.

**South African Legal System:**
• Based on Roman-Dutch law with English law influences
• Constitutional supremacy under the 1996 Constitution
• Courts hierarchy from Magistrates' Courts to Constitutional Court
• Both civil and criminal law jurisdictions

**Getting Legal Help:**
1. Identify the specific area of law involved in your matter
2. Consult the relevant professional body or law society
3. Consider Legal Aid if you qualify for assistance
4. Prepare all relevant documentation before your consultation

**Your Constitutional Rights:**
All South Africans have fundamental rights protected by the Constitution, including:
• Right to equality and dignity
• Right to access to courts and legal representation
• Right to administrative justice
• Right to property protection

*Remember: While I can provide general information, specific legal matters require professional legal advice from qualified practitioners.*

Is there a specific area of South African law you'd like to know more about?"""
        ]

    async def generate_response(
        self, 
        message: str, 
        context: List[Dict] = None,
        conversation_history: str = "",
        legal_matter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a realistic legal response for demo purposes"""
        
        try:
            message_lower = message.lower().strip()
            
            # Check for specific legal areas
            for pattern, response_data in self.legal_responses.items():
                if re.search(pattern, message_lower):
                    return {
                        'content': response_data['response'],
                        'legal_area': response_data['legal_area'],
                        'urgency': response_data['urgency'],
                        'confidence': 0.85,
                        'sources': self._get_demo_sources(response_data['legal_area']),
                        'legal_citations': self._extract_citations(response_data['response'])
                    }
            
            # Emergency/urgent matters
            if any(word in message_lower for word in ['emergency', 'urgent', 'help', 'crisis']):
                return {
                    'content': self._get_emergency_response(),
                    'legal_area': 'Emergency Legal Matter',
                    'urgency': 'Critical',
                    'confidence': 0.90,
                    'sources': [],
                    'legal_citations': []
                }
            
            # Consultation booking requests
            if any(word in message_lower for word in ['consultation', 'appointment', 'meeting', 'book']):
                return {
                    'content': self._get_consultation_response(),
                    'legal_area': 'Consultation Booking',
                    'urgency': 'Normal',
                    'confidence': 0.95,
                    'sources': [],
                    'legal_citations': []
                }
            
            # General legal inquiry
            import random
            general_response = random.choice(self.general_responses)
            
            return {
                'content': general_response,
                'legal_area': 'General Legal Inquiry',
                'urgency': 'Normal',
                'confidence': 0.75,
                'sources': self._get_general_sources(),
                'legal_citations': self._extract_citations(general_response)
            }
            
        except Exception as e:
            logger.error(f"Error generating demo response: {str(e)}")
            return self._get_error_response()

    def _get_emergency_response(self) -> str:
        return """**EMERGENCY LEGAL MATTER DETECTED**

If this is a genuine legal emergency, please:

🚨 **Immediate Actions:**
1. **Life/Safety First:** If someone is in immediate danger, contact emergency services (10111)
2. **Legal Emergency:** Contact the after-hours legal hotline or emergency legal services
3. **Document Everything:** Preserve all evidence and documentation
4. **Legal Representation:** Contact a qualified attorney immediately

**Emergency Legal Contacts:**
• Legal Aid South Africa: 0800 110 110
• After-hours attorney services in your area
• Relevant professional law society emergency contacts

**Constitutional Rights:**
You have the right to legal representation and to remain silent until you have legal advice.

**Critical Legal Areas Requiring Immediate Attention:**
• Arrest or detention
• Court appearance deadlines
• Urgent court interdicts
• Family violence or protection orders
• Emergency custody matters

*This is an emergency protocol response. For specific legal advice, contact a qualified attorney immediately.*

Would you like help finding emergency legal representation in your area?"""

    def _get_consultation_response(self) -> str:
        return """I'd be happy to help you schedule a legal consultation.

**Consultation Booking Process:**
1. **Identify Your Legal Need:** What type of legal matter requires attention?
2. **Gather Documentation:** Prepare all relevant documents and information
3. **Choose Attorney Type:** Find an attorney who specializes in your legal area
4. **Schedule Appointment:** Contact the attorney's office directly

**What to Prepare:**
• Brief summary of your legal issue
• All relevant documentation
• List of questions you want to ask
• Information about deadlines or time constraints

**Types of Legal Consultations Available:**
• **Initial Consultation:** Usually 30-60 minutes to assess your case
• **Follow-up Consultation:** For ongoing matters
• **Emergency Consultation:** For urgent legal matters
• **Second Opinion:** If you want another attorney's perspective

**Professional Legal Areas:**
• Criminal Law • Family Law • Commercial Law
• Property Law • Labour Law • Civil Litigation
• Immigration Law • Estate Planning

**Next Steps:**
1. I can help you identify the right type of attorney for your needs
2. Provide guidance on what to expect during your consultation
3. Explain your rights and legal options

Would you like me to help you determine what type of legal consultation you need, or do you have specific questions about the consultation process?"""

    def _get_demo_sources(self, legal_area: str) -> List[Dict]:
        """Get demo legal sources for different areas"""
        sources_map = {
            'Criminal Law': [
                {
                    'title': 'Constitution of South Africa - Chapter 2 (Bill of Rights)',
                    'citation': 'Constitution of the Republic of South Africa, 1996',
                    'excerpt': 'Everyone has the right to a fair trial, including the right to be presumed innocent, to remain silent, and to choose and be represented by a legal practitioner...',
                    'relevance_score': 0.95
                },
                {
                    'title': 'Criminal Procedure Act',
                    'citation': 'Criminal Procedure Act 51 of 1977',
                    'excerpt': 'Provides the framework for criminal proceedings in South African courts, including arrest procedures, bail applications...',
                    'relevance_score': 0.90
                }
            ],
            'Family Law': [
                {
                    'title': 'Divorce Act',
                    'citation': 'Divorce Act 70 of 1979',
                    'excerpt': 'A court may grant a decree of divorce on the ground of the irretrievable breakdown of a marriage...',
                    'relevance_score': 0.92
                },
                {
                    'title': 'Children\'s Act',
                    'citation': 'Children\'s Act 38 of 2005',
                    'excerpt': 'The best interests of the child are of paramount importance in every matter concerning the child...',
                    'relevance_score': 0.88
                }
            ]
        }
        
        return sources_map.get(legal_area, [])

    def _get_general_sources(self) -> List[Dict]:
        """Get general legal sources"""
        return [
            {
                'title': 'Constitution of South Africa',
                'citation': 'Constitution of the Republic of South Africa, 1996',
                'excerpt': 'The Constitution is the supreme law of South Africa and provides the framework for all other laws...',
                'relevance_score': 0.80
            }
        ]

    def _extract_citations(self, content: str) -> List[str]:
        """Extract legal citations from response content"""
        citation_patterns = [
            r'Act \d+ of \d{4}',
            r'Constitution of.*\d{4}',
            r'Section \d+.*Constitution',
            r'Chapter \d+.*Constitution'
        ]
        
        citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, content)
            citations.extend(matches)
        
        return list(set(citations))  # Remove duplicates

    def _get_error_response(self) -> Dict[str, Any]:
        """Return error response for demo"""
        return {
            'content': """I apologize, but I'm experiencing technical difficulties processing your legal inquiry.

**Alternative Options:**
• Please try rephrasing your question
• Contact our support team directly
• Schedule a consultation with a qualified attorney

**Emergency Legal Matters:**
If this is urgent, please contact Legal Aid South Africa at 0800 110 110 or your local attorney immediately.

*Technical issues are being resolved. Thank you for your patience.*""",
            'legal_area': 'Technical Error',
            'urgency': 'Normal',
            'confidence': 0.0,
            'sources': [],
            'legal_citations': []
        }

# Global instance for use in endpoints
demo_ai_service = DemoAIService()
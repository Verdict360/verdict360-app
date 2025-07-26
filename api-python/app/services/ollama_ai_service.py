"""
Ollama AI Service for Legal Chat Responses
Integrates with local Ollama instance running Llama models for real legal AI responses
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

class OllamaAIService:
    """AI service using local Ollama instance for legal responses"""
    
    def __init__(self, model_name: str = "llama3.2:latest", base_url: str = None):
        import os
        if base_url is None:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = model_name
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)  # 2 minute timeout for AI responses
        
        # Legal context and system prompts
        self.system_prompt = """You are a helpful legal information assistant providing general information about South African law and legal processes. You help website visitors understand legal procedures and direct them to appropriate legal resources.

You provide educational information about:
- South African legal system and procedures
- Different areas of law (criminal, family, commercial, property)
- Legal processes and what to expect
- Constitutional rights and protections
- Legal resources and where to find help

You are educational and informative, similar to how a law library assistant or legal information website would provide general guidance.

CONVERSATIONAL APPROACH:
- Greet visitors warmly and ask how you can help with their legal concerns
- Listen to their situation and provide helpful information about legal processes
- Explain South African legal procedures in plain language
- Be supportive and understanding of their concerns
- Guide them toward getting professional legal help when appropriate

RESPONSE EXAMPLES:

For greetings:
User: "Hi"  
You: "Hello! I'm here to provide information about South African law and legal processes. What legal topic would you like to learn about?"

For legal questions:
User: "I'm having a dispute with my employer"
You: "Employment disputes in South Africa are typically handled through the CCMA (Commission for Conciliation, Mediation and Arbitration). The process usually involves conciliation first, then arbitration if needed. Employees have rights under the Labour Relations Act and Basic Conditions of Employment Act. For specific cases, consulting with an employment attorney is often recommended to understand your options fully."

LANGUAGE AND CURRENCY STANDARDS:
- Use British/South African English spelling exclusively (customise not customize, analyse not analyze, colour not color, licence not license, centre not center, organised not organized)
- All monetary amounts must be in South African Rand (ZAR) using format: R2,500 or R25,000 (never $ or USD)
- Use South African legal terminology and professional titles correctly
- Maintain consistent British English throughout all responses

CONVERSATION EXAMPLES:

For greetings:
User: "Hi" / "Hello" / "Hey there"
Response: "Hello! Welcome to [FIRM_NAME]. I'm here to help with any legal questions or concerns you might have. What brings you here today?"

User: "Good morning"
Response: "Good morning! I hope you're having a wonderful day. I'm here to assist with legal matters. Is there something specific I can help you with?"

For general inquiries:
User: "I need help"
Response: "Of course! I'd be happy to help you. Our firm specialises in a wide range of legal areas. What type of legal matter are you dealing with?"

PROFESSIONAL GUIDANCE:
When someone could benefit from attorney services, naturally mention:
- "Our attorneys have experience with these types of matters"
- "This might be a situation where legal representation could be helpful"
- "Many clients in similar situations have found it beneficial to speak with an attorney"
- "Our legal team is available to discuss this further if you'd like"

RESPONSE FORMAT:
End responses with these options for further assistance:
[SCHEDULE_CONSULTATION] [CONTACT_FIRM]

SOUTH AFRICAN LEGAL CONTEXT:
- Legal system based on Roman-Dutch law with English law influences
- Constitution of South Africa, 1996 is the supreme law
- Court hierarchy: Magistrates' Courts, High Courts, Supreme Court of Appeal, Constitutional Court
- Major legal areas: Constitutional, Criminal, Civil, Commercial, Family, Property, Labour, Administrative law

FORMAT YOUR RESPONSES WITH:
1. Direct answer to the legal question
2. Relevant legal framework/citations
3. Practical next steps
4. Professional disclaimer
5. Offer for further assistance

Remember: Provide general legal guidance, not specific legal advice. Always recommend consulting with qualified attorneys for specific legal matters."""

    async def generate_response(
        self, 
        message: str, 
        context: List[Dict] = None,
        conversation_history: str = "",
        legal_matter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate AI response using Ollama"""
        
        try:
            # Build comprehensive prompt with legal context
            full_prompt = await self._build_legal_prompt(
                user_message=message,
                context=context or [],
                conversation_history=conversation_history,
                legal_matter=legal_matter
            )
            
            logger.info(f"Generating AI response for legal query: {message[:100]}...")
            
            # Call Ollama API
            ai_response = await self._call_ollama(full_prompt)
            
            # Process and validate response
            processed_response = await self._process_legal_response(ai_response, message)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return await self._get_fallback_response(message)

    async def _build_legal_prompt(
        self,
        user_message: str,
        context: List[Dict],
        conversation_history: str,
        legal_matter: Optional[str]
    ) -> str:
        """Build comprehensive legal prompt for the AI"""
        
        # Check if this is a greeting
        greeting_context = await self._detect_greeting(user_message)
        
        # Extract legal context from vector search results
        context_str = ""
        if context:
            context_str = "\n\nRELEVANT LEGAL CONTEXT:\n"
            for i, item in enumerate(context[:3], 1):
                context_str += f"{i}. {item.get('title', 'Legal Document')}\n"
                context_str += f"   Citation: {item.get('citation', 'N/A')}\n"
                context_str += f"   Content: {item.get('excerpt', item.get('content', ''))[:200]}...\n\n"
        
        # Include conversation history if available
        history_str = ""
        if conversation_history:
            history_str = f"\n\nPREVIOUS CONVERSATION CONTEXT:\n{conversation_history}\n"
        
        # Legal matter context
        matter_str = ""
        if legal_matter:
            matter_str = f"\n\nLEGAL MATTER TYPE: {legal_matter}\n"
        
        # Determine urgency and special handling
        urgency_context = ""
        if any(word in user_message.lower() for word in ['emergency', 'urgent', 'arrest', 'court date', 'deadline']):
            urgency_context = "\n\nURGENT MATTER DETECTED: This appears to be time-sensitive. Emphasize immediate professional legal assistance.\n"
        
        # Build complete prompt
        full_prompt = f"""{self.system_prompt}

{greeting_context}{context_str}{history_str}{matter_str}{urgency_context}

USER QUESTION: {user_message}

Please provide a comprehensive, professional legal response following the format guidelines above."""
        
        return full_prompt

    async def _call_ollama(self, prompt: str) -> str:
        """Make API call to Ollama"""
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent legal responses
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 1500,  # Longer responses for comprehensive legal guidance
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            result = response.json()
            ai_response = result.get('response', '').strip()
            
            if not ai_response:
                raise Exception("Empty response from Ollama")
            
            logger.info(f"Generated AI response ({len(ai_response)} chars)")
            return ai_response
            
        except Exception as e:
            logger.error(f"Ollama API call failed: {str(e)}")
            raise

    async def _process_legal_response(self, ai_response: str, original_query: str) -> Dict[str, Any]:
        """Process and validate AI response for legal appropriateness"""
        
        # Validate and correct language standards
        corrected_response = await self._validate_sa_english(ai_response)
        
        # Add conversion buttons to every response
        final_response = await self._add_conversion_buttons(corrected_response)
        
        # Analyze response for legal area classification
        legal_area = await self._classify_legal_area(original_query, final_response)
        
        # Determine urgency level
        urgency = await self._assess_urgency(original_query, final_response)
        
        # Calculate confidence score based on response quality
        confidence = await self._calculate_confidence(final_response)
        
        # Extract any legal citations mentioned
        legal_citations = await self._extract_legal_citations(final_response)
        
        # Generate sources (for now, use local legal knowledge base)
        sources = await self._generate_legal_sources(legal_area)
        
        return {
            'content': final_response,
            'legal_area': legal_area,
            'urgency': urgency,
            'confidence': confidence,
            'legal_citations': legal_citations,
            'sources': sources,
            'model_used': self.model_name,
            'timestamp': datetime.utcnow().isoformat(),
            'has_conversion_buttons': True  # Flag for widget to render buttons
        }

    async def _classify_legal_area(self, query: str, response: str) -> str:
        """Classify the legal area based on query and response"""
        
        classifications = {
            'criminal': ['criminal', 'arrest', 'bail', 'court', 'charge', 'police', 'rights', 'detention'],
            'family': ['divorce', 'custody', 'maintenance', 'marriage', 'spouse', 'children', 'alimony'],
            'commercial': ['business', 'company', 'contract', 'commercial', 'employment', 'labour'],
            'property': ['property', 'house', 'buying', 'selling', 'transfer', 'bond', 'lease', 'rent'],
            'civil': ['civil', 'litigation', 'damages', 'dispute', 'claim', 'personal injury'],
            'constitutional': ['constitutional', 'rights', 'bill of rights', 'equality', 'dignity'],
            'administrative': ['administrative', 'government', 'public', 'municipal', 'licensing']
        }
        
        query_lower = (query + ' ' + response).lower()
        
        for area, keywords in classifications.items():
            if any(keyword in query_lower for keyword in keywords):
                return area.title() + ' Law'
        
        return 'General Legal Inquiry'

    async def _assess_urgency(self, query: str, response: str) -> str:
        """Assess urgency level of the legal matter"""
        
        critical_keywords = ['emergency', 'urgent', 'arrest', 'detention', 'court date', 'deadline', 'eviction']
        high_keywords = ['criminal', 'bail', 'custody', 'restraining order', 'foreclosure']
        
        text_lower = (query + ' ' + response).lower()
        
        if any(keyword in text_lower for keyword in critical_keywords):
            return 'Critical'
        elif any(keyword in text_lower for keyword in high_keywords):
            return 'High'
        else:
            return 'Normal'

    async def _calculate_confidence(self, response: str) -> float:
        """Calculate confidence score based on response quality indicators"""
        
        confidence = 0.7  # Base confidence
        
        # Boost confidence for legal indicators
        if 'Constitution' in response:
            confidence += 0.05
        if 'Act' in response and any(char.isdigit() for char in response):
            confidence += 0.05
        if 'legal advice' in response or 'attorney' in response:
            confidence += 0.05
        if len(response) > 300:  # Comprehensive response
            confidence += 0.05
        if 'South Africa' in response:
            confidence += 0.05
        
        return min(confidence, 0.95)  # Cap at 95%

    async def _extract_legal_citations(self, response: str) -> List[str]:
        """Extract legal citations from the response"""
        
        import re
        citations = []
        
        # Common SA legal citation patterns
        patterns = [
            r'Constitution of.*?\d{4}',
            r'Act \d+ of \d{4}',
            r'Section \d+.*?Constitution',
            r'Chapter \d+.*?Constitution',
            r'\d{4} \(\d+\) SA \d+',  # Case citations
            r'Criminal Procedure Act.*?\d+',
            r'Companies Act.*?\d+',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            citations.extend(matches)
        
        return list(set(citations))  # Remove duplicates

    async def _generate_legal_sources(self, legal_area: str) -> List[Dict]:
        """Generate relevant legal sources based on legal area"""
        
        sources_map = {
            'Criminal Law': [
                {
                    'title': 'Constitution of South Africa - Chapter 2',
                    'citation': 'Constitution of the Republic of South Africa, 1996',
                    'relevance_score': 0.95
                },
                {
                    'title': 'Criminal Procedure Act',
                    'citation': 'Criminal Procedure Act 51 of 1977',
                    'relevance_score': 0.90
                }
            ],
            'Family Law': [
                {
                    'title': 'Divorce Act',
                    'citation': 'Divorce Act 70 of 1979',
                    'relevance_score': 0.92
                },
                {
                    'title': 'Children\'s Act',
                    'citation': 'Children\'s Act 38 of 2005',
                    'relevance_score': 0.88
                }
            ]
        }
        
        return sources_map.get(legal_area, [
            {
                'title': 'Constitution of South Africa',
                'citation': 'Constitution of the Republic of South Africa, 1996',
                'relevance_score': 0.80
            }
        ])

    async def _get_fallback_response(self, message: str) -> Dict[str, Any]:
        """Generate fallback response when AI fails"""
        
        return {
            'content': f"""I apologise, but I'm experiencing technical difficulties processing your legal enquiry about "{message[:100]}...".

**However, our expert attorneys are immediately available to help you!**

Don't let a technical issue delay getting the legal assistance you need. Our qualified legal team can provide personalised guidance for your specific situation.

**For urgent legal matters:** Contact Legal Aid South Africa at 0800 110 110

---

**Get direct access to our legal experts:**

Our experienced attorneys specialise in South African law and are ready to review your case personally. Don't wait - schedule your consultation now.

[SCHEDULE_CONSULTATION] [CONTACT_FIRM]""",
            'legal_area': 'Technical Error',
            'urgency': 'Normal',
            'confidence': 0.0,
            'legal_citations': [],
            'sources': [],
            'model_used': 'fallback',
            'timestamp': datetime.utcnow().isoformat(),
            'has_conversion_buttons': True
        }

    async def test_connection(self) -> bool:
        """Test connection to Ollama service"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection test failed: {str(e)}")
            return False

    async def list_available_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []

    async def _validate_sa_english(self, content: str) -> str:
        """Validate and correct South African English spelling and currency"""
        
        # Common American to British English corrections
        corrections = {
            # Spelling corrections
            'customize': 'customise',
            'customized': 'customised',
            'customizing': 'customising',
            'analyze': 'analyse',
            'analyzed': 'analysed',
            'analyzing': 'analysing',
            'organize': 'organise',
            'organized': 'organised',
            'organizing': 'organising',
            'realize': 'realise',
            'realized': 'realised',
            'realizing': 'realising',
            'recognize': 'recognise',
            'recognized': 'recognised',
            'recognizing': 'recognising',
            'specialize': 'specialise',
            'specialized': 'specialised',
            'specializing': 'specialising',
            'optimize': 'optimise',
            'optimized': 'optimised',
            'optimizing': 'optimising',
            'center': 'centre',
            'centers': 'centres',
            'centered': 'centred',
            'color': 'colour',
            'colors': 'colours',
            'colored': 'coloured',
            'behavior': 'behaviour',
            'behaviors': 'behaviours',
            'favor': 'favour',
            'favors': 'favours',
            'favored': 'favoured',
            'honor': 'honour',
            'honored': 'honoured',
            'honors': 'honours',
            'license': 'licence',  # when used as noun
            'inquiry': 'enquiry',
            'inquiries': 'enquiries',
            'apologize': 'apologise',
            'apologized': 'apologised',
            'apologizing': 'apologising',
        }
        
        corrected = content
        
        # Apply word-boundary corrections for exact matches
        import re
        for american, british in corrections.items():
            # Word boundary replacement
            pattern = r'\b' + re.escape(american) + r'\b'
            corrected = re.sub(pattern, british, corrected, flags=re.IGNORECASE)
        
        # Currency corrections - convert $ to R
        corrected = re.sub(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', r'R\1', corrected)
        corrected = corrected.replace('USD', 'ZAR')
        corrected = corrected.replace(' dollars', ' rand')
        corrected = corrected.replace(' dollar', ' rand')
        
        return corrected

    async def _add_conversion_buttons(self, content: str) -> str:
        """Add schedule/contact buttons to AI response for client conversion"""
        
        # Check if buttons are already present to avoid duplication
        if '[SCHEDULE_CONSULTATION]' in content or '[CONTACT_FIRM]' in content:
            return content
        
        # Add compelling call-to-action with buttons
        button_section = """

---

**Ready to get expert legal help?**

Our experienced attorneys are standing by to review your case and provide professional guidance. Don't wait - legal matters require prompt attention.

[SCHEDULE_CONSULTATION] [CONTACT_FIRM]"""
        
        return content + button_section

    async def _detect_greeting(self, user_message: str) -> str:
        """Detect if user message is a greeting and provide appropriate context"""
        
        message_lower = user_message.lower().strip()
        
        # Common greetings
        greetings = [
            'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
            'morning', 'afternoon', 'evening', 'greetings', 'howdy', 'hey there',
            'hi there', 'hello there'
        ]
        
        # Simple conversation starters
        simple_starters = [
            'i need help', 'can you help me', 'help me', 'i have a question',
            'i have a problem', 'can you assist', 'assist me'
        ]
        
        if any(greeting in message_lower for greeting in greetings):
            return "\n\nGREETING DETECTED: The user is starting a conversation with a greeting. Respond warmly and welcome them to the firm. Ask how you can help with their legal needs in a conversational way.\n"
        
        if any(starter in message_lower for starter in simple_starters):
            return "\n\nGENERAL HELP REQUEST: The user needs assistance but hasn't specified what. Respond warmly and ask what type of legal matter they need help with.\n"
        
        return ""

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance for use in endpoints
ollama_ai_service = OllamaAIService()
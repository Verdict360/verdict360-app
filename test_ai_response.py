#!/usr/bin/env python3
"""
Quick test script to verify AI responses are client-acquisition focused
"""

import asyncio
import sys
import os

# Add the api-python directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api-python'))

from app.services.demo_ai_service import demo_ai_service

async def test_ai_responses():
    """Test the AI responses for client acquisition focus"""
    
    test_messages = [
        "hi",
        "hello", 
        "I need legal help",
        "I'm having trouble with my employer",
        "Can you help with divorce",
        "I was arrested",
        "I need to buy a house"
    ]
    
    print("🧪 Testing AI Responses for Client Acquisition Focus\n")
    print("=" * 60)
    
    for message in test_messages:
        print(f"\n📨 USER: {message}")
        print("-" * 40)
        
        try:
            response = await demo_ai_service.generate_response(message)
            ai_content = response.get('content', 'No response')
            
            # Check if response contains conversion buttons
            has_schedule_btn = '[SCHEDULE_CONSULTATION]' in ai_content
            has_contact_btn = '[CONTACT_FIRM]' in ai_content
            
            # Check if response is client-acquisition focused
            acquisition_keywords = [
                'consultation', 'attorneys', 'legal team', 'schedule', 
                'contact', 'help', 'experienced', 'qualified', 'expert'
            ]
            
            is_client_focused = any(keyword.lower() in ai_content.lower() 
                                  for keyword in acquisition_keywords)
            
            # Check if response is defensive
            defensive_keywords = [
                "can't provide legal advice", "not licensed", "disclaimer",
                "should not be considered", "not a substitute"
            ]
            
            is_defensive = any(keyword.lower() in ai_content.lower() 
                             for keyword in defensive_keywords)
            
            print(f"🤖 AI: {ai_content[:200]}...")
            if len(ai_content) > 200:
                print("    [Response truncated]")
            
            print(f"\n✅ Analysis:")
            print(f"   • Has Schedule Button: {'✅ Yes' if has_schedule_btn else '❌ No'}")
            print(f"   • Has Contact Button: {'✅ Yes' if has_contact_btn else '❌ No'}")  
            print(f"   • Client-Acquisition Focused: {'✅ Yes' if is_client_focused else '❌ No'}")
            print(f"   • Defensive Response: {'❌ Yes' if is_defensive else '✅ No'}")
            
            # Overall assessment
            if has_schedule_btn and has_contact_btn and is_client_focused and not is_defensive:
                print(f"   • Overall: 🎯 PERFECT CLIENT ACQUISITION RESPONSE")
            elif is_client_focused and not is_defensive:
                print(f"   • Overall: ✅ GOOD CLIENT ACQUISITION RESPONSE")
            elif is_defensive:
                print(f"   • Overall: ❌ DEFENSIVE RESPONSE (NEEDS FIX)")
            else:
                print(f"   • Overall: ⚠️ NEUTRAL RESPONSE (COULD BE IMPROVED)")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_ai_responses())
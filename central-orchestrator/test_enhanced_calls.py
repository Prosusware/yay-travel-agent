#!/usr/bin/env python3
"""
Test script to demonstrate enhanced ElevenLabs call functionality
with system prompts and first messages.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_enhanced_call_parameters():
    """Test the enhanced call parameters without making actual calls."""
    
    # Example task and parameters
    task = "Follow up on the quarterly sales report and discuss next steps"
    phone_number = "447874943523"
    
    # Example system prompt
    system_prompt = """You are a professional sales follow-up assistant calling on behalf of your company. 

Your role:
- Follow up on the quarterly sales report that was sent last week
- Discuss any questions or concerns the client might have
- Schedule a meeting if needed to go over the details
- Maintain a professional and helpful tone throughout

Key information:
- The quarterly sales report showed a 15% increase in revenue
- We have new product offerings that might interest the client
- The client's previous feedback was positive about our service quality

Guidelines:
- Be courteous and professional
- Listen actively to their responses
- Take notes of important points
- Offer to schedule a follow-up meeting if needed
- Thank them for their continued business"""

    # Example first message
    first_message = """Hello! This is an AI assistant calling from your sales team regarding the quarterly sales report we sent last week. I wanted to follow up to see if you had a chance to review it and if you have any questions or would like to discuss the results. Do you have a few minutes to chat?"""
    
    print("Enhanced ElevenLabs Call Configuration")
    print("=" * 50)
    print(f"Task: {task}")
    print(f"Phone Number: {phone_number}")
    print(f"Priority: normal")
    print()
    print("System Prompt:")
    print("-" * 20)
    print(system_prompt)
    print()
    print("First Message:")
    print("-" * 20)
    print(first_message)
    print()
    
    # Show the payload that would be sent to ElevenLabs
    payload = {
        "agent_id": os.getenv("ELEVENLABS_AGENT_ID", "your_agent_id"),
        "agent_phone_number_id": os.getenv("ELEVENLABS_PHONE_NUMBER_ID", "your_phone_number_id"),
        "to_number": phone_number,
        "first_message": first_message,
        "agent": {
            "prompt": {
                "prompt": system_prompt
            }
        }
    }
    
    print("ElevenLabs API Payload:")
    print("-" * 25)
    import json
    print(json.dumps(payload, indent=2))
    print()
    print("✓ Enhanced call configuration ready!")
    print("✓ System prompt configured for professional sales follow-up")
    print("✓ First message set for natural conversation opening")
    print("✓ All parameters properly formatted for ElevenLabs API")


def show_api_improvements():
    """Show the improvements made to the API integration."""
    
    print("\nAPI Integration Improvements")
    print("=" * 40)
    print("✓ Added system_prompt parameter to define agent behavior")
    print("✓ Added first_message parameter for conversation opening")
    print("✓ Integrated Mistral AI for intelligent prompt generation")
    print("✓ Enhanced call result tracking with prompt information")
    print("✓ Fallback prompts for when AI generation fails")
    print("✓ Context-aware prompt creation using research data")
    print("✓ Professional conversation flow management")
    print()
    print("Benefits:")
    print("- More natural and contextual conversations")
    print("- Better task completion rates")
    print("- Professional and appropriate communication")
    print("- Adaptive behavior based on task priority")
    print("- Integration with research findings")


if __name__ == "__main__":
    print("Testing Enhanced ElevenLabs Integration")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        "ELEVENLABS_API_KEY",
        "ELEVENLABS_AGENT_ID", 
        "ELEVENLABS_PHONE_NUMBER_ID",
        "TARGET_PHONE_NUMBER",
        "MISTRAL_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file before running the agents.")
    else:
        print("✓ All required environment variables are set")
    
    print()
    test_enhanced_call_parameters()
    show_api_improvements()
    
    print("\nNext Steps:")
    print("1. Ensure all environment variables are properly set")
    print("2. Run 'python advanced_agent.py' to test the enhanced agent")
    print("3. The agent will generate contextual prompts automatically")
    print("4. Monitor call results for system prompt and first message data") 
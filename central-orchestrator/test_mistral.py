#!/usr/bin/env python3

import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI

# Load environment variables
load_dotenv()

def test_mistral_connection():
    """Test basic Mistral AI connection"""
    print("🧪 Testing Mistral AI Connection...")
    
    try:
        mistral_llm = ChatMistralAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
            temperature=0.1
        )
        
        # Simple test prompt
        test_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Respond with exactly: {'status': 'connected'}"),
            ("user", "Test connection")
        ])
        
        chain = test_prompt | mistral_llm
        response = chain.invoke({})
        
        print(f"✅ Mistral Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Mistral Connection Failed: {e}")
        return False


def test_json_generation():
    """Test JSON generation with Mistral"""
    print("\n🧪 Testing JSON Generation...")
    
    try:
        mistral_llm = ChatMistralAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
            temperature=0.1
        )
        
        json_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a JSON generator. 
            
IMPORTANT: You MUST respond with ONLY valid JSON in this exact format. Do not include any other text:
{
    "system_prompt": "A professional AI assistant prompt",
    "first_message": "Hello, this is a test message"
}"""),
            ("user", "Generate a test JSON response for task: Call client about project update")
        ])
        
        chain = json_prompt | mistral_llm
        response = chain.invoke({})
        
        print(f"Raw Response: {response.content}")
        
        # Test JSON parsing with robust extraction
        response_text = response.content.strip()
        
        try:
            result = json.loads(response_text)
            print("✅ Direct JSON parsing successful")
        except json.JSONDecodeError:
            print("⚠️ Direct parsing failed, trying extraction...")
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                print("✅ JSON extraction successful")
            else:
                raise Exception("No JSON found in response")
        
        print(f"✅ Parsed JSON: {json.dumps(result, indent=2)}")
        return True
        
    except Exception as e:
        print(f"❌ JSON Generation Test Failed: {e}")
        return False


def test_call_script_generation():
    """Test call script generation like in the agent"""
    print("\n🧪 Testing Call Script Generation...")
    
    try:
        mistral_llm = ChatMistralAI(
            api_key=os.getenv("MISTRAL_API_KEY"),
            model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
            temperature=0.1
        )
        
        call_preparation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert call script generator. Based on the task and context, create:
1. A system prompt for the AI agent making the call
2. An appropriate first message to start the conversation

The system prompt should:
- Define the agent's role and purpose
- Include relevant context and information
- Specify the desired outcome
- Set a professional and appropriate tone

The first message should:
- Be natural and conversational
- Introduce the purpose clearly
- Be engaging but professional
- Set the right tone for the conversation

IMPORTANT: You MUST respond with ONLY valid JSON in this exact format. Do not include any other text:
{
    "system_prompt": "Your detailed system prompt here",
    "first_message": "Your opening message here"
}"""),
            ("user", """Task: {task}
Context: {context}
Priority: {priority}

Generate the system prompt and first message for this call.""")
        ])
        
        chain = call_preparation_prompt | mistral_llm
        response = chain.invoke({
            "task": "Call client to discuss project timeline and deliverables",
            "context": "Research findings: Project is 80% complete, client has requested accelerated timeline",
            "priority": "high"
        })
        
        print(f"Raw Response: {response.content[:200]}...")
        
        # Test robust JSON parsing
        response_text = response.content.strip()
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
            else:
                raise Exception("No JSON found in response")
        
        print("✅ Call Script Generation Successful!")
        print(f"System Prompt: {result.get('system_prompt', '')[:100]}...")
        print(f"First Message: {result.get('first_message', '')}")
        return True
        
    except Exception as e:
        print(f"❌ Call Script Generation Failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Mistral AI Integration Test Suite")
    print("=" * 50)
    
    # Check environment variables
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ MISTRAL_API_KEY not found in environment")
        exit(1)
    
    print(f"🔑 API Key: {os.getenv('MISTRAL_API_KEY')[:10]}...")
    print(f"🤖 Model: {os.getenv('MISTRAL_MODEL', 'mistral-large-latest')}")
    
    # Run tests
    tests = [
        test_mistral_connection,
        test_json_generation,
        test_call_script_generation
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! Mistral integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the error messages above.") 
#!/usr/bin/env python3
"""
Test script for the WhatsApp LangGraph Agent API
"""
import requests
import time
from typing import Dict, Any

# API configuration
API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_models():
    """Test the models endpoint"""
    print("🔍 Testing models endpoint...")
    response = requests.get(f"{API_BASE_URL}/models")
    if response.status_code == 200:
        models = response.json()["models"]
        print(f"Available models: {len(models)}")
        for model in models:
            print(f"  - {model['name']}: {model['description']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    print()

def test_tools():
    """Test the tools endpoint"""
    print("🔍 Testing tools endpoint...")
    response = requests.get(f"{API_BASE_URL}/tools")
    if response.status_code == 200:
        tools = response.json()["tools"]
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    print()

def execute_task(task: str, model: str = "llama-3.3-70b-versatile", max_iterations: int = 10) -> Dict[str, Any]:
    """Execute a task using the agent"""
    print(f"🤖 Executing task: {task}")
    print(f"Using model: {model}")
    print(f"Max iterations: {max_iterations}")
    
    payload = {
        "task": task,
        "model": model,
        "max_iterations": max_iterations
    }
    
    response = requests.post(f"{API_BASE_URL}/execute_task", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status: {result['status']}")
        print(f"📝 Message: {result['message']}")
        print(f"🆔 Task ID: {result['task_id']}")
        
        # Print execution log
        print("\n📋 Execution Log:")
        for i, log_entry in enumerate(result['execution_log'], 1):
            timestamp = log_entry['timestamp']
            log_type = log_entry['type']
            message = log_entry.get('message', '')
            
            if log_type == 'task_start':
                print(f"  {i}. 🚀 [{timestamp}] Task Started: {message}")
            elif log_type == 'reasoning':
                iteration = log_entry.get('iteration', 0)
                print(f"  {i}. 🧠 [{timestamp}] Iteration {iteration}: {message}")
            elif log_type == 'tool_call':
                tool_name = log_entry.get('tool_name', '')
                args = log_entry.get('args', {})
                print(f"  {i}. 🔧 [{timestamp}] Tool Call: {tool_name} with args {args}")
            elif log_type == 'tool_result':
                tool_name = log_entry.get('tool_name', '')
                result_data = log_entry.get('result', '')
                print(f"  {i}. 📊 [{timestamp}] Tool Result: {tool_name} -> {result_data}")
            elif log_type == 'error':
                print(f"  {i}. ❌ [{timestamp}] Error: {message}")
            else:
                print(f"  {i}. 📄 [{timestamp}] {log_type}: {message}")
        
        return result
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return {}

def main():
    """Main test function"""
    print("🚀 WhatsApp LangGraph Agent API Test (Groq Edition)")
    print("=" * 60)
    
    # Test health
    test_health()
    
    # Test models
    test_models()
    
    # Test tools
    test_tools()
    
    # Example tasks to test with different models
    test_tasks = [
        {
            "task": "Search for contacts named John",
            "model": "llama-3.3-70b-versatile"
        },
        {
            "task": "Show me the last 5 messages from my most recent chat",
            "model": "llama-3.1-8b-instant"  # Test with faster model
        },
        {
            "task": "List all my WhatsApp chats",
            "model": "mixtral-8x7b-32768"  # Test with different model
        },
        # Add more test tasks as needed
    ]
    
    print("🧪 Testing example tasks with different Groq models...")
    for i, test_case in enumerate(test_tasks, 1):
        print(f"\n📋 Test {i}/{len(test_tasks)}")
        print("-" * 40)
        result = execute_task(
            task=test_case["task"],
            model=test_case["model"]
        )
        
        if result and result.get('status') == 'ok':
            print(f"✅ Task {i} completed successfully!")
        else:
            print(f"❌ Task {i} failed!")
        
        # Add a small delay between tasks
        time.sleep(2)
    
    print("\n🎉 Testing complete!")
    print("\n💡 Available Groq models:")
    print("  - llama-3.3-70b-versatile (most capable)")
    print("  - llama-3.1-70b-versatile (high performance)")
    print("  - llama-3.1-8b-instant (fast)")
    print("  - mixtral-8x7b-32768 (balanced)")
    print("  - gemma2-9b-it (efficient)")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Also ensure your GROQ_API_KEY is set in the .env file")
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}") 
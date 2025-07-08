#!/usr/bin/env python3
"""
Example script showing how to use the Groq-powered WhatsApp Agent
"""
import requests
import json
import time

# API configuration
API_BASE_URL = "http://localhost:8000"

def send_whatsapp_task(task: str, model: str = "llama-3.3-70b-versatile"):
    """Send a task to the WhatsApp agent"""
    
    print(f"🤖 Sending task to Groq model: {model}")
    print(f"📝 Task: {task}")
    print("-" * 50)
    
    payload = {
        "task": task,
        "model": model,
        "max_iterations": 8
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/execute_task", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Status: {result['status']}")
            print(f"📋 Message: {result['message']}")
            print(f"🆔 Task ID: {result['task_id']}")
            
            # Show key execution steps
            print("\n📊 Key Execution Steps:")
            for log_entry in result['execution_log']:
                if log_entry['type'] in ['reasoning', 'tool_call', 'error']:
                    log_type = log_entry['type']
                    timestamp = log_entry['timestamp']
                    
                    if log_type == 'reasoning':
                        iteration = log_entry.get('iteration', 0)
                        message = log_entry['message'][:100] + "..." if len(log_entry['message']) > 100 else log_entry['message']
                        print(f"  🧠 Iteration {iteration}: {message}")
                    elif log_type == 'tool_call':
                        tool_name = log_entry.get('tool_name', '')
                        print(f"  🔧 Called tool: {tool_name}")
                    elif log_type == 'error':
                        print(f"  ❌ Error: {log_entry['message']}")
            
            return result
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Main example function"""
    print("🚀 Groq-Powered WhatsApp Agent Examples")
    print("=" * 50)
    
    # Example tasks with different models
    examples = [
        {
            "task": "Search for contacts named John and show me their phone numbers",
            "model": "llama-3.1-8b-instant",
            "description": "Fast model for simple contact search"
        },
        {
            "task": "List my 5 most recent WhatsApp chats and show the last message from each",
            "model": "mixtral-8x7b-32768",
            "description": "Balanced model for moderate complexity"
        },
        {
            "task": "Find all messages from today that contain the word 'meeting' and summarize them",
            "model": "llama-3.3-70b-versatile",
            "description": "Most capable model for complex analysis"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📋 Example {i}: {example['description']}")
        print("=" * 60)
        
        result = send_whatsapp_task(
            task=example["task"],
            model=example["model"]
        )
        
        if result:
            print(f"✅ Example {i} completed!")
        else:
            print(f"❌ Example {i} failed!")
        
        # Wait between examples
        if i < len(examples):
            print("\n⏳ Waiting 3 seconds before next example...")
            time.sleep(3)
    
    print("\n🎉 All examples completed!")
    print("\n💡 Try your own tasks:")
    print("  - 'Send a message to Alice saying Hello!'")
    print("  - 'Download the latest image from my chat with Bob'")
    print("  - 'Find all group chats and list their names'")
    print("  - 'Check recent messages for anyone asking about deadlines'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user.")
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("\nMake sure:")
        print("1. The WhatsApp agent API is running on http://localhost:8000")
        print("2. Your GROQ_API_KEY is set in the .env file")
        print("3. The WhatsApp bridge is running") 
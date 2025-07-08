#!/usr/bin/env python3
"""
Example usage of the LangGraph agents for phone calls and research tasks.
"""

import os
from dotenv import load_dotenv
from agent import run_agent
from advanced_agent import run_enhanced_agent

# Load environment variables
load_dotenv()

def basic_agent_example():
    """Example using the basic agent."""
    print("="*60)
    print("BASIC AGENT EXAMPLE")
    print("="*60)
    
    task = "Call the client at +1234567890 to confirm their appointment for tomorrow"
    phone_number = "+1234567890"
    
    print(f"Task: {task}")
    print(f"Phone Number: {phone_number}")
    print("\nRunning basic agent...\n")
    
    result = run_agent(task, phone_number)
    
    print("Results:")
    print(f"- Task: {result['current_task']}")
    print(f"- Completed: {result['task_complete']}")
    print(f"- Status: {result['completion_status']}")
    print(f"- Steps: {result['step_count']}")
    print(f"- Key Facts: {len(result.get('key_facts', {}))}")
    print(f"- Phone Calls: {len(result.get('phone_call_results', []))}")
    print(f"- Research Results: {len(result.get('tavily_results', []))}")


def advanced_agent_example():
    """Example using the advanced agent."""
    print("\n" + "="*60)
    print("ADVANCED AGENT EXAMPLE")
    print("="*60)
    
    task = "Research the latest trends in AI customer service and call our main client to discuss implementation options"
    phone_number = "+1987654321"
    
    print(f"Task: {task}")
    print(f"Phone Number: {phone_number}")
    print("\nRunning advanced agent...\n")
    
    result = run_enhanced_agent(task, phone_number, max_steps=8)
    
    print("Results:")
    print(f"- Task: {result['current_task']}")
    print(f"- Status: {result['task_status']}")
    print(f"- Completion Score: {result['completion_score']:.2f}")
    print(f"- Steps Executed: {result['step_count']}")
    
    print("\nTask Requirements:")
    for req in result.get('task_requirements', []):
        status = "✓" if req['completed'] else "✗"
        print(f"  {status} {req['name']}: {req['description']}")
    
    print(f"\nDetailed Metrics:")
    print(f"- Key Facts Collected: {len(result.get('key_facts', {}))}")
    print(f"- Research Results: {len(result.get('tavily_results', []))}")
    print(f"- Phone Calls Made: {len(result.get('phone_call_results', []))}")
    
    if result.get('execution_log'):
        print("\nExecution Log:")
        for log_entry in result['execution_log']:
            print(f"  Step {log_entry['step']}: {log_entry['action']} (Score: {log_entry.get('completion_score', 0):.2f})")


def custom_task_example():
    """Example with a custom user-defined task."""
    print("\n" + "="*60)
    print("CUSTOM TASK EXAMPLE")
    print("="*60)
    
    # You can customize this task
    task = input("Enter your custom task (or press Enter for default): ").strip()
    if not task:
        task = "Research information about LangChain agents and call the tech lead to discuss integration"
    
    phone_number = input("Enter phone number (or press Enter for default): ").strip()
    if not phone_number:
        phone_number = "+1555123456"
    
    print(f"\nExecuting custom task: {task}")
    print(f"Phone Number: {phone_number}")
    
    # Choose agent type
    agent_choice = input("Use (b)asic or (a)dvanced agent? [a]: ").lower()
    
    if agent_choice == 'b':
        print("\nUsing basic agent...")
        result = run_agent(task, phone_number)
        print(f"Completed: {result['task_complete']}")
        print(f"Status: {result['completion_status']}")
    else:
        print("\nUsing advanced agent...")
        result = run_enhanced_agent(task, phone_number, max_steps=10)
        print(f"Status: {result['task_status']}")
        print(f"Completion Score: {result['completion_score']:.2f}")
        
        print("\nRequirements Summary:")
        for req in result.get('task_requirements', []):
            status = "✓" if req['completed'] else "✗"
            print(f"  {status} {req['name']}")


def main():
    """Main function to run examples."""
    print("LangGraph Agent Examples")
    print("Make sure you have set up your environment variables:")
    print("- TAVILY_API_KEY")
    print("- ELEVENLABS_VOICE_ID")
    print("- TWILIO_OUTBOUND_ENDPOINT")
    print("- API_TOKEN")
    print("- TARGET_PHONE_NUMBER")
    print()
    
    # Check if required environment variables are set
    required_vars = ["TAVILY_API_KEY", "TWILIO_OUTBOUND_ENDPOINT"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"WARNING: Missing environment variables: {', '.join(missing_vars)}")
        print("The agents may not work properly without these variables.")
        print()
    
    try:
        # Run basic agent example
        basic_agent_example()
        
        # Run advanced agent example
        advanced_agent_example()
        
        # Run custom task example
        custom_task_example()
        
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
    except Exception as e:
        print(f"\nError during execution: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main() 